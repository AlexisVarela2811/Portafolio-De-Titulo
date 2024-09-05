from django.urls import path
from .views import registro_view, login_view

app_name = 'cuentas'

urlpatterns = [
    path('registro/', registro_view, name='registro'),
    path('login/', login_view, name='login'),
]
