# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from .forms import RegistroForm, LoginForm
from .models import Usuario

"""

    Manejo de registro de nuevos usuarios
    Procesa los datos del formulario cuando se realiza una solicitud POST.
    Si el formulario es válido, guarda el nuevo usuario y redirige al formulario de inicio de sesión.
    En caso de una solicitud GET, muestra un formulario de registro vacío.

"""
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registro exitoso.')
            return redirect('cuentas:login')
    else:
        form = RegistroForm()
    return render(request, 'cuentas/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            password = form.cleaned_data['password']
            user = authenticate(correo=correo, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('cuentas:registro')
            else:
                messages.error(request, 'Credenciales incorrectas.')
    else:
        form = LoginForm()
    return render(request, 'cuentas/login.html', {'form': form})
