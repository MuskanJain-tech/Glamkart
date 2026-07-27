from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Order, Review


class UserRegisterForm(UserCreationForm):
    """Form for new user signup"""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserLoginForm(AuthenticationForm):
    """Custom login form with Bootstrap classes"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Username"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Password"
    }))


class CheckoutForm(forms.ModelForm):
    """Form for order checkout"""
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": 3,
        "placeholder": "Enter your shipping address"
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your phone number"
    }))

    class Meta:
        model = Order
        fields = ["shipping_address", "phone_number"]


class ReviewForm(forms.ModelForm):
    """Form to add a product review"""
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect
    )
    comment = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": 2,
        "placeholder": "Write your review..."
    }))

    class Meta:
        model = Review
        fields = ["rating", "comment"]


class SearchForm(forms.Form):
    """Search bar form"""
    query = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Search products..."
    }))
