"""Equivale URL Configuration"""
from unicodedata import name
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    #panel admin django
    path('', include('productos.urls')),
    path('admin/', admin.site.urls),
    #apps
    path('cuentas/', include(('cuentas.urls','cuentas'), namespace='cuentas')),
    path('productos/', include(('productos.urls','productos'), namespace='productos')),
    #oauth
    path('social-auth/', include('social_django.urls', namespace='social'))
]
#Imagenes
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)