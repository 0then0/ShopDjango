from django.test import Client, TestCase
from django.urls import reverse

from store.models import Category, Product


class StoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="Cat1", slug="cat1")
        for i in range(3):
            Product.objects.create(
                name=f"Pr{i}",
                description="desc",
                price=5,
                stock=2,
                category=self.cat,
            )

    def test_product_list_status_and_context(self):
        resp = self.client.get(reverse("store:product_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("page_obj", resp.context)
        self.assertEqual(len(resp.context["page_obj"]), 3)

    def test_product_detail(self):
        prod = Product.objects.first()
        resp = self.client.get(reverse("store:product_detail", args=[prod.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, prod.name)
