from django.db import models

class TipoCancha(models.Model):
    id_tipo_cancha = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=150)

    class Meta:
        db_table = 'tipo_cancha'
        verbose_name = 'Tipo de Cancha'
        verbose_name_plural = 'Tipos de Cancha'

    def __str__(self):
        return self.nombre


class Cancha(models.Model):
    id_cancha = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=150)
    imagen = models.ImageField(upload_to='canchas/', blank=True, null=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    precio = models.PositiveIntegerField(null=True, blank=True)
    tipo_cancha = models.ForeignKey(TipoCancha, on_delete=models.CASCADE, db_column='tipo_cancha_id_tipo_cancha')

    class Meta:
        db_table = 'cancha'
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'

    def __str__(self):
        return self.nombre


class Equipamiento(models.Model):
    id_equipamiento = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    stock = models.PositiveIntegerField()
    precio = models.PositiveIntegerField(null=True, blank=True)

    # Relación ManyToMany con TipoCancha
    tipos_cancha = models.ManyToManyField(
        'TipoCancha',
        related_name='equipamientos',
        blank=True,
        db_table='equipamiento_tipo_cancha'  # tabla intermedia personalizada
    )

    class Meta:
        db_table = 'equipamiento'
        verbose_name = 'Equipamiento'
        verbose_name_plural = 'Equipamientos'

    def __str__(self):
        return self.nombre


class Horario(models.Model):
    id_horario = models.BigAutoField(primary_key=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        db_table = 'horario'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'

    def __str__(self):
        return f"{self.hora_inicio} - {self.hora_fin}"


class Promocion(models.Model):
    id_promocion = models.BigAutoField(primary_key=True)
    codigo = models.CharField(max_length=10, null=True, blank=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    descuento_porcentaje = models.PositiveIntegerField(default=0, null=True, blank=True)  # Ej: 10 -> 10%
    descuento_fijo = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)  # Ej: 50 -> $50
    activo = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        db_table = 'promocion'
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'

    def __str__(self):
        return self.codigo


class Usuario(models.Model):
    id_usuario = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(db_column='pass', max_length=100)

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Reserva(models.Model):
    id_reserva = models.BigAutoField(primary_key=True)
    fecha = models.DateField()
    subtotal = models.BigIntegerField()
    descuento = models.BigIntegerField(default=0)
    total = models.BigIntegerField()
    estado = models.CharField(max_length=1, choices=[('A', 'Activa'), ('C', 'Cancelada')])
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, db_column='cancha_id_cancha')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id_usuario')
    promocion = models.ForeignKey(Promocion, on_delete=models.SET_NULL, db_column='promocion_id_promocion', null=True, blank=True)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, db_column='horario_id_horario')

    class Meta:
        db_table = 'reserva'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.usuario}"


class ReservaEquipamiento(models.Model):
    equipamiento = models.ForeignKey(Equipamiento, on_delete=models.CASCADE, db_column='equipamiento_id_equipamiento')
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, db_column='reserva_id_reserva')
    cantidad = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'reserva_equipamiento'
        unique_together = (('equipamiento', 'reserva'),)
        verbose_name = 'Reserva de Equipamiento'
        verbose_name_plural = 'Reservas de Equipamiento'

    def __str__(self):
        return f"{self.reserva} - {self.equipamiento}"


class Tarifa(models.Model):
    id_tarifa = models.BigAutoField(primary_key=True)
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, db_column='cancha_id_cancha')
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, db_column='horario_id_horario')
    precio = models.PositiveIntegerField()

    class Meta:
        db_table = 'tarifa'
        unique_together = ('cancha', 'horario')
        verbose_name = 'Tarifa'
        verbose_name_plural = 'Tarifas'

    def __str__(self):
        return f"{self.cancha.nombre} | {self.horario} → ${self.precio}"
