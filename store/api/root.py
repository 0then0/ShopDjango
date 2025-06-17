from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            # existing ViewSets
            "categories": reverse("category-list", request=request, format=format),
            "products": reverse("product-list", request=request, format=format),
            "cart": reverse("cart-list", request=request, format=format),
            "orders": reverse("order-list", request=request, format=format),
            # DRF session auth
            "login": reverse("rest_framework:login", request=request, format=format),
            "logout": reverse("rest_framework:logout", request=request, format=format),
            # JWT endpoints (simplejwt)
            "token_obtain_pair": reverse(
                "token_obtain_pair", request=request, format=format
            ),
            "token_refresh": reverse("token_refresh", request=request, format=format),
        }
    )
