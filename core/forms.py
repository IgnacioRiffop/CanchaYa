from django import forms
from .models import *

class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = ['nombre', 'direccion', 'imagen', 'hora_inicio', 'hora_fin', 'precio', 'tipo_cancha']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'tipo_cancha': forms.Select(attrs={'class': 'form-select'}),
        }

class TarifaForm(forms.ModelForm):
    class Meta:
        model = Tarifa
        fields = ['cancha', 'horario', 'precio']
        widgets = {
            'cancha': forms.Select(attrs={'class': 'form-select'}),
            'horario': forms.Select(attrs={'class': 'form-select'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['hora_inicio', 'hora_fin']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class PromocionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = ['codigo', 'descripcion', 'descuento_porcentaje', 'descuento_fijo', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'descuento_porcentaje': forms.NumberInput(attrs={'class': 'form-control'}),
            'descuento_fijo': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'fecha',
            'subtotal',
            'descuento',
            'total',
            'estado',
            'cancha',
            'usuario',
            'promocion',
            'horario',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'cancha': forms.Select(attrs={'class': 'form-control'}),
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'promocion': forms.Select(attrs={'class': 'form-control'}),
            'horario': forms.Select(attrs={'class': 'form-control'}),
        }

class EquipamientoForm(forms.ModelForm):
    tipos_cancha = forms.ModelMultipleChoiceField(
        queryset=TipoCancha.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Equipamiento
        fields = ['nombre', 'stock', 'precio', 'tipos_cancha']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
        }