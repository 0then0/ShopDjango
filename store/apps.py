from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from django.db.models.signals import post_migrate

        from .models import Category, Order, Product

        def create_groups(sender, **kwargs):
            # Managers (product and category management)
            managers, _ = Group.objects.get_or_create(name="Managers")
            # rights to CRUD models Product and Category
            ct_prod = ContentType.objects.get_for_model(Product)
            ct_cat = ContentType.objects.get_for_model(Category)
            perms = Permission.objects.filter(
                content_type__in=[ct_prod, ct_cat],
                codename__in=[
                    "add_product",
                    "change_product",
                    "delete_product",
                    "add_category",
                    "change_category",
                    "delete_category",
                ],
            )
            managers.permissions.set(perms)

            # Employees (order status management)
            staff, _ = Group.objects.get_or_create(name="Staff")
            ct_order = ContentType.objects.get_for_model(Order)
            # allow changing the status field in the Order
            perm_change_order = Permission.objects.get(
                content_type=ct_order, codename="change_order"
            )
            staff.permissions.set([perm_change_order])

        post_migrate.connect(create_groups, sender=self)
