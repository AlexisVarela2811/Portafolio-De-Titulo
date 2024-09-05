from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
#from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from .forms import RegistroForm, LoginForm
from .models import Usuario

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            token, created = Token.objects.get_or_create(user=user)
            messages.success(request, f'Registro exitoso! Token: {token.key}')
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
                token, created = Token.objects.get_or_create(user=user)
                messages.success(request, f'Login exitoso! Token: {token.key}')
                return redirect('cuentas:registro')
            else:
                messages.error(request, 'Credenciales incorrectas.')
    else:
        form = LoginForm()
    return render(request, 'cuentas/login.html', {'form': form})
