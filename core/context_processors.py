from django.db import connections
from django.contrib.auth.decorators import login_required

def datos_usuario(request):
    """
    Recupera nombre y apellido del usuario autenticado desde la tabla USUARIO en Oracle.
    Usa la conexión directa (no ORM) para evitar inconsistencias con la base de datos por defecto.
    """
    if request.user.is_authenticated:
        email = request.user.email

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
                    nombre_completo = f"{nombre} {apellido}".strip()
                    return {'nombre_usuario': nombre_completo, 'email_usuario': email}
        except Exception as e:
            print(f"⚠️ [Context Processor Oracle] Error obteniendo usuario desde Oracle: {e}")

    # Valor por defecto si no está autenticado o no se encuentra
    return {'nombre_usuario': None, 'email_usuario': None}
