import json
from cuentas.models import Region, Comuna

def cargar_regiones_y_comunas():
    with open('data/regiones.json', encoding='utf-8') as file:
        data = json.load(file)

    for region_data in data['regiones']:
        region_nombre = region_data['region']
        region, created = Region.objects.get_or_create(nombre=region_nombre)
        
        for comuna_nombre in region_data['comunas']:
            Comuna.objects.get_or_create(nombre=comuna_nombre, region=region)

    print("Regiones y comunas cargadas exitosamente.")

#python manage.py shell
#from data.script_load import cargar_regiones_y_comunas
#cargar_regiones_y_comunas()