from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('id_cancha', 'nombre', 'tipo_cancha', 'precio', 'imagen_preview', 'hora_inicio', 'hora_fin')
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
@admin.register(Equipamiento)

class EquipamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock', 'precio', 'mostrar_tipos')
    list_filter = ('tipos_cancha',)
    search_fields = ('nombre',)
    filter_horizontal = ('tipos_cancha',)

    def mostrar_tipos(self, obj):
        return ", ".join([t.nombre for t in obj.tipos_cancha.all()])
    mostrar_tipos.short_description = 'Tipos de Cancha'


admin.site.register(ReservaEquipamiento)