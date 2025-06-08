from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path(
        "cart/ajax/update-item/",
        views.ajax_update_cart_item,
        name="ajax_update_cart_item",
    ),
    # path("cart/update/", views.update_cart, name="update_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path(
        "order/confirmation/<int:order_id>/",
        views.order_confirmation,
        name="order_confirmation",
    ),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
