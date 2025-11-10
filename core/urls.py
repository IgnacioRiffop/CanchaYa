from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.index, name='index'),
    path('contacto/', views.contacto, name='contacto'),
    path('promociones/', views.promociones, name='promociones'),
    path('registro/', views.registro, name='registro'),
    path('olvide_contrasena/', views.olvide_contrasena, name='olvide_contrasena'),
    path('restablecer/<uidb64>/<token>/', views.restablecer_contrasena, name='restablecer_contrasena'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('canchas/', views.canchas, name='canchas'),
    path('perfil/', login_required(views.perfil, login_url='login'), name='perfil'),
    path('editar_perfil/', login_required(views.editar_perfil, login_url='login'), name='editar_perfil'),
    path('reserva/<int:id_cancha>/', login_required(views.reserva, login_url='login'), name='reserva'),
    path('reserva/<int:id_reserva>/cancelar/', login_required(views.cancelar_reserva, login_url='login'), name='cancelar_reserva'),

    path('comprobante/', views.comprobante, name='comprobante'),
    path('cuenta/', login_required(views.cuenta, login_url='login'), name='cuenta'),
    path('modificarCuenta/', login_required(views.modificarCuenta, login_url='login'), name='modificarCuenta'),
    path('historialReserva/', login_required(views.historialReserva, login_url='login'), name='historialReserva'),
    path('detalleReserva/<int:id_reserva>/', login_required(views.detalleReserva, login_url='login'), name='detalleReserva'),
    path('api/promocion/<str:codigo>/', views.validar_promocion, name='validar_promocion'),
    path('api/horarios_ocupados/', login_required(views.api_horarios_ocupados, login_url='login'), name='api_horarios_ocupados'),
    path('api/stock_equipamientos/', views.api_stock_equipamientos, name='api_stock_equipamientos'),
    path('crear_checkout/', views.crear_checkout, name='crear_checkout'),
    path('pago_exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago_fallido/', views.pago_fallido, name='pago_fallido'),
    path('api/clima/', views.obtener_clima, name='obtener_clima'),
    path('reportes/ingresos/', views.reportes_ingresos, name='reportes_ingresos'),
    path('reportes/ingresos/exportar-excel/', views.exportar_ingresos_excel, name='exportar_ingresos_excel'),
    path('reportes/ingresos/exportar-pdf/', views.exportar_ingresos_pdf, name='exportar_ingresos_pdf'),
    path('reportes/ocupaciones/exportar-excel/', views.exportar_ocupaciones_excel, name='exportar_ocupaciones_excel'),
    path('reportes/ocupaciones/exportar-pdf/', views.exportar_ocupaciones_pdf, name='exportar_ocupaciones_pdf'),
    path('reportes/', views.centro_reportes, name='centro_reportes'),
    path('reportes/ocupaciones/', views.reportes_ocupaciones, name='reportes_ocupaciones'),
    path('centroGestion/', views.centroGestion, name='centroGestion'),
    path('gestionComercial/', views.gestionComercial, name='gestionComercial'),
    path('gestionCuentas/', views.gestionCuentas, name='gestionCuentas'),
    path('crudOperadores/', views.crudOperadores, name='crudOperadores'),
    path('crudAdministradores/', views.crudAdministradores, name='crudAdministradores'),
    path('crudUsuarios/', views.crudUsuarios, name='crudUsuarios'),
    path('usuarios/<int:id_usuario>/editar/', login_required(views.usuario_edit, login_url='login'), name='usuario_edit'),
    path('usuarios/<int:id_usuario>/eliminar/', login_required(views.usuario_delete, login_url='login'), name='usuario_delete'),

    path('crudCanchas/', views.crudCanchas, name='crudCanchas'),
    path('canchas/agregar/', views.cancha_create, name='cancha_add'),
    path('canchas/<int:pk>/editar/', views.cancha_edit, name='cancha_edit'),
    path('canchas/eliminar/<int:pk>/', views.cancha_delete, name='cancha_delete'),
    path('canchas/activar/<int:pk>/', views.cancha_activate, name='cancha_activate'),

    path('crudReservas/', views.crudReservas, name='crudReservas'),
    path('crudReservas/agregar/', views.reserva_create, name='reserva_add'),
    path('crudReservas/<int:pk>/editar/', views.reserva_edit, name='reserva_edit'),
    path('crudReservas/<int:pk>/eliminar/', views.reserva_delete, name='reserva_delete'),


    path('crudEquipamientos/', views.crudEquipamientos, name='crudEquipamientos'),
    path('crudEquipamientos/agregar/', views.equipamiento_create, name='equipamiento_add'),
    path('crudEquipamientos/<int:pk>/editar/', views.equipamiento_edit, name='equipamiento_edit'),
    path('crudEquipamientos/<int:pk>/eliminar/', views.equipamiento_delete, name='equipamiento_delete'),



    path('crudTarifas/', views.crudTarifas, name='crudTarifas'),
    path('crudTarifas/agregar/', views.tarifa_create, name='tarifa_add'),
    path('crudTarifas/<int:pk>/editar/', views.tarifa_edit, name='tarifa_edit'),
    path('crudTarifas/<int:pk>/eliminar/', views.tarifa_delete, name='tarifa_delete'),

    path('crudPromociones/', views.crudPromociones, name='crudPromociones'),
    path('crudPromociones/agregar/', views.promocion_create, name='promocion_add'),
    path('crudPromociones/<int:pk>/editar/', views.promocion_edit, name='promocion_edit'),
    path('crudPromociones/<int:pk>/eliminar/', views.promocion_delete, name='promocion_delete'),



    path('crudHorarios/', views.crudHorarios, name='crudHorarios'),
    path('horarios/agregar/', views.horario_create, name='horario_add'),
    path('horarios/<int:pk>/editar/', views.horario_edit, name='horario_edit'),
    path('horarios/<int:pk>/eliminar/', views.horario_delete, name='horario_delete'),

]
