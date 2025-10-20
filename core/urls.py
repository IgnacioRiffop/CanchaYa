from django.urls import path
from . import views

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
    path('perfil/', views.perfil, name='perfil'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('reserva/', views.reserva, name='reserva'),
    path('comprobante/', views.comprobante, name='comprobante'),
    path('cuenta/', views.cuenta, name='cuenta'),
    path('modificarCuenta/', views.modificarCuenta, name='modificarCuenta'),
    path('historialReserva/', views.historialReserva, name='historialReserva'),
    path('detalleReserva/', views.detalleReserva, name='detalleReserva'),
]
