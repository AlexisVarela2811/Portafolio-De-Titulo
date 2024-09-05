from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre, correo, password=None, **extra_fields):
        correo = self.normalize_email(correo)
        usuario = self.model(
            correo=correo,
            nombre=nombre,
            **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

class Usuario(AbstractBaseUser, PermissionsMixin):
    usuarioid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    correo = models.EmailField(max_length=100, unique=True)
    fecharegistro = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre

