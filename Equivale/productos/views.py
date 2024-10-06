from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.db import connection
from decimal import Decimal

from .models import (
    Categoria, Producto, Carrito, CarritoItem, Pedido, Donacion,
    ApadrinamientoArbol, TipoArbol, MetodoEntrega, CausaAmbiental
)
from .forms import ProductoForm, SearchForm
from .paypal import crear_pago, ejecutar_pago

@login_required
def obtener_subcategorias(request):
    categoria_padre_id = request.GET.get('categoria_padre_id')
    subcategorias = Categoria.objects.filter(categoria_padre_id=categoria_padre_id) if categoria_padre_id else []
    subcategorias_data = [{'id': sub.id, 'nombre': sub.nombre} for sub in subcategorias]
    return JsonResponse({'subcategorias': subcategorias_data})

@login_required
def gestionar_productos(request, id=None):
    producto = get_object_or_404(Producto, id=id) if id else None
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)

    if request.method == 'POST' and form.is_valid():
        producto = form.save(commit=False)
        if not producto.pk:
            producto.creador = request.user
        producto.save()
        return redirect('productos:listar_productos')

    categorias = Categoria.objects.filter(categoria_padre__isnull=True)
    return render(request, 'productos/gestionar_productos.html', {
        'form': form,
        'editing': id is not None,
        'categorias': categorias
    })

@login_required
def listar_productos(request):
    productos = Producto.objects.filter(creador=request.user)
    return render(request, 'productos/listar_productos.html', {'productos': productos})

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos:listar_productos')
    return render(request, 'productos/eliminar_confirmar.html', {'producto': producto})

def pagina_principal(request):
    productos = Producto.objects.all().select_related('categoria', 'subcategoria', 'creador')
    categorias = Categoria.objects.filter(categoria_padre__isnull=True)

    filtros = {
        'categoria_id': request.GET.get('categoria'),
        'subcategoria_id__in': request.GET.getlist('subcategoria'),
        'nombre__icontains': request.GET.get('q'),
        'descripcion__icontains': request.GET.get('q'),
        'precio__gte': request.GET.get('precio_min'),
        'precio__lte': request.GET.get('precio_max')
    }
    
    productos = productos.filter(**{k: v for k, v in filtros.items() if v})

    orden = request.GET.get('orden', 'fechacreacion')
    ordering_map = {
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'nombre': 'nombre',
        'fechacreacion': '-fechacreacion'
    }
    productos = productos.order_by(ordering_map.get(orden, '-fechacreacion'))

    paginator = Paginator(productos, 20)
    page = request.GET.get('page')
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)

    context = {
        'productos': productos,
        'categorias': categorias,
        'subcategorias': Categoria.objects.filter(categoria_padre_id=filtros['categoria_id']) if filtros['categoria_id'] else [],
        **filtros,
        'orden': orden
    }
    return render(request, 'productos/pagina_principal.html', context)

def detalle_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, 'productos/detalle_producto.html', {'producto': producto})

def crear_carrito(user):
    return Carrito.objects.get_or_create(usuario=user)[0]

def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = crear_carrito(request.user)
    carrito_item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()
    return redirect('productos:ver_carrito')

def calcular_totales(carrito_items, porcentaje_donacion, arbol_id, metodo_entrega_id):
    total_carrito = sum(item.cantidad * item.producto.precio for item in carrito_items)
    costo_arbol = TipoArbol.objects.filter(id=arbol_id).first().costo if arbol_id else 0
    costo_envio = MetodoEntrega.objects.filter(id=metodo_entrega_id).first().costo if metodo_entrega_id else 0
    total_donacion = total_carrito * Decimal(porcentaje_donacion) / Decimal(100)

    total = total_carrito + costo_arbol + costo_envio + total_donacion
    return total, total_carrito, costo_arbol, costo_envio, total_donacion

def ver_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    carrito_items = CarritoItem.objects.filter(carrito=carrito)
    
    metodo_envio_id = request.POST.get('metodo_entrega')
    porcentaje_donacion = int(request.POST.get('porcentaje_donacion', 0))
    tipo_arbol_id = request.POST.get('tipo_arbol')
    
    total, total_carrito, costo_arbol, costo_envio, total_donacion = calcular_totales(
        carrito_items, porcentaje_donacion, tipo_arbol_id, metodo_envio_id
    )
    
    causa_ambiental = CausaAmbiental.objects.filter(id=request.POST.get('causa_ambiental')).first()

    contexto = {
        'carrito_items': carrito_items,
        'total_carrito': total_carrito,
        'costo_envio': costo_envio,
        'total_donacion': total_donacion,
        'costo_arbol': costo_arbol,
        'total_final': total,
        'metodos_entrega': MetodoEntrega.objects.all(),
        'tipos_arbol': TipoArbol.objects.all(),
        'porcentaje_donacion': porcentaje_donacion,
        'selected_arbol': tipo_arbol_id,
        'causas_ambientales': CausaAmbiental.objects.all(),
        'selected_causa_ambiental': causa_ambiental,
    }

    return render(request, 'productos/ver_carrito.html', contexto)

def eliminar_item_carrito(request, item_id):
    carrito_item = get_object_or_404(CarritoItem, id=item_id)
    carrito_item.delete()
    return redirect('productos:ver_carrito')

@require_POST
def actualizar_cantidad(request, item_id):
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
def ver_voucher(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'productos/voucher.html', {'pedido': pedido})

@login_required
def generar_pedido(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método de solicitud no permitido'})

    usuario = request.user
    carrito = get_object_or_404(Carrito, usuario=usuario)

    metodo_entrega_id = request.POST.get('metodo_entrega')
    porcentaje_donacion = request.POST.get('porcentaje_donacion', '0')
    tipo_arbol_id = request.POST.get('tipo_arbol')
    causa_ambiental_id = request.POST.get('causa_ambiental')
    total_final = request.POST.get('total_final')

    if not metodo_entrega_id or not metodo_entrega_id.isdigit():
        return JsonResponse({'success': False, 'message': 'Método de entrega inválido'})

    try:
        metodo_entrega = MetodoEntrega.objects.get(id=int(metodo_entrega_id))
    except MetodoEntrega.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Método de entrega no encontrado'})

    if not total_final or Decimal(total_final) <= 0:
        return JsonResponse({'success': False, 'message': 'El total final no es válido'})

    direccion_usuario = usuario.direcciones.first()
    if not direccion_usuario:
        return JsonResponse({'success': False, 'message': 'El usuario no tiene direcciones registradas'})

    pedido = Pedido.objects.create(
        usuario=usuario,
        total=Decimal(total_final),
        total_final=Decimal(total_final),
        carrito=carrito,
        porcentaje_donacion=Decimal(porcentaje_donacion) if porcentaje_donacion.isdigit() else None,
        metodo_entrega=metodo_entrega,
        direccion_entrega=direccion_usuario,
        region_entrega=direccion_usuario.comuna.region,
        comuna_entrega=direccion_usuario.comuna,
        estado='Pendiente'
    )

    if Decimal(porcentaje_donacion) > 0:
        causa = CausaAmbiental.objects.filter(id=causa_ambiental_id).first()
        donacion = Donacion.objects.create(
            causa=causa,
            monto=Decimal(total_final) * (Decimal(porcentaje_donacion) / Decimal(100)),
            porcentaje=Decimal(porcentaje_donacion),
            pedido_donacion=pedido
        )
        pedido.monto_donacion = donacion
        pedido.save()

    payment = crear_pago(pedido)
    if payment:
        approval_url = next((link.href for link in payment.links if link.rel == "approval_url"), None)
        if approval_url:
            return HttpResponseRedirect(approval_url)

    return JsonResponse({'success': False, 'message': 'Error al crear el pago en PayPal'})

@login_required
def confirmar_pago(request, pedido_id):
    payer_id = request.GET.get('PayerID')
    payment_id = request.GET.get('paymentId')

    if not payer_id or not payment_id:
        return JsonResponse({'success': False, 'message': 'No se proporcionaron datos válidos'})

    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    payment = ejecutar_pago(payer_id, payment_id)

    if payment and payment.state == "approved":
        pedido.estado = 'Pagado'
        pedido.save()

        for item in CarritoItem.objects.filter(carrito=pedido.carrito):
            producto = item.producto
            producto.stock -= item.cantidad 
            producto.save()

        return redirect('productos:voucher', pedido_id=pedido.id)
    else:
        return JsonResponse({'success': False, 'message': 'Error al confirmar el pago.'})

@login_required
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    pedido.delete()
    return redirect('productos:lista_pedidos')

@login_required
def cancelar_pago(request):
    return render(request, 'paypal/cancelar_pago.html')

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, 'productos/mis_pedidos.html', {'pedidos': pedidos})

@login_required
def cancelar_pedido(request, pedido_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})

    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    pedido.estado = 'Cancelado'
    pedido.save()

    for item in CarritoItem.objects.filter(carrito=pedido.carrito):
        producto = item.producto
        producto.stock += item.cantidad 
        producto.save()

    return JsonResponse({'success': True, 'message': 'Pedido cancelado con éxito.'})

@login_required
def productos_vendidos(request):
    usuario_id = request.user.usuarioid
    with connection.cursor() as cursor:
        cursor.callproc('generar_informe_ventas_usuario', [usuario_id])
        cursor.execute("SELECT * FROM ventas_usuario")
        resultados = cursor.fetchall()
    return render(request, 'productos/productos_vendidos.html', {'resultados': resultados})

@login_required
def borrar_pedidos(request):
    Pedido.objects.all().delete()
    return redirect('mis_pedidos')