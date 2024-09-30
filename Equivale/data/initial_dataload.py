import json
from productos.models import TipoArbol, Categoria, MetodoEntrega
from cuentas.models import Region, Comuna

# Cargar árboles
def load_arboles():
    with open('data/tipos_arboles.json', encoding='utf-8') as file:
        data = json.load(file)

    for arbol_data in data:
        nombre = arbol_data['nombre']
        descripcion = arbol_data['descripcion']
        costo = arbol_data['costo']

        TipoArbol.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': descripcion,
                'costo': costo
            }
        )
    
    print("Tipos de árboles cargados exitosamente.")

# Cargar productos
def load_productos():
    with open('data/categorias.json', encoding='utf-8') as file:
        data = json.load(file)

    def cargar_categorias_recursivamente(categorias, categoria_padre=None):
        for cat_data in categorias:
            categoria, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={
                    'descripcion': cat_data.get('descripcion', ''),
                    'categoria_padre': categoria_padre
                }
            )

            if 'subcategorias' in cat_data:
                cargar_categorias_recursivamente(cat_data['subcategorias'], categoria)

    cargar_categorias_recursivamente(data)
    print("Categorías y subcategorías cargadas exitosamente.")

# Cargar regiones y comunas
def load_regiones():
    with open('data/regiones.json', encoding='utf-8') as file:
        data = json.load(file)

    for region_data in data['regiones']:
        region_nombre = region_data['region']
        region, created = Region.objects.get_or_create(nombre=region_nombre)
        
        for comuna_nombre in region_data['comunas']:
            Comuna.objects.get_or_create(nombre=comuna_nombre, region=region)

    print("Regiones y comunas cargadas exitosamente.")

# Cargar métodos entrega

def load_metodos_entrega():
    metodos = [
        {
            'nombre': 'Prioritario',
            'descripcion': 'Entrega antes de las 11:00 AM en RM y antes de las 12:00 PM en regiones el siguiente día hábil',
            'tiempo_estimado': '1 día hábil',
            'costo': 10000
        },
        {
            'nombre': 'Express',
            'descripcion': 'Entrega antes de las 19:00 PM el siguiente día hábil',
            'tiempo_estimado': '1 día hábil',
            'costo': 8000
        },
        {
            'nombre': 'Normal',
            'descripcion': 'Entrega dentro de 1-2 días hábiles antes de las 19:00 PM',
            'tiempo_estimado': '1-2 días hábiles',
            'costo': 6000  
        },
        {
            'nombre': 'Extremo',
            'descripcion': 'Entrega dentro de 2-3 días hábiles antes de las 19:00 PM',
            'tiempo_estimado': '2-3 días hábiles',
            'costo': 5000
        }
    ]

    for metodo_data in metodos:
        metodo, created = MetodoEntrega.objects.get_or_create(
            nombre=metodo_data['nombre'],
            defaults={
                'descripcion': metodo_data['descripcion'],
                'tiempo_estimado': metodo_data['tiempo_estimado'],
                'costo': metodo_data['costo']
            }
        )
        if created:
            print(f'Se creó el método de entrega: {metodo.nombre}')
        else:
            print(f'El método de entrega "{metodo.nombre}" ya existe')

# Cargar todos los datos iniciales de una vez

def load_all():
    load_arboles()
    load_productos()
    load_regiones()
    load_metodos_entrega()
    print("Todos los datos iniciales han sido cargados.")
