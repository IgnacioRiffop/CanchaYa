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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cancha = None
        fecha = None

        # 🟢 Si estamos EDITANDO, usamos los datos de la reserva
        if self.instance and self.instance.pk:
            cancha = self.instance.cancha
            fecha = self.instance.fecha

        # 🟡 Si es POST (por ejemplo, al fallar validación), intentamos leer de self.data
        if not cancha:
            cancha_id = self.data.get('cancha') or self.initial.get('cancha')
            if cancha_id:
                try:
                    cancha = Cancha.objects.get(pk=cancha_id)
                except Cancha.DoesNotExist:
                    cancha = None

        if not fecha:
            fecha_str = self.data.get('fecha') or self.initial.get('fecha')
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                except ValueError:
                    fecha = None

        # ✅ Si tenemos cancha y fecha, filtramos horarios DISPONIBLES
        if cancha and fecha:
            reservas_qs = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
                estado='A'
            )

            # Si estamos editando, NO contamos nuestra propia reserva como choque
            if self.instance and self.instance.pk:
                reservas_qs = reservas_qs.exclude(pk=self.instance.pk)

            horarios_ocupados = reservas_qs.values_list('horario_id', flat=True)

            # 🔥 En el combo de 'horario' solo mostramos los libres
            self.fields['horario'].queryset = Horario.objects.exclude(
                id_horario__in=horarios_ocupados
            )

    def clean(self):
        cleaned = super().clean()

        cancha = cleaned.get('cancha')
        fecha = cleaned.get('fecha')
        horario = cleaned.get('horario')
        estado = cleaned.get('estado')  # por si usas 'A' / 'C'

        # Doble seguridad: si se deja ACTIVA, no permitir choques
        if cancha and fecha and horario and estado == 'A':
            qs = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
                horario=horario,
                estado='A'
            )
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error(
                    'horario',
                    'Ya existe una reserva activa para esta cancha, fecha y horario.'
                )

        return cleaned


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🟢 SOLO AL EDITAR (cuando la reserva ya existe)
        if self.instance and self.instance.pk and self.instance.cancha_id and self.instance.fecha:
            cancha = self.instance.cancha
            fecha = self.instance.fecha

            # Horarios ya ocupados por otras reservas ACTIVAS en esa cancha/fecha
            horarios_ocupados = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
                estado='A'
            ).exclude(pk=self.instance.pk).values_list('horario_id', flat=True)

            # En el select de "horario" mostramos:
            #  - el horario actual de la reserva
            #  - + todos los horarios libres
            self.fields['horario'].queryset = Horario.objects.exclude(
                id_horario__in=horarios_ocupados
            )

    def clean(self):
        cleaned = super().clean()

        cancha = cleaned.get('cancha')
        fecha = cleaned.get('fecha')
        horario = cleaned.get('horario')
        estado = cleaned.get('estado')  # 'A' / 'C'

        # 🛑 Validar solo si se deja la reserva ACTIVA
        if cancha and fecha and horario and estado == 'A':
            qs = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
                horario=horario,
                estado='A'
            )

            # Si estamos editando, nos excluimos a nosotros mismos
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error(
                    'horario',
                    'Ya existe una reserva activa para esta cancha, fecha y horario.'
                )

        return cleaned


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