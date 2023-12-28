from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from pfimapp.models import CustomUser, TipoDocumento, EstadoCivil, Maestria, Sede
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _

class CustomAuthenticationForm(AuthenticationForm):        
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control','autocomplete': 'email', 'autofocus': True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control','autocomplete': 'current-password'}),
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='Correo (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nacionalidad = forms.CharField(label='Nacionalidad (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    tipoDocumento = forms.ModelChoiceField(label='Tipo de Documento (*)',queryset=TipoDocumento.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control required'}))
    numeroDocumento = forms.CharField(label='Número de Documento (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    numeroUbigeoNacimiento = forms.CharField(label='Número de ubigeo de nacimiento (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    direccion = forms.CharField(label='Dirección (*)',max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))    
    primerNombre = forms.CharField(label='Primer Nombre (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    segundoNombre = forms.CharField(label='Segundo Nombre',max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidoPaterno = forms.CharField(label='Apellido Paterno (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    apellidoMaterno = forms.CharField(label='Apellido Materno (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    estadoCivil = forms.ModelChoiceField(label='Estado Civil (*)',queryset=EstadoCivil.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control required'}))
    correoUNI = forms.EmailField(label='Correo UNI',max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))     
    telefono = forms.CharField(label='Celular (*)',max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))        
    fechaNacimiento = forms.DateField(label='Fecha de Nacimiento (*)',required=False, widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('email','nacionalidad', 'tipoDocumento', 'numeroDocumento','numeroUbigeoNacimiento', 'direccion', 'primerNombre', 'segundoNombre', 'apellidoPaterno', 'apellidoMaterno', 'estadoCivil', 'fechaNacimiento','correoUNI', 'telefono','fechaNacimiento')


class CustomUserForm(forms.ModelForm):
    email = forms.EmailField(label='Correo (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nacionalidad = forms.CharField(label='Nacionalidad (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    tipoDocumento = forms.ModelChoiceField(label='Tipo de Documento (*)',queryset=TipoDocumento.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control required'}))
    numeroDocumento = forms.CharField(label='Número de Documento (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    numeroUbigeoNacimiento = forms.CharField(label='Número de ubigeo de nacimiento (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    direccion = forms.CharField(label='Dirección (*)',max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))    
    primerNombre = forms.CharField(label='Primer Nombre (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    segundoNombre = forms.CharField(label='Segundo Nombre',max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidoPaterno = forms.CharField(label='Apellido Paterno (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    apellidoMaterno = forms.CharField(label='Apellido Materno (*)',max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))
    estadoCivil = forms.ModelChoiceField(label='Estado Civil (*)',queryset=EstadoCivil.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control required'}))
    correoUNI = forms.EmailField(label='Correo UNI',max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))     
    telefono = forms.CharField(label='Celular (*)',max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control required'}))        
    fechaNacimiento = forms.DateField(label='Fecha de Nacimiento (*)',required=False, widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('email','nacionalidad', 'tipoDocumento', 'numeroDocumento','numeroUbigeoNacimiento', 'direccion', 'primerNombre', 'segundoNombre', 'apellidoPaterno', 'apellidoMaterno', 'estadoCivil', 'fechaNacimiento','correoUNI', 'telefono','fechaNacimiento')

