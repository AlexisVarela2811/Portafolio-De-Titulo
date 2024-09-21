from django import forms
from .models import Producto, Categoria, Direccion, CausaAmbiental, TipoArbol, Region, Comuna, Direccion, ApadrinamientoArbol

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

class CheckoutForm(forms.Form):
    direccion_entrega = forms.ModelChoiceField(queryset=Direccion.objects.none())
    region_entrega = forms.ModelChoiceField(queryset=Region.objects.none())
    comuna_entrega = forms.ModelChoiceField(queryset=Comuna.objects.none())
    causa_donacion = forms.ModelChoiceField(queryset=CausaAmbiental.objects.all(), required=False)
    porcentaje_donacion = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    apadrinamiento = forms.BooleanField(required=False)
    tipo_arbol = forms.ModelChoiceField(queryset=TipoArbol.objects.all(), required=False)

    def __init__(self, *args, direcciones, regiones, comunas, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direccion_entrega'].queryset = Direccion.objects.filter(usuario=user)
        self.fields['region_entrega'].queryset = Region.objects.filter(usuario=user)
        self.fields['comuna_entrega'].queryset = Comuna.objects.filter(usuario=user)

class DonacionForm(forms.Form):
    causa = forms.ModelChoiceField(queryset=CausaAmbiental.objects.all(), required=False, label='Causa ambiental')
    porcentaje_donacion = forms.ChoiceField(choices = [(5,'5%'),(10,'10%'), (15,'15%')], required=False, label='Porcentaje de donación')

class ApadrinamientoArbolForm(forms.ModelForm):
    class Meta:
        model = ApadrinamientoArbol
        fields = ['tipo_arbol']
        widgets = {
            'tipo_arbol': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ApadrinamientoArbolForm, self).__init__(*args, **kwargs)
        self.fields['tipo_arbol'].queryset = TipoArbol.objects.all()