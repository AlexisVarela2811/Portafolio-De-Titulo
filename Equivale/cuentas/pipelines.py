from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.shortcuts import redirect
from social_core.exceptions import AuthAlreadyAssociated

def save_user_from_oauth(backend, details, response, user=None, *args, **kwargs):
    UserModel = get_user_model()
    name = None

    if backend.name == 'google-oauth2':
        name = response.get('name')
        if not name:
            name = details.get('fullname')
    elif backend.name == 'github':
        name = response.get('name')
        if not name:
            name = details.get('fullname')
    if not name:
        name = details.get('email', '').split('@')[0]
    if user:
        user.nombre = name
        user.email = details.get('email')
        user.save()
    else:
        try:
            user = UserModel.objects.create_user(
                nombre=name,
                email=details.get('email'),
            )
        except Exception as e:
            print(f"Error creating user: {e}")
            user = UserModel.objects.get(email=details.get('email'))
    request = kwargs.get('request')
    if request:
        user = authenticate(request, email=details.get('email'))
        if user:
            auth_login(request, user)
            redirect_url = kwargs.get('redirect_url', 'cuentas:perfil')
            return redirect(redirect_url)
    return {
        'nombre': name,
        'email': details.get('email'),
    }
