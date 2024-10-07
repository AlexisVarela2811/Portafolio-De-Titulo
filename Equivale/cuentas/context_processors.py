def nombre_usuario(request):
    if request.user.is_authenticated:
        return {'nombre': request.user.nombre.split()[0].capitalize()}
    return {'nombre': 'Invitado'}
