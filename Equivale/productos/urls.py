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
    path('buscar/', views.buscar_productos, name='buscar_productos'), #Permite realizar la busqueda de productos en barra de búsqueda
    path('eliminar_item_carrito/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'), #Permite eliminar un item del carrito
    path('actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),#  Permite actualizar la cantidad de un item del carrito
    path('obtener_subcategorias/', views.obtener_subcategorias, name='obtener_subcategorias'),# Permite obtener las subcategorias en el front end
    path('voucher/<int:pedido_id>/', views.ver_voucher, name='voucher'),# Permite emitir un voucher al cliente
    path('pedido/', views.generar_pedido, name='generar_pedido'),# Genera un pedido 
    path('pedido/cancelar/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),  # URL para cancelar pedidos

    path('pedido/<int:pedido_id>/eliminar/', views.eliminar_pedido, name='eliminar_pedido'),
    path('mispedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('confirmar_pago/<int:pedido_id>/', views.confirmar_pago, name='confirmar_pago'),
    path('cancelar_pago/', views.cancelar_pago, name='cancelar_pago'),
    path('productos-vendidos/', views.productos_vendidos, name='productos_vendidos'),
]