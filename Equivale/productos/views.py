from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Categoria, Producto
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required

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


@login_required
def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/listar_productos.html', {'productos': productos})

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos:listar_productos')
    return render(request, 'productos/eliminar_confirmar.html', {'producto': producto})