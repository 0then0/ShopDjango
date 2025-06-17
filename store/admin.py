from django import forms
from django.contrib import admin
from django.forms import HiddenInput
from django.utils.html import format_html

from .models import Cart, CartItem, Category, Order, OrderItem, Product


def is_staff_user(request):
    return request.user.groups.filter(name="Staff").exists()


class HideForStaffMixin:
    def has_module_permission(self, request):
        if is_staff_user(request):
            return False
        return super().has_module_permission(request)


# Categories
@admin.register(Category)
class CategoryAdmin(HideForStaffMixin, admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}  # авто-slug
    list_per_page = 20


# Products
@admin.register(Product)
class ProductAdmin(HideForStaffMixin, admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "image_preview")
    list_filter = ("category", "stock")
    search_fields = ("name", "description")
    list_editable = ("price", "stock")
    readonly_fields = ("image_preview",)
    list_per_page = 20

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:60px; max-height:60px; border-radius:4px;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Preview"


# Cart and its elements
@admin.register(Cart)
class CartAdmin(HideForStaffMixin, admin.ModelAdmin):
    list_display = ("user", "created_at")
    readonly_fields = ("created_at",)


@admin.register(CartItem)
class CartItemAdmin(HideForStaffMixin, admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
    list_select_related = ("product", "cart")
    list_per_page = 20


# Inline editor for order items
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ("product", "quantity", "price_at_order")
        widgets = {
            "price_at_order": HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "price_at_order" in self.fields:
            self.fields["price_at_order"].required = False

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        if product:
            cleaned["price_at_order"] = product.price
        return cleaned


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemForm
    extra = 1

    def has_add_permission(self, request, obj=None):
        return (
            obj and obj.status == "PENDING" and super().has_add_permission(request, obj)
        )

    def has_change_permission(self, request, obj=None):
        return (
            obj
            and obj.status == "PENDING"
            and super().has_change_permission(request, obj)
        )

    def has_delete_permission(self, request, obj=None):
        return (
            obj
            and obj.status == "PENDING"
            and super().has_delete_permission(request, obj)
        )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != "PENDING":
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


# Orders
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "ordered_at", "status", "total_price")
    list_filter = ("status", "ordered_at")
    search_fields = (
        "user__username",
        "first_name",
        "last_name",
        "address",
        "city",
        "postal_code",
    )
    readonly_fields = (
        "user",
        "first_name",
        "last_name",
        "address",
        "city",
        "postal_code",
        "phone",
        "ordered_at",
        "total_price",
    )
    fields = (
        "user",
        "first_name",
        "last_name",
        "address",
        "city",
        "postal_code",
        "phone",
        "status",
    )
    inlines = [OrderItemInline]
    list_per_page = 20
    actions = ["mark_completed", "mark_cancelled"]

    def mark_completed(self, request, queryset):
        updated = queryset.update(status="COMPLETED")
        self.message_user(request, f"{updated} order(s) marked as completed.")

    mark_completed.short_description = "Mark selected orders as Completed"

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="CANCELLED")
        self.message_user(request, f"{updated} order(s) marked as cancelled.")

    mark_cancelled.short_description = "Mark selected orders as Cancelled"

    def get_readonly_fields(self, request, obj=None):
        if is_staff_user(request):
            return list(self.readonly_fields)
        return super().get_readonly_fields(request, obj)

    def get_fields(self, request, obj=None):
        if is_staff_user(request):
            return self.fields
        return super().get_fields(request, obj)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("store.change_order")
