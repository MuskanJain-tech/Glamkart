from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category, Product, Cart, Wishlist, Order, Review


class GlamkartModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            category=self.category,
            name="Smartphone",
            price=500,
            stock=10
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), "Electronics")

    def test_product_str(self):
        self.assertEqual(str(self.product), "Smartphone")

    def test_wishlist(self):
        Wishlist.objects.create(user=self.user, product=self.product)
        self.assertEqual(Wishlist.objects.count(), 1)

    def test_cart_item_addition(self):
        cart = Cart.objects.create(user=self.user)
        cart.items.create(product=self.product, quantity=2)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)


class GlamkartViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.category = Category.objects.create(name="Clothing")
        self.product = Product.objects.create(
            category=self.category,
            name="T-Shirt",
            price=20,
            stock=50
        )

    def test_home_page_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_product_list_view(self):
        response = self.client.get(reverse("product_list"))
        self.assertContains(response, "T-Shirt")

    def test_product_detail_view(self):
        response = self.client.get(reverse("product_detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T-Shirt")

    def test_cart_requires_login(self):
        response = self.client.get(reverse("cart_view"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_add_to_cart_authenticated(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to cart
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)

    def test_add_to_wishlist(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("add_to_wishlist", args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Wishlist.objects.count(), 1)

    def test_checkout_flow(self):
        self.client.login(username="testuser", password="12345")
        # Add product to cart first
        self.client.get(reverse("add_to_cart", args=[self.product.id]))
        response = self.client.post(reverse("checkout"), {"shipping_address": "123 Street"})
        self.assertEqual(response.status_code, 302)                          # Redirect to payment
        self.assertEqual(Order.objects.count(), 1)

    def test_add_review(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(reverse("add_review", args=[self.product.id]), {
            "rating": 5,
            "comment": "Great product!"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
