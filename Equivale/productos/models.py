from django.db import models
from django.conf import settings
from cuentas.models import Comuna, Direccion, Region
#Categoria de productos
class Categoria(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria_padre = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='subcategorias')
    def __str__(self):
        return self.nombre

#Productos a comprar o vender
class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    marca = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    subcategoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_subcategoria')
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre

#Carrito de compras del usuario
class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='CarritoItem')

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

#Item del carrito de compras del usuario
class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('carrito', 'producto')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

# Causa ambiental para donaciones
class CausaAmbiental(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

#Donacion
class Donacion(models.Model):
    pedido_donacion = models.ForeignKey('Pedido', on_delete=models.CASCADE) 
    causa = models.ForeignKey('CausaAmbiental', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Donación {self.id} - Causa: {self.causa.nombre} - Monto: {self.monto}"

# Pedido
class Pedido(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_final = models.DecimalField(max_digits=10, decimal_places=2)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    monto_donacion = models.OneToOneField(Donacion, on_delete=models.SET_NULL, null=True, blank=True)
    porcentaje_donacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    apadrinamiento = models.ForeignKey('ApadrinamientoArbol', null=True, blank=True, on_delete=models.SET_NULL)
    metodo_entrega = models.ForeignKey('MetodoEntrega', on_delete=models.CASCADE)
    direccion_entrega = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    region_entrega = models.ForeignKey(Region, on_delete=models.CASCADE)
    comuna_entrega = models.ForeignKey(Comuna, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50, default='Pendiente')

    def __str__(self):
        return f"Pedido {self.id} - Usuario: {self.usuario.username} - Total: {self.total}"

#Tipo de arbol
class TipoArbol(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.nombre

#Apadrinamiento del arbol
class ApadrinamientoArbol(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_arbol = models.ForeignKey(TipoArbol, on_delete=models.CASCADE)
    fecha_apadrinamiento = models.DateTimeField(auto_now_add=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Apadrinamiento de {self.usuario.username} - {self.tipo_arbol.nombre}"
#Envios Metodo y Envio Modelos
class Envio(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    metodo_entrega = models.ForeignKey('MetodoEntrega', on_delete=models.CASCADE)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=50, default='Pendiente')

    def __str__(self):
        return f"Envío {self.id} Pedido de {self.pedido.usuario.username} costo {self.costo_envio}"

class MetodoEntrega(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tiempo_estimado = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.nombre
