from django.contrib import admin
from django.urls import path
from rest_framework import routers
from api import views as api

from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'hash', api.HashViewSet, base_name='hash')

urlpatterns = [
    path('admin/', admin.site.urls),

] + router.urls

urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)