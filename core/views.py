from django.shortcuts import render, redirect
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


def index(request):
    return render(request,'core/index.html')

def contacto(request):
    return render(request, 'core/contacto.html')

def promociones(request):
    return render(request, 'core/promociones.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index(request):
    return render(request, 'core/index.html')

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
    

def canchas(request):
    return render(request, 'core/canchas.html')

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


def reserva(request):
    return render(request, 'core/reserva.html')

def comprobante(request):
    return render(request, 'core/comprobante.html')

def cuenta(request):
    return render(request, 'core/cuenta.html')

def modificarCuenta(request):
    return render(request, 'core/modificarCuenta.html')