from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Core Pages
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("reviews/", views.reviews, name="reviews"),

    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page='home'), name="logout"),
    path("register/", views.register, name="register"),
    path("forgot-password/", views.forgot_password, name="forgot"),

    # Products
    path("products/", views.product_list, name="product_list"),
    path("shop/", views.product_list, name="shop"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_view, name="category_view"),

    # Cart
    # urls.py
    path("cart/", views.cart_view, name="cart"),  
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),

    # Wishlist
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<int:product_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),

    # Checkout & Orders
    path("checkout/", views.checkout, name="checkout"),
    path("order/<int:order_id>/summary/", views.order_summary, name="order_summary"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),

    # Payments
    path("payment/<int:order_id>/", views.payment, name="payment"),

    # Reviews
    path("review/add/<int:product_id>/", views.add_review, name="add_review"),

    # User Dashboard & Profile
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),

    # New User Pages
    path("settings/", views.settings_view, name="settings_view"),
    path("track-shipment/", views.track_shipment, name="track_shipment"),

    # Search
    path("search/", views.search, name="search"),

    # Notifications
    path("notifications/", views.notifications, name="notification"),

     path("place_order/", views.place_order, name="place_order"),

]
