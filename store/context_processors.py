from django.db import models

from .models import Cart


def cart_item_count(request):
    """
    Returns the total number of items in the cart:
    - if the user is logged in - summarize the quantity in the CartItem model,
    - otherwise - summarize all values of session[‘cart’].
    """
    total = 0

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        total = cart.items.aggregate(total_qty=models.Sum("quantity"))["total_qty"] or 0
    else:
        session_cart = request.session.get("cart", {})
        total = sum(session_cart.values())

    return {"cart_item_count": total}
