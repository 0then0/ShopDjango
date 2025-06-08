import json
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .context_processors import cart_item_count as get_cart_count
from .forms import OrderForm, SignUpForm
from .models import Cart, CartItem, Category, Order, OrderItem, Product


def product_list(request):
    """
    List of products with filtering: search, category, price, in stock, pagination.
    """
    qs = Product.objects.select_related("category").all()
    categories = Category.objects.all()

    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    in_stock = request.GET.get("in_stock")  # 'on' если чекнут

    if q:
        qs = qs.filter(models.Q(name__icontains=q) | models.Q(description__icontains=q))

    if category_id.isdigit():
        qs = qs.filter(category_id=category_id)

    if min_price:
        try:
            qs = qs.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if in_stock == "on":
        qs = qs.filter(stock__gt=0)

    qs = qs.order_by("name")
    paginator = Paginator(qs, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    breadcrumbs = [
        {"title": "Home", "url": reverse("store:product_list")},
    ]

    return render(
        request,
        "store/product_list.html",
        {
            "page_obj": page_obj,
            "breadcrumbs": breadcrumbs,
            "categories": categories,
            "search_query": q,
            "selected_category": category_id,
            "min_price": min_price,
            "max_price": max_price,
            "in_stock": in_stock,
        },
    )


def product_detail(request, pk):
    """
    Display details for a single product identified by its pk.
    """
    product = get_object_or_404(Product, pk=pk)
    in_cart = False
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(
            cart__user=request.user, product=product
        ).exists()
    else:
        session_cart = request.session.get("cart", {})
        in_cart = str(product.pk) in session_cart

    breadcrumbs = [
        {"title": "Home", "url": reverse("store:product_list")},
        {"title": product.name, "url": ""},
    ]
    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "in_cart": in_cart,
            "breadcrumbs": breadcrumbs,
        },
    )


def signup_view(request):
    """
    Displays the registration form and handles the POST request.
    If the data is valid, it creates a new user and logs him in immediately.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            merge_session_cart_to_db(request, user)
            messages.success(
                request, f"Welcome, {username}! Your account has been created."
            )
            return redirect("store:product_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, "store/signup.html", {"form": form})


def login_view(request):
    """
    Displays the standard authorization form.
    On successful login, it redirects to PRODUCT_LIST.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                merge_session_cart_to_db(request, user)
                messages.success(request, f"You are now logged in as {username}.")
                return redirect("store:product_list")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, "store/login.html", {"form": form})


def logout_view(request):
    """
    Logs out the current user and redirects to the product list.
    """
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("store:product_list")


def cart_view(request):
    """
    Shows the cart:
      - for logged-in users — from the database,
      - for anonymous users — from request.session['cart'].
    """
    items = []
    total = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related("product").all()
        for item in items:
            item.subtotal = item.product.price * item.quantity
        total = sum(item.subtotal for item in items)
    else:
        session_cart = request.session.get("cart", {})
        product_ids = [int(pid) for pid in session_cart.keys()]
        products = Product.objects.filter(pk__in=product_ids)
        for prod in products:
            qty = session_cart.get(str(prod.pk), 0)
            fake = SimpleNamespace(
                product=prod, quantity=qty, subtotal=prod.price * qty, pk=prod.pk
            )
            items.append(fake)
            total += fake.subtotal

    breadcrumbs = [
        {"title": "Home", "url": reverse("store:product_list")},
        {"title": "Cart", "url": ""},
    ]
    return render(
        request,
        "store/cart.html",
        {
            "items": items,
            "total": total,
            "breadcrumbs": breadcrumbs,
        },
    )


@require_POST
def add_to_cart(request, pk):
    """
    Adds an item to the current user's cart.
    If the cart doesn't exist yet - creates it.
    If the product is already in the cart, increases the quantity by 1.
    If AJAX request, return JSON, otherwise redirect to cart.
    """
    product = get_object_or_404(Product, pk=pk)
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            item.save()
    else:
        # for anonymous users: store the dictionary {product_id: quantity} in the session
        cart = request.session.get("cart", {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session["cart"] = cart

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "cart_url": reverse("store:cart_view"),
            }
        )

    cart_count = get_cart_count(request)["cart_item_count"]
    return JsonResponse(
        {
            "success": True,
            "cart_url": reverse("store:cart_view"),
            "cart_item_count": cart_count,
        }
    )


def merge_session_cart_to_db(request, user):
    """
    On login/registration: transfers data from request.session['cart']
    to Cart/CartItem tables and clears the session.
    """
    session_cart = request.session.get("cart", {})
    if not session_cart:
        return

    cart, _ = Cart.objects.get_or_create(user=user)
    for pid_str, qty in session_cart.items():
        try:
            prod = Product.objects.get(pk=int(pid_str))
        except Product.DoesNotExist:
            continue
        item, created = CartItem.objects.get_or_create(cart=cart, product=prod)
        if created:
            item.quantity = qty
        else:
            item.quantity += qty
        item.quantity = min(item.quantity, prod.stock)
        item.save()
    del request.session["cart"]


def remove_from_cart(request, pk):
    """
    If the user is logged in - delete CartItem with this pk.
    If anonymous - delete the session['cart'][str(pk)] record.
    For anonymous user pk is product_id, for auth - CartItem.pk.
    """
    if request.user.is_authenticated:
        CartItem.objects.filter(pk=pk, cart__user=request.user).delete()
    else:
        session_cart = request.session.get("cart", {})
        session_cart.pop(str(pk), None)
        request.session["cart"] = session_cart
    return redirect("store:cart_view")


@require_POST
def ajax_update_cart_item(request):
    """
    AJAX: {'item_id': <int>, 'quantity': <int>}
    For authorized users, edit the CartItem in the database,
    for anonymous users, request.session['cart'].
    """
    try:
        data = json.loads(request.body)
        item_id = str(int(data.get("item_id")))
        quantity = int(data.get("quantity"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid data")

    if quantity < 1:
        return JsonResponse({"success": False, "error": "Quantity must be at least 1."})

    if request.user.is_authenticated:
        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            item = CartItem.objects.get(pk=int(item_id), cart=cart)
        except CartItem.DoesNotExist:
            return HttpResponseBadRequest("No such item")
        if quantity > item.product.stock:
            return JsonResponse(
                {"success": False, "error": f"Max stock is {item.product.stock}"}
            )
        item.quantity = quantity
        item.full_clean()
        item.save()
        item_subtotal = item.product.price * item.quantity
        items = cart.items.select_related("product").all()
        cart_total = sum(i.product.price * i.quantity for i in items)

    else:
        session_cart = request.session.get("cart", {})
        if item_id not in session_cart:
            return HttpResponseBadRequest("No such item in session cart")
        try:
            prod = Product.objects.get(pk=int(item_id))
        except Product.DoesNotExist:
            return HttpResponseBadRequest("Product does not exist")
        if quantity > prod.stock:
            return JsonResponse(
                {"success": False, "error": f"Max stock is {prod.stock}"}
            )
        session_cart[item_id] = quantity
        request.session["cart"] = session_cart
        item_subtotal = prod.price * quantity
        cart_total = 0
        for pid_str, qty in session_cart.items():
            try:
                p = Product.objects.get(pk=int(pid_str))
            except Product.DoesNotExist:
                continue
            cart_total += p.price * qty

    return JsonResponse(
        {
            "success": True,
            "item_subtotal": f"{item_subtotal:.2f}",
            "cart_total": f"{cart_total:.2f}",
            "cart_item_count": get_cart_count(request)["cart_item_count"],
        }
    )


def clear_cart(request):
    """
    Clears the cart:
      - for logged-in users - deletes CartItem from the database,
      - for anonymous users - deletes data from the session.
    """
    if request.user.is_authenticated:
        CartItem.objects.filter(cart__user=request.user).delete()
    else:
        if "cart" in request.session:
            del request.session["cart"]
    return redirect("store:cart_view")


@login_required
def checkout_view(request):
    """
    Shows the order form.
    If the cart is empty, redirects to the catalog.
    POST: validates data, creates Order and OrderItem, lists items from stock, clears cart.
    """
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product").all()
    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("store:product_list")

    total = 0
    for item in items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    profile = request.user.profile
    initial_data = {
        "first_name": profile.user.first_name or "",
        "last_name": profile.user.last_name or "",
        "address": profile.address or "",
        "city": profile.city or "",
        "postal_code": profile.postal_code or "",
        "phone": profile.phone or "",
    }

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total
            order.ordered_at = timezone.now()
            order.status = "PENDING"
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_order=item.product.price,
                )
                product = item.product
                product.stock -= item.quantity
                product.save()

            items.delete()

            messages.success(request, f"Order #{order.id} created successfully!")
            return redirect("store:order_confirmation", order_id=order.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrderForm(initial=initial_data)

    breadcrumbs = [
        {"title": "Home", "url": reverse("store:product_list")},
        {"title": "Cart", "url": reverse("store:cart_view")},
        {"title": "Checkout", "url": ""},
    ]
    return render(
        request,
        "store/checkout.html",
        {
            "form": form,
            "items": items,
            "total": total,
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
def order_confirmation(request, order_id):
    """
    Confirmation page after a successful checkout.
    Shows the details of an order that has just been created.
    """
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order_items = order.order_items.select_related("product").all()

    total = 0
    for item in order_items:
        item.subtotal = item.price_at_order * item.quantity
        total += item.subtotal

    return render(
        request,
        "store/order_confirmation.html",
        {"order": order, "order_items": order_items},
    )


@login_required
def order_history(request):
    """
    Displays a list of all orders made by the current user,
    from newest to oldest.
    """
    order_list = Order.objects.filter(user=request.user).order_by("-ordered_at")
    paginator = Paginator(order_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    breadcrumbs = [
        {"title": "Home", "url": reverse("store:product_list")},
        {"title": "My Orders", "url": ""},
    ]
    return render(
        request,
        "store/order_history.html",
        {
            "page_obj": page_obj,
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
def order_detail(request, order_id):
    """
    Shows the details of a single order: delivery address, status, and products.
    """
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    items = order.order_items.select_related("product").all()

    for item in items:
        item.subtotal = item.price_at_order * item.quantity

    breadcrumbs = [
        {"title": "Home", "url": reverse("store:product_list")},
        {"title": "My Orders", "url": reverse("store:order_history")},
        {"title": f"Order #{order.id}", "url": ""},
    ]
    return render(
        request,
        "store/order_detail.html",
        {
            "order": order,
            "order_items": items,
            "breadcrumbs": breadcrumbs,
        },
    )
