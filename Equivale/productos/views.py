from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Categoria, Producto, Carrito, CarritoItem, Pedido, Donacion, ApadrinamientoArbol, TipoArbol, MetodoEntrega, Envio, CarritoItem
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .forms import ProductoForm, SearchForm, ApadrinamientoArbolForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q , Sum
from django.conf import settings
from decimal import Decimal
from django.views.decorators.http import require_POST

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
    tipos_arbol = TipoArbol.objects.all()
    metodos_entrega = MetodoEntrega.objects.all()

    total_carrito = sum(item.cantidad * item.producto.precio for item in carrito_items)
    
    carrito_items_totales = [
        {
            'id': item.id,
            'producto': item.producto,
            'cantidad': item.cantidad,
            'total_producto': item.cantidad * item.producto.precio
        }
        for item in carrito_items
    ]

    if request.method == 'POST':
        porcentaje_donacion = request.POST.get('porcentaje_donacion', '0')
        metodo_entrega_id = request.POST.get('metodo_entrega', None)
        
        try:
            porcentaje_donacion = int(porcentaje_donacion)
        except ValueError:
            porcentaje_donacion = 0

        arbol_id = request.POST.get('tipo_arbol')
        costo_arbol = 0 
        if arbol_id:
            arbol = get_object_or_404(TipoArbol, id=arbol_id)
            costo_arbol = arbol.costo

        if metodo_entrega_id:
            metodo_entrega = get_object_or_404(MetodoEntrega, id=metodo_entrega_id)
            costo_envio = metodo_entrega.costo
        else:
            costo_envio = 0

        total_donacion = total_carrito * Decimal(porcentaje_donacion) / Decimal(100)
    else:
        porcentaje_donacion = 0
        total_donacion = 0
        costo_arbol = 0
        costo_envio = 0

    total_con_arbol = total_carrito + costo_arbol + costo_envio

    return render(request, 'productos/ver_carrito.html', {
        'carrito_items': carrito_items_totales,
        'total_carrito': total_carrito,
        'total_con_arbol': total_con_arbol,
        'total_donacion': total_donacion,
        'tipos_arbol': tipos_arbol,
        'metodos_entrega': metodos_entrega,
        'porcentaje_donacion': porcentaje_donacion,
        'costo_arbol': costo_arbol,
        'costo_envio': costo_envio
    })

#Eliminar item del carrito
def eliminar_item_carrito(request, item_id):
    carrito_item = get_object_or_404(CarritoItem, id=item_id)
    carrito_item.delete()
    return redirect('productos:ver_carrito')

#Actualizar numero de productos en el carro
@require_POST
def actualizar_cantidad(request, item_id):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        try:
            carrito_item = CarritoItem.objects.get(id=item_id)
            carrito_item.cantidad = cantidad
            carrito_item.save()

            total_producto = carrito_item.cantidad * carrito_item.producto.precio
            total_carrito = sum(item.cantidad * item.producto.precio for item in CarritoItem.objects.filter(carrito=carrito_item.carrito))

            return JsonResponse({
                'success': True,
                'item_id': item_id,
                'nuevo_total_producto': total_producto,
                'nuevo_total_carrito': total_carrito
            })

        except CarritoItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item no encontrado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

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

@login_required
def checkout_vista(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    carrito_items = CarritoItem.objects.filter(carrito=carrito)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            pedido = Pedido.objects.create(
                usuario=request.user,
                total=0,  
                metodo_entrega=form.cleaned_data['metodo_entrega'],
                direccion_entrega=form.cleaned_data['direccion_entrega'],
                region_entrega=form.cleaned_data['region_entrega'],
                comuna_entrega=form.cleaned_data['comuna_entrega'],
            )

            total_donacion = 0
            if form.cleaned_data['causa_donacion']:
                porcentaje = form.cleaned_data['porcentaje_donacion']
                total_donacion = carrito_items.aggregate(
                    total=Sum('cantidad' * 'producto__precio')
                )['total'] or 0
                total_donacion *= (porcentaje / 100)

                donacion = Donacion.objects.create(
                    pedido_donacion=pedido,
                    causa=form.cleaned_data['causa_donacion'],
                    monto=total_donacion,
                    porcentaje=porcentaje,
                )
                pedido.monto_donacion = donacion

            apadrinamiento = None
            if form.cleaned_data['apadrinamiento']:
                apadrinamiento = ApadrinamientoArbol.objects.create(
                    usuario=request.user,
                    tipo_arbol=form.cleaned_data['tipo_arbol'],
                    latitud=form.cleaned_data['latitud'],
                    longitud=form.cleaned_data['longitud'],
                )
                pedido.apadrinamiento = apadrinamiento

            total_productos = carrito_items.aggregate(
                total=Sum('cantidad' * 'producto__precio')
            )['total'] or 0

            costo_envio = calcular_costo_envio(
                pedido.metodo_entrega,
                pedido.region_entrega,
                pedido.comuna_entrega
            )

            pedido.total = total_productos + total_donacion + costo_envio
            pedido.save()

            return redirect('productos:pedido_exitoso')

    else:
        form = CheckoutForm()
        arbol_form = ApadrinamientoArbolForm()
    return render(request, 'productos/checkout.html', {
        'form': form,
        'carrito_items': carrito_items,
        'arbol_form': arbol_form,
    })

def calcular_total_pedido(request):
    total = pedido.carrito.products.aggregate(total=Sum('Precio'))['total'] or 0
    if pedido.monto_donacion:
        total += pedido.monto_donacion
    costo_envio = calcular_costo_envio(pedido.region_entrega, pedido.comuna_entrega)
    total += costo_envio
    return total

