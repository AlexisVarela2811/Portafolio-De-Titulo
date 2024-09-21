import json
from productos.models import TipoArbol

def cargar_tipos_arboles():
    with open('data/tipos_arboles.json', encoding='utf-8') as file:
        data = json.load(file)

    for arbol_data in data:
        nombre = arbol_data['nombre']
        descripcion = arbol_data['descripcion']

        TipoArbol.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
    
    print("Tipos de árboles cargados exitosamente.")


#    python manage.py shell
#    from data.script_load_arboles import cargar_tipos_arboles
#    cargar_tipos_arboles()