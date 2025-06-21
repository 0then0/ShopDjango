from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from store.models import Cart, CartItem, Category, Order, OrderItem, Product

from .permissions import IsStaffOrOwner
from .serializers import (
    CartItemSerializer,
    CategorySerializer,
    OrderSerializer,
    ProductSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filterset_fields = ["category", "price", "stock"]
    search_fields = ["name", "description"]

    pagination_class = None


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CartItem.objects.filter(cart__user=self.request.user)
        return []

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def guest_add(self, request):
        # handle guest session cart separately or error
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsStaffOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("store.change_order"):
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        cart_items = CartItem.objects.filter(cart__user=user)

        total = sum(item.product.price * item.quantity for item in cart_items)

        order = serializer.save(user=user, total_price=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_order=item.product.price,
            )

        cart_items.delete()

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
