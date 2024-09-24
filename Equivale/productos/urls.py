from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.pagina_principal, name='pagina_principal'),
    path('gestionar/', views.gestionar_productos, name='gestionar_productos'),  # Para crear un producto
    path('gestionar/<int:id>/', views.gestionar_productos, name='gestionar_productos_con_id'),  # Para editar un producto
    path('listar/', views.listar_productos, name='listar_productos'),  # Para listar productos
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),  # Para eliminar un producto
    path('subcategorias/', views.obtener_subcategorias, name='obtener_subcategorias'), #Obtener subcategorias
    path('detalle/<int:id>/', views.detalle_producto, name='detalle_producto'),  # Para ver detalle de un producto
    path('agregar_carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'), #Agregar producto al carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'), #Ver el carrito
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('eliminar_item_carrito/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'), 
    path('actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('obtener_subcategorias/', views.obtener_subcategorias, name='obtener_subcategorias'),
]