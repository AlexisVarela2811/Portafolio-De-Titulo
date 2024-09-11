from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.shortcuts import redirect
from social_core.exceptions import AuthAlreadyAssociated
import requests

#Funcion para guardar el usuario en el modelo de usuario ademas de obtener los datos del usuario y validar
def save_user_from_oauth(backend, details, response, user=None, *args, **kwargs):
    UserModel = get_user_model()
    name = None
    email = None
    if backend.name == 'google-oauth2':
        name = response.get('name') or details.get('fullname')
    elif backend.name == 'github':
        name = response.get('name') or details.get('fullname')
    if not name:
        name = details.get('email', '').split('@')[0]
    if user:
        user.nombre = name
        if backend.name == 'github':
            access_token = response.get('access_token')
            email = get_github_email(access_token)
        else:
            email = details.get('email')
        user.email = email
        user.save()
    else:
        try:
            if backend.name == 'github':
                access_token = response.get('access_token')
                email = get_github_email(access_token)
            else:
                email = details.get('email')

            user = UserModel.objects.create_user(
                nombre=name,
                email=email,
            )
        except Exception as e:
            print(f"Error creating user: {e}")
            user = UserModel.objects.get(email=email)
    request = kwargs.get('request')
    if request:
        user = authenticate(request, email=email)
        if user:
            auth_login(request, user)
            redirect_url = kwargs.get('redirect_url', 'cuentas:perfil')
            return redirect(redirect_url)
    return {
        'nombre': name,
        'email': email,
    }

#Scope Para solicitar a git email de usuario de forma adicional
def get_github_email(access_token):
    url = "https://api.github.com/user/emails"
    headers = {"Authorization": f"token {access_token}"}
    response = requests.get(url, headers=headers)
    emails = response.json()
    for email_info in emails:
        if email_info.get('primary'):
            return email_info.get('email')
    return None


#Falta generar validacion que no se puedan ocupar los mismos correos en ambas plataformas o con registro convencional