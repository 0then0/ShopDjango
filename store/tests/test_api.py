from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Category, Product


class StoreApiTest(APITestCase):
    def setUp(self):
        managers, _ = Group.objects.get_or_create(name="Managers")
        staff, _ = Group.objects.get_or_create(name="Staff")
        self.manager = User.objects.create_user("mgr", "mgr@example.com", "pass")
        self.manager.groups.add(managers)
        self.staff = User.objects.create_user("stf", "stf@example.com", "pass")
        self.staff.groups.add(staff)
        self.user = User.objects.create_user("joe", "joe@example.com", "pass")

        self.cat = Category.objects.create(name="C", slug="c")
        self.prod = Product.objects.create(
            name="P", description="d", price=1, stock=5, category=self.cat
        )

    def test_list_products_public(self):
        url = reverse("product-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 1)

    def test_manager_can_create_product(self):
        self.client.force_authenticate(self.manager)
        url = reverse("product-list")
        data = {
            "name": "X",
            "description": "d",
            "price": 2,
            "stock": 3,
            "category_id": self.cat.pk,
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_cannot_create_product(self):
        self.client.force_authenticate(self.staff)
        url = reverse("product-list")
        data = {
            "name": "X",
            "description": "d",
            "price": 2,
            "stock": 3,
            "category_id": self.cat.pk,
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cart_and_order(self):
        self.client.force_authenticate(self.user)
        url_cart = reverse("cart-list")
        resp = self.client.post(
            url_cart, {"product_id": self.prod.pk, "quantity": 2}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        url_order = reverse("order-list")
        order_data = {
            "first_name": "J",
            "last_name": "D",
            "address": "A",
            "city": "C",
            "postal_code": "123",
            "phone": "000",
        }
        resp2 = self.client.post(url_order, order_data, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        order_id = resp2.json()["id"]
        self.client.force_authenticate(self.staff)
        url_order_detail = reverse("order-detail", args=[order_id])
        resp3 = self.client.patch(
            url_order_detail, {"status": "PROCESSING"}, format="json"
        )
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
