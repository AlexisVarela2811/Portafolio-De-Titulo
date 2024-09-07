# forms.py
from django import forms
from django.contrib.auth import authenticate
from .models import Usuario

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'password']

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
    correo = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    def clean(self):
        cleaned_data = super().clean()
        correo = cleaned_data.get('correo')
        password = cleaned_data.get('password')
        if correo and password:
            user = authenticate(correo=correo, password=password)
            if user is None:
                raise forms.ValidationError('Credenciales incorrectas.')
        return cleaned_data
