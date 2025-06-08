from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Order


class SignUpForm(UserCreationForm):
    """
    Override the default UserCreationForm,
    add the email field. The username, password1, password2 fields are set automatically.
    """

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter email"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adding Bootstrap CSS classes to the form fields:
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field.widget.attrs.get("class") is None:
                field.widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        """
        Check that the entered email is not registered yet.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email address is already in use.")
        return email


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "address", "city", "postal_code", "phone"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        # Check cart items against stock
        user = self.initial.get("user") or getattr(self.instance, "user", None)
        if user:
            from .models import CartItem

            items = CartItem.objects.filter(cart__user=user).select_related("product")
            for item in items:
                if item.quantity > item.product.stock:
                    raise forms.ValidationError(
                        f"Not enough stock for product '{item.product.name}'. "
                        f"Requested: {item.quantity}, Available: {item.product.stock}."
                    )
        return cleaned
