from django import forms
from django.contrib.auth import authenticate
from .models import Usuario

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    correo = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        correo = self.cleaned_data.get('correo')
        password = self.cleaned_data.get('password')
        if correo and password:
            user = authenticate(correo=correo, password=password)
            if user is None:
                raise forms.ValidationError('Credenciales incorrectas')
        return super().clean()
