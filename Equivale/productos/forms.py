from django import forms
from .models import Producto, Categoria

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'marca', 'descripcion', 'precio', 'stock', 'imagen', 'categoria', 'subcategoria']
    
    subcategoria = forms.ModelChoiceField(queryset=Categoria.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'categoria' in self.data:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = Categoria.objects.filter(categoria_padre_id=categoria_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['subcategoria'].queryset = Categoria.objects.none()
        
        elif self.instance.pk:
            if self.instance.categoria:
                self.fields['subcategoria'].queryset = Categoria.objects.filter(categoria_padre=self.instance.categoria)
                if self.instance.subcategoria:
                    self.fields['subcategoria'].initial = self.instance.subcategoria
            else:
                self.fields['subcategoria'].queryset = Categoria.objects.none()

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Buscar productos')
