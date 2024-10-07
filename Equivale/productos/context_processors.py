from django.utils.functional import cached_property

def format_precio(request):
    return {
        'format_precio': lambda precio: f"{int(precio)}" if precio else "0"
    }
