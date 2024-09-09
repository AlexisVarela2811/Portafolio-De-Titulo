from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import Usuario, Direccion, Comuna

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")
    class Meta:
        model = get_user_model()
        fields = ['nombre', 'email', 'password'] 

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")  
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')  
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)  
            if user is None:
                raise forms.ValidationError('Credenciales incorrectas.')
        return cleaned_data

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email']  
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}), 
        }

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['direccion', 'comuna']

    comuna = forms.ModelChoiceField(queryset=Comuna.objects.all(), label='Comuna')

