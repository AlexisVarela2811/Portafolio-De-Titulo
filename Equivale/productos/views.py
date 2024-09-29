from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import (
    Categoria, Producto, Carrito, CarritoItem, Pedido, Donacion,
    ApadrinamientoArbol, TipoArbol, MetodoEntrega, CausaAmbiental
)
from .forms import ProductoForm, SearchForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from decimal import Decimal
from django.views.decorators.http import require_POST
from productos.paypal import crear_pago, ejecutar_pago
from django.http import HttpResponseRedirect
from django.db import connection

#Enviar las subcategorias al front end para poder ser resivido mediante js
@login_required
def obtener_subcategorias(request):
    categoria_padre_id = request.GET.get('categoria_padre_id')
    subcategorias_data = []

    if categoria_padre_id:
        subcategorias = Categoria.objects.filter(categoria_padre_id=categoria_padre_id)
        subcategorias_data = [{'id': subcategoria.id, 'nombre': subcategoria.nombre} for subcategoria in subcategorias]

    return JsonResponse({'subcategorias': subcategorias_data})

#Permite editar los productos creados del usuario
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

#Pagina pricipal de  de productos Grilla
def pagina_principal(request):
    productos = Producto.objects.all().select_related('categoria', 'subcategoria', 'creador')
    categorias = Categoria.objects.filter(categoria_padre__isnull=True)

    # Aplicar filtros
    categoria_id = request.GET.get('categoria')
    subcategoria_ids = request.GET.getlist('subcategoria')
    search_query = request.GET.get('q')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if subcategoria_ids:
        productos = productos.filter(subcategoria_id__in=subcategoria_ids)
    if search_query:
        productos = productos.filter(Q(nombre__icontains=search_query) | Q(descripcion__icontains=search_query))
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    subcategorias = Categoria.objects.filter(categoria_padre_id=categoria_id) if categoria_id else []

    # Ordenamiento
    orden = request.GET.get('orden', 'fechacreacion')
    ordering_map = {
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'nombre': 'nombre',
    }
    productos = productos.order_by(ordering_map.get(orden, '-fechacreacion'))

    # Paginación
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
        'categoria_id': categoria_id,
        'subcategorias': subcategorias,
        'subcategoria_ids': subcategoria_ids,
        'search_query': search_query,
        'orden': orden,
        'precio_min': precio_min,
        'precio_max': precio_max
    }
    return render(request, 'productos/pagina_principal.html', context)


#Detalle de un producto
def detalle_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, 'productos/detalle_producto.html', {'producto': producto})

def crear_carrito(user):
    carrito, created = Carrito.objects.get_or_create(usuario=user)
    return carrito

def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = crear_carrito(request.user)
    carrito_item, item_created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
    if not item_created:
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
    usuario = request.user
    carrito = get_object_or_404(Carrito, usuario=usuario)
    carrito_items = CarritoItem.objects.filter(carrito=carrito)
    # Inicialización de variables
    total_carrito = 0
    costo_envio = 0
    total_donacion = 0
    costo_arbol = 0
    total_final = 0

    # Cálculo del total del carrito
    for item in carrito_items:
        total_carrito += item.producto.precio * item.cantidad

    # Cálculo del costo de envío
    metodo_envio_id = request.POST.get('metodo_entrega')
    if metodo_envio_id:
        metodo_envio = MetodoEntrega.objects.get(id=metodo_envio_id)
        costo_envio = metodo_envio.costo

    # Cálculo de la donación
    porcentaje_donacion = int(request.POST.get('porcentaje_donacion', 0))
    if porcentaje_donacion > 0:
        total_donacion = (porcentaje_donacion / 100) * total_carrito

    # Cálculo del costo del árbol
    tipo_arbol_id = request.POST.get('tipo_arbol')
    if tipo_arbol_id:
        tipo_arbol = TipoArbol.objects.get(id=tipo_arbol_id)
        costo_arbol = tipo_arbol.costo

    # Cálculo del total final
    total_final = total_carrito + costo_envio + total_donacion + costo_arbol

    # Selección de Causa Ambiental
    causa_ambiental_id = request.POST.get('causa_ambiental')
    selected_causa_ambiental = None
    if causa_ambiental_id:
        selected_causa_ambiental = CausaAmbiental.objects.get(id=causa_ambiental_id)

    # Contexto para pasar al template
    contexto = {
        'carrito_items': carrito_items,
        'total_carrito': total_carrito,
        'costo_envio': costo_envio,
        'total_donacion': total_donacion,
        'costo_arbol': costo_arbol,
        'total_final': total_final,
        'metodos_entrega': MetodoEntrega.objects.all(),
        'tipos_arbol': TipoArbol.objects.all(),
        'porcentaje_donacion': porcentaje_donacion,
        'selected_arbol': tipo_arbol_id,
        'causas_ambientales': CausaAmbiental.objects.all(),
        'selected_causa_ambiental': selected_causa_ambiental,
    }

    return render(request, 'productos/ver_carrito.html', contexto)

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
def ver_voucher(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    contexto = {
        'pedido': pedido,
    }

    return render(request, 'productos/voucher.html', contexto)


@login_required
def generar_pedido(request):
    if request.method == 'POST':
        usuario = request.user
        carrito = get_object_or_404(Carrito, usuario=usuario)

        # Obtener los datos enviados en el POST
        metodo_entrega_id = request.POST.get('metodo_entrega')
        porcentaje_donacion = request.POST.get('porcentaje_donacion', 0)
        tipo_arbol_id = request.POST.get('tipo_arbol')
        causa_ambiental_id = request.POST.get('causa_ambiental')
        total_final = request.POST.get('total_final')

        # Validar método de entrega
        if not metodo_entrega_id or not metodo_entrega_id.isdigit():
            return JsonResponse({'success': False, 'message': 'Método de entrega inválido'})

        metodo_entrega_id = int(metodo_entrega_id)

        try:
            metodo_entrega = MetodoEntrega.objects.get(id=metodo_entrega_id)
        except MetodoEntrega.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Método de entrega no encontrado'})

        # Validar que total_final no sea nulo o vacío
        if total_final is None or total_final == '':
            return JsonResponse({'success': False, 'message': 'El total final no es válido'})
        
        # Convierte total_final a Decimal
        try:
            total_final = Decimal(total_final)
        except (ValueError, InvalidOperation):
            return JsonResponse({'success': False, 'message': 'El total final no es un número válido'})

        # Verifica que total_final no sea menor o igual a 0
        if total_final <= 0:
            return JsonResponse({'success': False, 'message': 'El total final debe ser mayor que 0'})

        # Obtener dirección del usuario
        direccion_usuario = usuario.direcciones.first()
        if not direccion_usuario:
            return JsonResponse({'success': False, 'message': 'El usuario no tiene direcciones registradas'})

        # Crear Pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            total=total_final,  
            total_final=total_final,  
            carrito=carrito,
            monto_donacion=None,  
            porcentaje_donacion=Decimal(porcentaje_donacion) if porcentaje_donacion.isdigit() else None,
            apadrinamiento=None,  
            metodo_entrega=metodo_entrega,
            direccion_entrega=direccion_usuario,
            region_entrega=direccion_usuario.comuna.region,
            comuna_entrega=direccion_usuario.comuna,
            estado='Pendiente'
        )

        # Crear Donacion si hay porcentaje de donación
        donacion = None
        if porcentaje_donacion and Decimal(porcentaje_donacion) > 0:
            causa = None
            if causa_ambiental_id and causa_ambiental_id.isdigit():
                causa_ambiental_id = int(causa_ambiental_id)
                try:
                    causa = CausaAmbiental.objects.get(id=causa_ambiental_id)
                except CausaAmbiental.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Causa ambiental no encontrada'})

            donacion = Donacion.objects.create(
                causa=causa,
                monto=total_final * (Decimal(porcentaje_donacion) / Decimal(100)), 
                porcentaje=Decimal(porcentaje_donacion),
                pedido_donacion=pedido
            )

            pedido.monto_donacion = donacion
            pedido.save()

        payment = crear_pago(pedido)
        if payment:
            for link in payment.links:
                if link.rel == "approval_url":
                    return HttpResponseRedirect(link.href)

            return JsonResponse({'success': False, 'message': 'Error al crear el pago en PayPal'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no permitido'})

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

        for item in CarritoItem.objects.filter(carrito=pedido.carrito):
            producto = item.producto
            producto.stock -= item.cantidad 
            producto.save()

        pedido.save()
        return redirect('productos:voucher', pedido_id=pedido.id)
    else:
        return JsonResponse({'success': False, 'message': 'Error al confirmar el pago.'})

def eliminar_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
        pedido.delete()
        return redirect('productos:lista_pedidos') 
    except Pedido.DoesNotExist:
        return redirect('productos:lista_pedidos')  

@login_required
def cancelar_pago(request):
    return render(request, 'paypal/cancelar_pago.html')

def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, 'productos/mis_pedidos.html', {'pedidos': pedidos})

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    if request.method == 'POST':
        pedido.estado = 'Cancelado'

        for item in CarritoItem.objects.filter(carrito=pedido.carrito):
            producto = item.producto
            producto.stock += item.cantidad 
            producto.save()

        pedido.save()
        return JsonResponse({'success': True, 'message': 'Pedido cancelado con éxito.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def productos_vendidos(request):
    usuario_id = request.user.usuarioid
    with connection.cursor() as cursor:
        cursor.callproc('generar_informe_ventas_usuario', [usuario_id])
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ventas_usuario_temp")
        resultados = cursor.fetchall()
    return render(request, 'productos/productos_vendidos.html', {'resultados': resultados})

