from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Order, Cart, Wishlist, Product


# 🔹 Auto-create Cart & Wishlist for new users
@receiver(post_save, sender=User)
def create_user_cart_and_wishlist(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
        Wishlist.objects.create(user=instance, product=None)           # empty placeholder
        print(f"✅ Cart & Wishlist created for {instance.username}")

# 🔹 Reduce stock after Order is placed

@receiver(post_save, sender=Order)
def reduce_stock_on_order(sender, instance, created, **kwargs):
    if created and instance.items.exists():
        for item in instance.items.all():
            product = item.product
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()
        print(f"📦 Stock updated for order {instance.id}")

        # Clear cart after successful order

        Cart.objects.filter(user=instance.user).delete()
        print(f"🧹 Cart cleared for {instance.user.username}")

        # Send confirmation email

        send_mail(
            subject="Order Confirmation - Glamkart",
            message=f"Hello {instance.user.username},\n\nYour order #{instance.id} has been placed successfully!",
            from_email="no-reply@glamkart.com",
            recipient_list=[instance.user.email],
            fail_silently=True,
        )
        print(f"📧 Confirmation email sent to {instance.user.email}")


# 🔹 Restore stock if order is deleted/canceled

@receiver(post_delete, sender=Order)
def restore_stock_on_order_delete(sender, instance, **kwargs):
    if instance.items.exists():
        for item in instance.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        print(f"♻️ Stock restored for canceled order {instance.id}")
