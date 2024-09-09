from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        usuario = self.model(
            email=email,
            nombre=nombre,
            **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, nombre, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(nombre, email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    usuarioid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    email = models.EmailField(max_length=100, unique=True) 
    fecharegistro = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre

class Region(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="comunas")

    def __str__(self):
        return f'{self.nombre}, {self.region.nombre}'

class Direccion(models.Model):
    usuario = models.ForeignKey('cuentas.Usuario', on_delete=models.CASCADE, related_name='direcciones')
    direccion = models.CharField(max_length=255)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.direccion}, {self.comuna.nombre}, {self.comuna.region.nombre}'

