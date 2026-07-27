from django.contrib import admin
from .models import (
    Category, Product, Cart, CartItem, Wishlist, Order, OrderItem,
    Review, Gallery, Payment, Profile, Notification
)

# ---------------- Inline Models ----------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


# ---------------- Category ----------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "icon")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


# ---------------- Product ----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock", "created_at", "updated_at")
    list_filter = ("category", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)


# ---------------- Gallery ----------------
@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "image", "video")
    search_fields = ("title",)


# ---------------- Cart ----------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__username",)
    inlines = [CartItemInline]


# ---------------- Wishlist ----------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")
    search_fields = ("user__username", "product__name")


# ---------------- Order ----------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "shipping_address")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)
    readonly_fields = ("total_amount",)


# ---------------- Payment ----------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "method", "amount", "success", "payment_date")
    list_filter = ("method", "success", "payment_date")
    search_fields = ("order__user__username",)


# ---------------- Review ----------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "product__name", "comment")
    ordering = ("-created_at",)


# ---------------- Profile ----------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "photo")
    search_fields = ("user__username",)


# ---------------- Notification ----------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")

from django.contrib import admin
from .models import Contact

admin.site.register(Contact)
