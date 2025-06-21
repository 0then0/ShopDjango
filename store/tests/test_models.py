from django.test import TestCase

from store.models import Category, Product


class ProductModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="TestCat", slug="testcat")
        self.prod = Product.objects.create(
            name="TestProd",
            description="Desc",
            price=9.99,
            stock=10,
            category=self.cat,
        )

    def test_str_methods(self):
        self.assertEqual(str(self.cat), "TestCat")
        self.assertEqual(str(self.prod), "TestProd")

    def test_product_stock_validation(self):
        # An attempt to set a negative stock should throw a ValidationError
        self.prod.stock = -1
        with self.assertRaises(Exception):
            self.prod.full_clean()
