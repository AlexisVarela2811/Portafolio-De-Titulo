from productos.models import MetodoEntrega

def cargar_metodos_entrega():
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

# python manage.py shell
# from data.script_metodos_entrega import cargar_metodos_entrega
# cargar_metodos_entrega()