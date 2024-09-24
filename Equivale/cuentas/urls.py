from django.urls import path
from .views import registro_view,login_view, perfil_view, logout_view, base_view

app_name = 'cuentas'

urlpatterns = [
    path('registro/', registro_view, name='registro'),
    path('login/', login_view, name='login'),
    path('perfil/', perfil_view, name='perfil'),
    path('logout/',logout_view, name='logout'),
    path('base/', base_view, name='base'),
]
