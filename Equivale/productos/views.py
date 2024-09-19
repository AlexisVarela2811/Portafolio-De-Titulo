from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Categoria, Producto, Carrito, CarritoItem
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .forms import ProductoForm, SearchForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.conf import settings

#Enviar las subcategorias al front end para poder ser resivido mediante js
@login_required
def obtener_subcategorias(request):
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if categoria_padre_id:
        try:
            categoria_padre = Categoria.objects.get(id=categoria_padre_id)
            subcategorias = categoria_padre.subcategorias.all()
            subcategorias_data = [{'id': subcategoria.id, 'nombre': subcategoria.nombre} for subcategoria in subcategorias]
            return JsonResponse({'subcategorias': subcategorias_data})
        except Categoria.DoesNotExist:
            return JsonResponse({'subcategorias': []})
    else:
        return JsonResponse({'subcategorias': []})

#Permite editar los productos creados del usuario
@login_required
def gestionar_productos(request, id=None):
    if id:
        producto = get_object_or_404(Producto, id=id)
        form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    else:
        form = ProductoForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            producto = form.save(commit=False)
            if not producto.pk:
                producto.creador = request.user
            producto.save()
            return redirect('productos:listar_productos')
    
    return render(request, 'productos/gestionar_productos.html', {'form': form, 'editing': id is not None})

#Muestra la lista de productos del usuario
@login_required
def listar_productos(request):
    productos = Producto.objects.filter(creador=request.user)
    return render(request, 'productos/listar_productos.html', {'productos': productos})

#Permite eliminiar los productos
@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos:listar_productos')
    return render(request, 'productos/eliminar_confirmar.html', {'producto': producto})

#Grilla principal de productos
def pagina_principal(request):
    productos = Producto.objects.all().select_related('categoria', 'subcategoria', 'creador')

    # Filtros
    categoria_id = request.GET.get('categoria')
    subcategoria_id = request.GET.get('subcategoria')
    search_query = request.GET.get('q')

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if subcategoria_id:
        productos = productos.filter(subcategoria_id=subcategoria_id)
    if search_query:
        productos = productos.filter(
            Q(nombre__icontains=search_query) | 
            Q(descripcion__icontains=search_query)
        )

    # Ordenamiento
    orden = request.GET.get('orden', 'fechacreacion')
    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
    elif orden == 'nombre':
        productos = productos.order_by('nombre')
    else:
        productos = productos.order_by('-fechacreacion')

    # Paginación
    paginator = Paginator(productos, 20)
    page = request.GET.get('page')
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)

    categorias = Categoria.objects.filter(categoria_padre__isnull=True)

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_id': categoria_id,
        'subcategoria_id': subcategoria_id,
        'search_query': search_query,
        'orden': orden,
    }

    return render(request, 'productos/pagina_principal.html', context)

#Detalle de un producto
def detalle_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, 'productos/detalle_producto.html', {'producto': producto})

def crear_carrito(user):
    try:
        carrito = Carrito.objects.get(usuario=user)
    except Carrito.DoesNotExist:
        carrito = Carrito.objects.create(usuario=user)
    return carrito

def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = crear_carrito(request.user)
    carrito_item, item_created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
    if not item_created:
        carrito_item.cantidad += 1
        carrito_item.save()
    return redirect('productos:ver_carrito')

#Carrito Vista
def ver_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    carrito_items = CarritoItem.objects.filter(carrito=carrito)
    total_carrito = sum(item.cantidad * item.producto.precio for item in carrito_items)

    for item in carrito_items:
        item.total_precio = item.cantidad * item.producto.precio

    return render(request, 'productos/ver_carrito.html', {'carrito_items': carrito_items, 'total_carrito': total_carrito})

#Eliminar item del carrito
def eliminar_item_carrito(request, item_id):
    carrito_item = get_object_or_404(CarritoItem, id=item_id)
    carrito_item.delete()
    return redirect('productos:ver_carrito')

#Actualizar numero de productos en el carro
def actualizar_cantidad(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id)
    action = request.POST.get('action')
    cantidad = int(request.POST.get('cantidad', item.cantidad))
    if action == 'increase':
        item.cantidad += 1
    elif action == 'decrease' and item.cantidad > 1:
        item.cantidad -= 1
    else:
        item.cantidad = cantidad 
    item.save()
    return redirect('productos:ver_carrito')

#Busqueda productos
def buscar_productos(request):
    form = SearchForm(request.GET or None)
    productos = Producto.objects.all()

    if form.is_valid():
        search_query = form.cleaned_data.get('query')
        if search_query:
            productos = productos.filter(
                Q(nombre__icontains=search_query) |
                Q(descripcion__icontains=search_query)
            )

    context = {
        'productos': productos,
        'form': form,
    }
    return render(request, 'productos/buscar_productos.html', context)