from django.db import models
from django.conf import settings
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
