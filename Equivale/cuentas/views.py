from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm, LoginForm, PerfilForm, DireccionForm
from .models import Direccion

# Vista registro
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Autentica al usuario después de registrarlo
            user = authenticate(email=user.email, password=form.cleaned_data['password'])
            if user:
                auth_login(request, user)
                messages.success(request, 'Registro exitoso y sesión iniciada.')
                return redirect('cuentas:perfil')
            else:
                messages.error(request, 'Error al autenticar al usuario.')
    else:
        form = RegistroForm()
    return render(request, 'cuentas/registro.html', {'form': form})

# Vista login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('cuentas:perfil') 
            else:
                messages.error(request, 'Credenciales incorrectas.')
    else:
        form = LoginForm()
    return render(request, 'cuentas/login.html', {'form': form})

# Vista logout
@login_required
def logout_view(request):
    auth_logout(request)
    return render(request, 'cuentas/logout.html')

# Vista perfil
@login_required
def perfil_view(request):
    user = request.user
    direccion = Direccion.objects.filter(usuario=user).first()

    if request.method == 'POST':
        perfil_form = PerfilForm(request.POST, instance=user)
        direccion_form = DireccionForm(request.POST, instance=direccion)

        if perfil_form.is_valid() and direccion_form.is_valid():
            perfil_form.save()
            if direccion_form.instance:
                direccion_form.instance.usuario = user
                direccion_form.save()
            else:
                direccion_form.instance.usuario = user
                direccion_form.save()
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('cuentas:perfil')
    else:
        perfil_form = PerfilForm(instance=user)
        direccion_form = DireccionForm(instance=direccion)

    return render(request, 'cuentas/perfil.html', {
        'perfil_form': perfil_form,
        'direccion_form': direccion_form,
    })


def base_view(request):
    return render(request, 'base.html')