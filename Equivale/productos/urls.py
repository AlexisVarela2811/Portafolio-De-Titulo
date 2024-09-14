from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('gestionar/', views.gestionar_productos, name='gestionar_productos'),  # Para crear un producto
    path('gestionar/<int:id>/', views.gestionar_productos, name='gestionar_productos_con_id'),  # Para editar un producto
    path('listar/', views.listar_productos, name='listar_productos'),  # Para listar productos
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),  # Para eliminar un producto
    path('subcategorias/', views.obtener_subcategorias, name='obtener_subcategorias'),
]