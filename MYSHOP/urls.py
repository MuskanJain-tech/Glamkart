from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # <--- Important

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Glamkart.urls')),
]

# ✅ Media files ko serve karne ke liye (sirf development mode me)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
