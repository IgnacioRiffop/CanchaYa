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
from .forms import CanchaForm
from .models import *
from django.core.paginator import Paginator
from datetime import time
from datetime import date, timedelta
from datetime import datetime
import json
import stripe
from django.conf import settings


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
            
            # Obtener el objeto Usuario de tu tabla Oracle
            try:
                usuario = Usuario.objects.get(email=user.email)
                request.session['usuario_id'] = usuario.id_usuario
            except Usuario.DoesNotExist:
                messages.error(request, "No se encontró tu usuario en la base de datos interna.")
                return redirect('index')

            messages.success(request, f'¡Bienvenido {user.username}! Has iniciado sesión correctamente.')
            return redirect('index')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
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


# core/views.py
from django.http import JsonResponse
from django.db.models import Sum

def api_stock_equipamientos(request):
    fecha_str = request.GET.get('fecha')
    horario_id = request.GET.get('horario_id')

    if not fecha_str or not horario_id:
        return JsonResponse({'error': 'Faltan parámetros (fecha o horario_id).'}, status=400)

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido (usar YYYY-MM-DD).'}, status=400)

    try:
        horario_id = int(horario_id)  # 🔹 convierte a entero para que el filtro funcione
    except ValueError:
        return JsonResponse({'error': 'ID de horario inválido.'}, status=400)

    equipamientos = Equipamiento.objects.all()
    data = []

    for eq in equipamientos:
        reservado = ReservaEquipamiento.objects.filter(
            reserva__fecha=fecha,
            reserva__horario_id=horario_id,
            reserva__estado='A',
            equipamiento=eq
        ).aggregate(total_reservado=Sum('cantidad'))['total_reservado'] or 0

        disponible = max(eq.stock - reservado, 0)

        data.append({
            'id': eq.id_equipamiento,
            'nombre': eq.nombre,
            'stock_total': eq.stock,
            'reservado': reservado,
            'disponible': disponible,
            'precio': eq.precio,
        })

    return JsonResponse({'equipamientos': data})


def reserva(request, id_cancha):
    cancha = get_object_or_404(Cancha, pk=id_cancha)
    equipamientos_disponibles = Equipamiento.objects.filter(tipos_cancha=cancha.tipo_cancha)

    # Fechas mínimas y máximas
    hoy = date.today()
    fecha_max = hoy + timedelta(days=30)

    # Manejar selección de fecha
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha_seleccionada = hoy
    else:
        fecha_seleccionada = hoy

    # 🟩 Obtener horarios dentro del rango de la cancha
    horarios_qs = Horario.objects.filter(
        hora_inicio__gte=cancha.hora_inicio,
        hora_fin__lte=cancha.hora_fin
    ).order_by('hora_inicio')

    # 🟢 Incluir el precio real (según Tarifa o el precio base)
    horarios_disponibles = []
    for h in horarios_qs:
        tarifa = Tarifa.objects.filter(cancha=cancha, horario=h).first()
        precio_final = tarifa.precio if tarifa else cancha.precio

        horarios_disponibles.append({
            "id_horario": h.id_horario,
            "hora_inicio": h.hora_inicio.strftime("%H:%M"),
            "hora_fin": h.hora_fin.strftime("%H:%M"),
            "precio": precio_final,  # 🔹 precio por horario
        })

    # 🟩 Obtener horarios ocupados para la fecha seleccionada (solo IDs)
    reservas_ocupadas = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha_seleccionada,
        estado='A'
    ).values_list('horario_id', flat=True)

    horarios_ocupados = list(reservas_ocupadas)

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



def comprobante(request):
    return render(request, 'core/comprobante.html')

def cuenta(request):
    return render(request, 'core/cuenta.html')

def modificarCuenta(request):
    return render(request, 'core/modificarCuenta.html')


def historialReserva(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para ver tus reservas.")
        return redirect('login')

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    reservas_list = (
        Reserva.objects
        .filter(usuario=usuario)
        .select_related('cancha', 'horario', 'promocion')
        .prefetch_related('reservaequipamiento_set__equipamiento')
        .order_by('-fecha', '-horario__hora_inicio')
    )

    # 🔹 Paginación igual que en canchas (5 por página)
    paginator = Paginator(reservas_list, 5)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)

    return render(request, 'core/historialReserva.html', {'reservas': reservas})

def detalleReserva(request, id_reserva):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para ver el detalle de tu reserva.")
        return redirect('login')

    reserva = get_object_or_404(
        Reserva.objects
        .select_related('cancha', 'horario', 'promocion')
        .prefetch_related('reservaequipamiento_set__equipamiento'),
        id_reserva=id_reserva,
        usuario_id=usuario_id
    )

    return render(request, 'core/detalleReserva.html', {'reserva': reserva})


def validar_promocion(request, codigo):
    try:
        promo = Promocion.objects.get(codigo__iexact=codigo, activo=True)
        return JsonResponse({
            'id': promo.id_promocion,
            'codigo': promo.codigo,
            'descuento_porcentaje': promo.descuento_porcentaje,
            'descuento_fijo': float(promo.descuento_fijo),
        })
    except Promocion.DoesNotExist:
        return JsonResponse({'error': 'Código de promoción inválido'}, status=404)
    
def api_horarios_ocupados(request):
    cancha_id = request.GET.get('cancha_id')
    fecha_str = request.GET.get('fecha')

    # 🟥 Validar parámetros obligatorios
    if not cancha_id or not fecha_str:
        return JsonResponse({'error': 'Faltan parámetros (cancha_id o fecha).'}, status=400)

    # 🟩 Validar formato de fecha
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido (usar YYYY-MM-DD).'}, status=400)

    # 🟨 Verificar existencia de cancha
    try:
        cancha = Cancha.objects.get(id_cancha=cancha_id)
    except Cancha.DoesNotExist:
        return JsonResponse({'error': 'La cancha no existe.'}, status=404)

    # 🟩 Obtener horarios dentro del rango de la cancha
    horarios_qs = Horario.objects.filter(
        hora_inicio__gte=cancha.hora_inicio,
        hora_fin__lte=cancha.hora_fin
    ).order_by('hora_inicio')

    # 🟩 Construir lista de horarios con precio (tarifa o base)
    horarios_disponibles = []
    for h in horarios_qs:
        tarifa = Tarifa.objects.filter(cancha=cancha, horario=h).first()
        precio_final = tarifa.precio if tarifa else cancha.precio

        horarios_disponibles.append({
            "id_horario": h.id_horario,
            "hora_inicio": h.hora_inicio.strftime("%H:%M"),
            "hora_fin": h.hora_fin.strftime("%H:%M"),
            "precio": precio_final  # 🔹 nuevo campo agregado
        })

    # 🟩 Obtener horarios ocupados (solo IDs)
    horarios_ocupados = list(
        Reserva.objects.filter(
            cancha=cancha,
            fecha=fecha,
            estado='A'
        ).values_list('horario_id', flat=True)
    )

    # 🟩 Retornar respuesta JSON
    return JsonResponse({
        'horarios_disponibles': horarios_disponibles,
        'horarios_ocupados': horarios_ocupados
    })


stripe.api_key = settings.STRIPE_SECRET_KEY
from decimal import Decimal

def crear_checkout(request):
    if request.method != "POST":
        return redirect('index')

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para reservar.")
        return redirect('login')

    cancha_id = request.POST.get('cancha_id')
    fecha = request.POST.get('fecha')
    horario_id = request.POST.get('horario_id')
    equipamientos_json = request.POST.get('equipamientos', '{}')
    codigo_promocion = request.POST.get('codigo_promocion', '').strip()

    # Validaciones básicas mínimas
    if not (cancha_id and fecha and horario_id):
        messages.error(request, "Faltan datos de la reserva.")
        return redirect('index')

    cancha = get_object_or_404(Cancha, id_cancha=cancha_id)
    horario = get_object_or_404(Horario, id_horario=horario_id)

    # -------- Recalcular montos en backend (tarifa por horario + equipamientos + promo) --------
    # Precio base según tarifa si existe; si no, precio de la cancha
    tarifa = Tarifa.objects.filter(cancha=cancha, horario=horario).first()
    precio_base = tarifa.precio if tarifa else cancha.precio

    # Equipamientos
    subtotal = int(precio_base)
    try:
        equipamientos = json.loads(equipamientos_json) if equipamientos_json else {}
    except json.JSONDecodeError:
        equipamientos = {}

    for equip_id, cantidad in equipamientos.items():
        try:
            cantidad_int = int(cantidad or 0)
        except (TypeError, ValueError):
            cantidad_int = 0
        if cantidad_int > 0:
            equip = get_object_or_404(Equipamiento, id_equipamiento=equip_id)
            subtotal += int(equip.precio) * cantidad_int

    # Promoción
    descuento = 0
    promo = None
    if codigo_promocion:
        try:
            promo = Promocion.objects.get(codigo__iexact=codigo_promocion, activo=True)
            if promo.descuento_porcentaje:
                descuento = int(subtotal * promo.descuento_porcentaje / 100)
            elif promo.descuento_fijo:
                descuento = int(promo.descuento_fijo)
            if descuento > subtotal:
                descuento = subtotal
        except Promocion.DoesNotExist:
            descuento = 0
            promo = None

    total = subtotal - descuento

    if total <= 0:
        messages.error(request, "El total debe ser mayor que 0 para continuar con el pago.")
        return redirect('reserva', id_cancha=cancha_id)

    # Guardar datos (ya con montos recalculados en backend)
    request.session['reserva_temp'] = {
        'cancha_id': cancha_id,
        'fecha': fecha,
        'horario_id': horario_id,
        'equipamientos': json.dumps(equipamientos),
        'codigo_promocion': codigo_promocion,
        'subtotal': subtotal,
        'descuento': descuento,
        'total': total
    }

    # En CLP no hay decimales
    unit_amount = int(total)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'clp',
                    'product_data': {
                        'name': f'Reserva {cancha.nombre}',
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/pago_exitoso/',
            cancel_url='http://127.0.0.1:8000/pago_fallido/',
        )
        return redirect(session.url, code=303)

    except Exception as e:
        messages.error(request, f"Ocurrió un error al iniciar el pago: {e}")
        return redirect('reserva', id_cancha=cancha_id)


from django.db import transaction


def pago_exitoso(request):
    reserva_temp = request.session.get('reserva_temp')
    if not reserva_temp:
        messages.warning(request, "No se encontró información de la reserva pagada.")
        return redirect('index')

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para ver tu reserva.")
        return redirect('login')

    try:
        cancha_id = reserva_temp.get('cancha_id')
        fecha_str = reserva_temp.get('fecha')  # ⚙️ nombre cambiado solo para convertir correctamente
        horario_id = reserva_temp.get('horario_id')
        codigo_promocion = reserva_temp.get('codigo_promocion', '').strip()
        equipamientos_json = reserva_temp.get('equipamientos', '{}')

        # ✅ Convertir la fecha a tipo date (si viene como string)
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            fecha = date.today()

        cancha = get_object_or_404(Cancha, id_cancha=cancha_id)
        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
        horario = get_object_or_404(Horario, id_horario=horario_id)

        # Evitar doble reserva
        if Reserva.objects.filter(cancha=cancha, fecha=fecha, horario=horario, estado='A').exists():
            del request.session['reserva_temp']
            messages.error(request, "Este horario se reservó mientras completabas el pago.")
            return redirect('reserva', id_cancha=cancha_id)

        # -------- Recalcular montos con tarifa por horario (seguridad) --------
        tarifa = Tarifa.objects.filter(cancha=cancha, horario=horario).first()
        precio_base = tarifa.precio if tarifa else cancha.precio
        subtotal = int(precio_base)

        try:
            equipamientos = json.loads(equipamientos_json) if equipamientos_json else {}
        except json.JSONDecodeError:
            equipamientos = {}

        for equip_id, cantidad in equipamientos.items():
            try:
                cantidad_int = int(cantidad or 0)
            except (TypeError, ValueError):
                cantidad_int = 0
            if cantidad_int > 0:
                equip = get_object_or_404(Equipamiento, id_equipamiento=equip_id)
                subtotal += int(equip.precio) * cantidad_int

        descuento = 0
        promo = None
        if codigo_promocion:
            try:
                promo = Promocion.objects.get(codigo__iexact=codigo_promocion, activo=True)
                if promo.descuento_porcentaje:
                    descuento = int(subtotal * promo.descuento_porcentaje / 100)
                elif promo.descuento_fijo:
                    descuento = int(promo.descuento_fijo)
                if descuento > subtotal:
                    descuento = subtotal
            except Promocion.DoesNotExist:
                descuento = 0
                promo = None

        total = subtotal - descuento

        with transaction.atomic():
            reserva = Reserva.objects.create(
                fecha=fecha,
                subtotal=subtotal,
                descuento=descuento,
                total=total,
                estado='A',
                cancha=cancha,
                usuario=usuario,
                horario=horario,
                promocion=promo
            )

            for equip_id, cantidad in equipamientos.items():
                try:
                    cantidad_int = int(cantidad or 0)
                except (TypeError, ValueError):
                    cantidad_int = 0
                if cantidad_int > 0:
                    equip = get_object_or_404(Equipamiento, id_equipamiento=equip_id)
                    ReservaEquipamiento.objects.create(
                        reserva=reserva,
                        equipamiento=equip,
                        cantidad=cantidad_int
                    )

        del request.session['reserva_temp']

        # ✅ Enviar la fecha explícitamente al template (además de la reserva)
        return render(request, 'core/pago_exitoso.html', {
            'reserva': reserva,
            'fecha': fecha
        })

    except Exception as e:
        messages.error(request, f"Ocurrió un error al registrar la reserva: {str(e)}")
        return redirect('index')

def pago_fallido(request):
    return render(request, 'core/pago_fallido.html')


import requests

def obtener_clima(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    fecha = request.GET.get('fecha')

    if not lat or not lon:
        return JsonResponse({'error': 'Faltan coordenadas'}, status=400)

    API_KEY = '798b4f4d195871c9ca50aad795bd6420'
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=es"

    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if 'list' not in data:
            return JsonResponse({'error': 'Respuesta inválida de OpenWeather'}, status=500)

        fecha_reserva = datetime.strptime(fecha, "%Y-%m-%d").date()
        # Fecha máxima disponible en el pronóstico (último elemento)
        ultima_fecha = datetime.fromtimestamp(data['list'][-1]['dt']).date()

        # 🟡 Si la fecha excede el rango de 5 días, devolvemos un mensaje
        if fecha_reserva > ultima_fecha:
            return JsonResponse({
                'advertencia': 'Nuestro pronóstico está disponible solo dentro de los próximos 5 días.'
            })

        # Buscar el pronóstico más cercano al mediodía del día elegido
        pronostico = None
        for entry in data['list']:
            dt = datetime.fromtimestamp(entry['dt'])
            if dt.date() == fecha_reserva and dt.hour in [11, 12, 13]:
                pronostico = entry
                break

        # Si no se encontró exactamente al mediodía, tomamos el más cercano
        if not pronostico:
            pronostico = min(
                data['list'],
                key=lambda e: abs(datetime.fromtimestamp(e['dt']).date() - fecha_reserva)
            )

        clima = {
            'temperatura': pronostico['main']['temp'],
            'descripcion': pronostico['weather'][0]['description'].capitalize(),
            'icono': pronostico['weather'][0]['icon'],
        }
        return JsonResponse(clima)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def centroGestion(request):
    return render(request, 'core/centroGestion.html')

def gestionComercial(request):
    return render(request, 'core/gestionComercial.html')

def gestionCuentas(request):
    return render(request, 'core/gestionCuentas.html')

def crudOperadores(request):
    return render(request, 'core/crudOperadores.html')


def crudAdministradores(request):
    return render(request, 'core/crudAdministradores.html')


def crudUsuarios(request):
    return render(request, 'core/crudUsuarios.html')

def crudReservas(request):
    return render(request, 'core/crudReservas.html')

def crudEquipamientos(request):
    return render(request, 'core/crudEquipamientos.html')

def crudTarifas(request):
    return render(request, 'core/crudTarifas.html')

def crudPromociones(request):
    return render(request, 'core/crudPromociones.html')

def crudHorarios(request):
    return render(request, 'core/crudHorarios.html')

@login_required
def crudCanchas(request):
    # Reutilizamos tu nombre de vista, pero ahora enviamos datos reales
    canchas = Cancha.objects.select_related('tipo_cancha').order_by('id_cancha')
    return render(request, 'core/crudCanchas.html', {'canchas': canchas})

@login_required
def cancha_create(request):
    if request.method == 'POST':
        form = CanchaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cancha creada correctamente.')
            return redirect('crudCanchas')
        messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = CanchaForm()
    return render(request, 'core/canchas_form.html', {'form': form, 'modo': 'Agregar'})

@login_required
def cancha_edit(request, pk):
    cancha = get_object_or_404(Cancha, id_cancha=pk)
    if request.method == 'POST':
        form = CanchaForm(request.POST, request.FILES, instance=cancha)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cancha actualizada correctamente.')
            return redirect('crudCanchas')
        messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = CanchaForm(instance=cancha)
    return render(request, 'core/canchas_form.html', {'form': form, 'modo': 'Editar', 'cancha': cancha})

@login_required
def cancha_delete(request, pk):
    cancha = get_object_or_404(Cancha, id_cancha=pk)
    if request.method == 'POST':
        cancha.delete()
        messages.success(request, 'Cancha eliminada correctamente.')
        return redirect('crudCanchas')
    # Si llega por GET (p.ej. alguien pega la URL), vuelve a la lista
    return redirect('crudCanchas')