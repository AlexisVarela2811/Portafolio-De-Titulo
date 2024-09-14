import json
from productos.models import Categoria

def cargar_categorias():
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


if __name__ == "__main__":
    cargar_categorias()