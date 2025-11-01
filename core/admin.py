from django.contrib import admin
from django.utils.html import format_html
from .models import Cancha, Usuario, Reserva, TipoCancha, Horario, Promocion, Equipamiento, ReservaEquipamiento

@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('id_cancha', 'nombre', 'tipo_cancha', 'imagen_preview', 'hora_inicio', 'hora_fin')
    readonly_fields = ('imagen_preview',)

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 100px; height:auto;" />', obj.imagen.url)
        return "Sin imagen"
    imagen_preview.short_description = 'Imagen'


admin.site.register(Usuario)
admin.site.register(Reserva)
admin.site.register(TipoCancha)
admin.site.register(Horario)
admin.site.register(Promocion)
admin.site.register(Equipamiento)
admin.site.register(ReservaEquipamiento)