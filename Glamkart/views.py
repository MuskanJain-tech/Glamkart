from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from .models import Product, Category, Cart, CartItem, Order, Wishlist, Review, Payment, Profile, Gallery
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, authenticate
from .models import Contact


# -------------------------------
# Core Pages

def home(request):
    featured_products = Product.objects.all().order_by("-created_at")[:6]
    categories = Category.objects.all()
    gallery_images = Gallery.objects.all()  # ✅ Keep name same as template

    return render(request, "Glamkart/home.html", {
        "featured_products": featured_products,
        "categories": categories,
        "gallery_images": gallery_images,  # ✅ Fixed variable name
    })



def about(request):
    return render(request, "Glamkart/about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")   # same page reload

    return render(request, "Glamkart/contact.html")


def faq(request):
    return render(request, "Glamkart/faq.html")


def reviews(request):
    return render(request, "Glamkart/reviews.html")


# -------------------------------
# Product Views
# -------------------------------
def product_list(request):
    products = Product.objects.all()
    query = request.GET.get("q")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, "Glamkart/product_list.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"] or 0
    return render(request, "Glamkart/product_detail.html", {
        "product": product,
        "reviews": reviews,
        "avg_rating": round(avg_rating, 1),
    })


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, "Glamkart/category.html", {
        "category": category,
        "products": products,
    })


# -------------------------------
# Cart
# -------------------------------
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "Glamkart/cart.html", {"cart": cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to cart!")
    return redirect("cart")



@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect("cart_view")


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
    return redirect("cart_view")


# -------------------------------
# Wishlist
# -------------------------------
@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, "Glamkart/wishlist.html", {"wishlist": wishlist})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.name} added to wishlist!")
    return redirect("wishlist_view")


@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product__id=product_id).delete()
    messages.info(request, "Removed from wishlist.")
    return redirect("wishlist_view")


# -------------------------------
# Checkout & Orders
# -------------------------------
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == "POST":
        shipping_address = request.POST.get("shipping_address")
        total = sum(item.total_price() for item in CartItem.objects.filter(cart=cart))
        order = Order.objects.create(
            user=request.user,
            cart=cart,
            total_amount=total,
            shipping_address=shipping_address
        )
        messages.success(request, "Order placed successfully! Proceed to payment.")
        return redirect("payment", order_id=order.id)
    return render(request, "Glamkart/checkout.html", {"cart": cart})


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "Glamkart/order_summary.html", {"order": order})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "Glamkart/order_success.html", {"order": order})


# -------------------------------
# Payments
# -------------------------------
@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == "POST":
        method = request.POST.get("method")
        Payment.objects.create(
            order=order,
            method=method,
            amount=order.total_amount,
            success=True
        )
        order.status = "Processing"
        order.save()
        return redirect("order_success", order_id=order.id)
    return render(request, "Glamkart/payment.html", {"order": order})


# -------------------------------
# Reviews
# -------------------------------
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "")
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Review submitted!")
    return redirect("product_detail", slug=product.slug)


# -------------------------------
# Dashboard & Profile
# -------------------------------
@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    wishlist = Wishlist.objects.filter(user=request.user)

    aggregate_total = sum(order.total_amount for order in orders)
    active_shipments_count = orders.filter(status="Processing").count()
    recommended_products = Product.objects.all()[:5]

    context = {
        "orders": orders,
        "wishlist": wishlist,
        "aggregate_total": aggregate_total,
        "active_shipments_count": active_shipments_count,
        "recommended_products": recommended_products,
    }
    return render(request, "Glamkart/dashboard.html", context)


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "Glamkart/profile.html", {"user": request.user, "profile": profile})


# -------------------------------
# Authentication
# -------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        messages.error(request, "Invalid username or password")
    return render(request, "Glamkart/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        photo = request.FILES.get('photo')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        Profile.objects.create(user=user, photo=photo)
        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, "Glamkart/register.html")


# -------------------------------
# Search
# -------------------------------
def search(request):
    query = request.GET.get("q", "")
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, "Glamkart/search_results.html", {
        "products": products,
        "query": query
    })


# -------------------------------
# Forgot Password
# -------------------------------
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            reset_link = request.build_absolute_uri("/reset-password/")
            send_mail(
                "Password Reset Request",
                f"Hello {user.username}, click the link to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
            messages.success(request, "Check your inbox for the reset link!")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
    return render(request, "Glamkart/forgot_password.html")


# -------------------------------
# Track Shipment
# -------------------------------
@login_required
def track_shipment(request):
    orders = Order.objects.filter(user=request.user).exclude(status="Delivered")
    return render(request, "Glamkart/track_shipment.html", {"orders": orders})


# -------------------------------
# Settings
# -------------------------------
@login_required
def settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        photo = request.FILES.get("photo")

        if username:
            request.user.username = username
        if email:
            request.user.email = email
        request.user.save()

        if photo:
            profile.photo = photo
        profile.save()

        messages.success(request, "Settings updated successfully!")
        return redirect("settings_view")

    return render(request, "Glamkart/settings.html", {"user": request.user, "profile": profile})


# -------------------------------
# Notifications
# -------------------------------
@login_required
def notifications(request):
    notifications = []  # Future: use Notification model
    return render(request, "Glamkart/notifications.html", {"notifications": notifications})

@login_required
def place_order(request):
    cart = get_object_or_404(Cart, user=request.user)

    # If cart is empty
    if not CartItem.objects.filter(cart=cart).exists():
        messages.error(request, "Your cart is empty. Add items before placing an order.")
        return redirect("cart")

    if request.method == "POST":
        # Fetch checkout form details
        shipping_address = request.POST.get("shipping_address")
        phone = request.POST.get("phone")
        pincode = request.POST.get("pincode")
        city = request.POST.get("city")
        state = request.POST.get("state")

        # Calculate total
        total_amount = sum(item.total_price() for item in CartItem.objects.filter(cart=cart))

        # Create order
        order = Order.objects.create(
            user=request.user,
            cart=cart,
            total_amount=total_amount,
            shipping_address=shipping_address,
            phone=phone,
            pincode=pincode,
            city=city,
            state=state,
            status="Pending"
        )

        messages.success(request, "Order placed successfully! Proceed to payment.")
        return redirect("payment", order_id=order.id)

    # GET request → show checkout page
    return render(request, "Glamkart/place_order.html", {"cart": cart})