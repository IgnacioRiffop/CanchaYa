from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.db import transaction
from core.models import Usuario
from django.http import JsonResponse
import re
from .models import *
from django.core.paginator import Paginator
from datetime import time
from datetime import date, timedelta
from datetime import datetime
import json


def contacto(request):
    return render(request, 'core/contacto.html')

def promociones(request):
    return render(request, 'core/promociones.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index(request):
    canchas = Cancha.objects.all()[:2]  # solo las primeras 2
    return render(request,'core/index.html', {'canchas': canchas})

def contacto(request):
    return render(request, 'core/contacto.html')

def promociones(request):
    return render(request, 'core/promociones.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Has iniciado sesión correctamente.')
            return redirect('index')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return redirect('index')

    return redirect('index')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('index')




def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        print("🟢 [DEBUG] POST recibido en /registro/")
        print(f"👉 Nombre: {nombre}")
        print(f"👉 Apellido: {apellido}")
        print(f"👉 Email: {email}")

        # Validaciones básicas
        if not nombre or not apellido or not email or not password:
            print("⚠️ Faltan campos obligatorios.")
            messages.error(request, 'Por favor completa todos los campos.')
            return redirect('registro')

        # Validar duplicados
        if User.objects.filter(username=email).exists() or Usuario.objects.filter(email=email).exists():
            print("⚠️ El correo ya existe.")
            messages.error(request, 'Ya existe una cuenta registrada con este correo.')
            return redirect('registro')

        try:
            with transaction.atomic():
                print("🚀 Creando usuario en Django auth_user...")
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=nombre,
                    last_name=apellido
                )
                user.save()
                print("✅ auth_user creado.")

                # Generar ID manual
                next_id = 1
                ultimo = Usuario.objects.all().order_by('-id_usuario').first()
                if ultimo:
                    next_id = ultimo.id_usuario + 1

                print(f"🧮 Próximo ID asignado: {next_id}")

                Usuario.objects.create(
                    id_usuario=next_id,
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    password=make_password(password)
                )
                print("✅ Registro insertado correctamente en tabla USUARIO.")

            messages.success(request, 'Cuenta creada exitosamente. ¡Ya puedes iniciar sesión!')
            print("🎉 [ÉXITO] Usuario creado en ambas tablas correctamente.")
            return redirect('index')

        except Exception as e:
            print("❌ [ERROR] Falló el registro del usuario.")
            print(f"📄 Detalle: {str(e)}")
            messages.error(request, f'Ocurrió un error al registrar: {str(e)}')
            return redirect('registro')

    else:
        print("ℹ️ Carga inicial del formulario de registro.")
    return render(request, 'core/registro.html')

def olvide_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        print(f"📩 [DEBUG] Solicitud de recuperación recibida para: {email}")

        # Validar si existe el correo
        if not email:
            print("⚠️ [WARN] No se ingresó correo.")
            messages.error(request, "Por favor ingresa tu correo electrónico.")
            return redirect('index')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print("❌ [ERROR] No existe usuario con ese correo.")
            messages.error(request, "No existe una cuenta registrada con ese correo.")
            return redirect('index')

        # Generar token seguro y UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = request.build_absolute_uri(f"/restablecer/{uid}/{token}/")

        # Enviar correo
        asunto = "Restablece tu contraseña - CanchaYa"
        mensaje = f"""
Hola {user.first_name or 'usuario'},

Has solicitado restablecer tu contraseña en CanchaYa ⚽.
Haz clic en el siguiente enlace para crear una nueva contraseña:

{link}

Si no solicitaste esto, ignora este mensaje.

Atentamente,
El equipo de CanchaYa 💚
"""

        try:
            send_mail(
                asunto,
                mensaje,
                'canchasya.duoc@gmail.com',  # tu cuenta emisora
                [email],
                fail_silently=False,
            )
            print(f"✅ [INFO] Enlace de recuperación enviado a {email}")
            messages.success(request, "Te enviamos un enlace para restablecer tu contraseña.")
        except Exception as e:
            print(f"❌ [ERROR] No se pudo enviar el correo: {e}")
            messages.error(request, "Hubo un problema al enviar el correo. Intenta nuevamente más tarde.")

        return redirect('index')

    return redirect('index')

def restablecer_contrasena(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        print("❌ [ERROR] Token o usuario inválido.")
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        print(f"🟢 [INFO] Enlace válido para {user.email}")

        # 🔹 Si el usuario envía nueva contraseña
        if request.method == 'POST':
            nueva = request.POST.get('password')
            confirmar = request.POST.get('confirmar')

            if not nueva or not confirmar:
                messages.error(request, "Debes ingresar ambas contraseñas.")
                return redirect(request.path)

            if nueva != confirmar:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect(request.path)

            try:
                with transaction.atomic():
                    # Actualizar contraseña en Django (auth_user)
                    user.set_password(nueva)
                    user.save()

                    # Actualizar también en tabla Oracle 'usuario'
                    Usuario.objects.filter(email=user.email).update(password=make_password(nueva))
                    print(f"🔒 [OK] Contraseña actualizada para {user.email}")

                messages.success(request, "Tu contraseña fue restablecida exitosamente.")
                return redirect('index')

            except Exception as e:
                print(f"❌ [ERROR] Al actualizar contraseña: {e}")
                messages.error(request, "Ocurrió un error al actualizar tu contraseña.")
                return redirect('index')

        # 🔹 Si solo abre el enlace (GET)
        print("📩 [INFO] Mostrando modal de restablecer contraseña...")
        return render(request, 'core/index.html', {'abrir_reset': True, 'uid': uidb64, 'token': token})

    else:
        print("❌ [ERROR] Enlace expirado o inválido.")
        messages.error(request, "El enlace de recuperación no es válido o ha expirado.")
        return redirect('index')
    

# views.py
def canchas(request):
    canchas_list = Cancha.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    precio = request.GET.get('precio')
    hora = request.GET.get('hora')

    if tipo:
        canchas_list = canchas_list.filter(tipo_cancha__nombre__icontains=tipo)

    if precio:
        try:
            precio_max = int(precio)
            canchas_list = canchas_list.filter(precio__lte=precio_max)
        except ValueError:
            pass

    if hora:
        # Filtra canchas cuya hora_inicio <= hora <= hora_fin
        from datetime import time
        h, m = map(int, hora.split(':'))
        hora_obj = time(h, m)
        canchas_list = canchas_list.filter(hora_inicio__lte=hora_obj, hora_fin__gte=hora_obj)

    # Paginación
    paginator = Paginator(canchas_list, 5)
    page_number = request.GET.get('page')
    canchas = paginator.get_page(page_number)

    # Para select de filtros
    tipos = TipoCancha.objects.all()
    horas = [f"{h:02d}:00" for h in range(8, 24)]  # 08:00 a 23:00

    return render(request, 'core/canchas.html', {
        'canchas': canchas,
        'tipos': tipos,
        'horas': horas,
    })



from django.contrib.auth.decorators import login_required
from django.db import connections

@login_required
def perfil(request):
    email = request.user.email
    nombre = None
    apellido = None

    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("""
                SELECT NOMBRE, APELLIDO
                FROM USUARIO
                WHERE EMAIL = :email
            """, {'email': email})
            row = cursor.fetchone()
            if row:
                nombre, apellido = row
    except Exception as e:
        print(f"⚠️ [Perfil] Error obteniendo datos de Oracle: {e}")

    context = {
        'nombre': nombre,
        'apellido_usuario': apellido,
        'email_usuario': email,
    }
    return render(request, 'core/perfil.html', context)


@login_required
def editar_perfil(request):
    """
    Permite actualizar nombre y apellido del usuario logueado en Oracle.
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.user.email

        # 🧩 Validaciones backend
        if len(nombre) < 3 or len(apellido) < 3:
            return JsonResponse({'ok': False, 'msg': 'El nombre y apellido deben tener al menos 3 caracteres.'})

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$', nombre) or not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$', apellido):
            return JsonResponse({'ok': False, 'msg': 'Solo se permiten letras en los campos.'})

        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("""
                    UPDATE USUARIO
                    SET NOMBRE = :nombre, APELLIDO = :apellido
                    WHERE EMAIL = :email
                """, {'nombre': nombre, 'apellido': apellido, 'email': email})
            
            # También sincroniza con el modelo auth_user de Django
            request.user.first_name = nombre
            request.user.last_name = apellido
            request.user.save()

            return JsonResponse({'ok': True, 'msg': 'Datos actualizados correctamente.'})
        except Exception as e:
            print(f"❌ [ERROR] Falló la actualización del perfil: {e}")
            return JsonResponse({'ok': False, 'msg': 'Ocurrió un error al actualizar los datos.'})

    return JsonResponse({'ok': False, 'msg': 'Método inválido.'})



def reserva(request, id_cancha):
    cancha = get_object_or_404(Cancha, pk=id_cancha)
    equipamientos_disponibles = Equipamiento.objects.filter(tipos_cancha=cancha.tipo_cancha)

    # Filtrar horarios dentro del rango de la cancha
    horarios_disponibles = Horario.objects.filter(
        hora_inicio__gte=cancha.hora_inicio,
        hora_fin__lte=cancha.hora_fin
    ).order_by('hora_inicio')

    # Fechas mínimas y máximas
    hoy = date.today()
    fecha_max = hoy + timedelta(days=30)

    # Manejar selección de fecha
    fecha_seleccionada = request.GET.get('fecha')
    if fecha_seleccionada:
        # Convertir string a date
        fecha_seleccionada = datetime.strptime(fecha_seleccionada, "%Y-%m-%d").date()
    else:
        fecha_seleccionada = hoy

    horarios_ocupados = []
    if fecha_seleccionada:
        reservas = Reserva.objects.filter(
            cancha=cancha,
            fecha=fecha_seleccionada
        )
        horarios_ocupados = reservas.values_list('horario_id', flat=True)

    context = {
        'cancha': cancha,
        'horarios_disponibles': horarios_disponibles,
        'horarios_ocupados': horarios_ocupados,
        'fecha_actual': hoy,
        'fecha_max': fecha_max,
        'fecha_seleccionada': fecha_seleccionada,
        'equipamientos_disponibles': equipamientos_disponibles,
    }

    return render(request, 'core/reserva.html', context)



def confirmar_reserva(request):
    if request.method == "POST":
        cancha_id = request.POST.get('cancha_id')
        fecha = request.POST.get('fecha')
        horario_id = request.POST.get('horario_id')
        usuario_id = request.user.id
        equipamientos_json = request.POST.get('equipamientos', '{}')

        if not horario_id:
            messages.error(request, "Debes seleccionar un horario.")
            return redirect('reserva', id_cancha=cancha_id)

        cancha = get_object_or_404(Cancha, id_cancha=cancha_id)
        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
        horario = get_object_or_404(Horario, id_horario=horario_id)

        # Verificar disponibilidad
        if Reserva.objects.filter(cancha=cancha, fecha=fecha, horario=horario, estado='A').exists():
            messages.error(request, "Este horario ya está reservado. Por favor selecciona otro.")
            return redirect('reserva', id_cancha=cancha_id)

        # Calcular subtotal incluyendo equipamiento
        subtotal = cancha.precio
        try:
            equipamientos = json.loads(equipamientos_json)
            for equip_id, cantidad in equipamientos.items():
                if cantidad > 0:
                    equip = get_object_or_404(Equipamiento, id_equipamiento=equip_id)
                    subtotal += equip.precio * cantidad
        except json.JSONDecodeError:
            equipamientos = {}

        descuento = 0
        total = subtotal - descuento

        # Crear reserva
        reserva = Reserva.objects.create(
            fecha=fecha,
            subtotal=subtotal,
            descuento=descuento,
            total=total,
            estado='A',
            cancha=cancha,
            usuario=usuario,
            horario=horario
        )

        # Guardar equipamientos seleccionados
        for equip_id, cantidad in equipamientos.items():
            if cantidad > 0:
                equip = get_object_or_404(Equipamiento, id_equipamiento=equip_id)
                ReservaEquipamiento.objects.create(
                    reserva=reserva,
                    equipamiento=equip,
                    cantidad=cantidad
                )

        messages.success(request, f"Reserva realizada con éxito para {cancha.nombre} el {fecha} a las {horario.hora_inicio}.")
        return redirect('index')

    return redirect('index')



def comprobante(request):
    return render(request, 'core/comprobante.html')

def cuenta(request):
    return render(request, 'core/cuenta.html')

def modificarCuenta(request):
    return render(request, 'core/modificarCuenta.html')

def historialReserva(request):
    return render(request, 'core/historialReserva.html')

def detalleReserva(request):
    return render(request, 'core/detalleReserva.html')