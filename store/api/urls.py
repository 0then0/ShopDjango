from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .root import api_root
from .views import CartViewSet, CategoryViewSet, OrderViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("cart", CartViewSet, basename="cart")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", api_root, name="api-root"),
    path("", include(router.urls)),
    # DRF session login/logout
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
    # JWT endpoints
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
