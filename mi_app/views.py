import re
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Campana, PuntoVacunacion, Cita, Persona, TipoVacuna
from .reportes import ReporteCampanaBuilder, DirectorReportes
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# BPMN: "Accede a plataforma de agenda" (Punto de decisión inicial)
def mostrar_inicio(request):
    return render(request, 'mi_app/inicio.html')


# BPMN: Flujo "NO" -> "Ingresa sus datos de registro"
def registrar_usuario(request):
    if request.method == 'POST':
        # El Sistema de Manejo recibe la información
        rut_user = request.POST.get('rut')
        email = request.POST.get('correo')
        password = request.POST.get('password')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        telefono = request.POST.get('telefono')

        if rut_user:
            rut_user = rut_user.strip().upper()

        # Control de errores básico (Verifica validez conceptual)
        if not rut_user or not re.match(r'^[0-9]{7,8}[0-9K]$', rut_user):
            messages.error(request, "El RUT no sigue el formato correspondiente")
            return render(request, 'mi_app/registro.html')

        if User.objects.filter(username=rut_user).exists():
            messages.error(request, "El RUT ya está registrado.")
            return render(request, 'mi_app/registro.html')

        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, "Las contraseñas no coinciden. Por favor verifica e intenta de nuevo.")
            return render(request, 'mi_app/registro.html')

        # BPMN: "Recibe cuenta nueva y la almacena en BD" -> "Guarda cuenta en el sistema"
        # 1. Creamos el usuario de autenticación de Django
        nuevo_usuario = User.objects.create_user(username=rut_user, email=email, password=password)
        
        # 2. Creamos el perfil asociado en nuestra tabla Persona (UML)
        Persona.objects.create(
            rut=rut_user,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            correo=email,
            telefono=telefono
        )

        # BPMN: "Manda confirmación de almacenamiento correcto" -> "Envía confirmación de creación"
        messages.success(request, "Cuenta creada con éxito. Ahora puedes iniciar sesión.")
        return redirect('login')

    return render(request, 'mi_app/registro.html')


# BPMN: Flujo "SI" -> "Ingresa sus datos de login"
def iniciar_sesion(request):
    if request.method == 'POST':
        rut_user = request.POST.get('rut')
        password = request.POST.get('password')

        # BPMN: "Verifica validez de información" -> "Rescata información de loggeo de la cuenta"
        # Django busca internamente en la BD si el usuario existe y la contraseña coincide
        usuario = authenticate(request, username=rut_user, password=password)

        if usuario is not None:
            # BPMN: "Devuelve confirmación si la info coincide"
            login(request, usuario)
            # BPMN: "Entrega Token de acceso" (Django crea la cookie de sesión del navegador)
            return redirect('inicio') 
        else:
            # Si no coincide la información
            messages.error(request, "RUT o contraseña incorrectos.")
            return render(request, 'mi_app/login.html')

    return render(request, 'mi_app/login.html')

def cerrar_sesion(request):
    logout(request) # El sistema destruye el token de acceso/sesión en la BD
    return redirect('inicio') # BPMN: Redirige al inicio del diagrama

@login_required
def agendar_cita(request):
    
    # --- BLOQUE DE CARGA (GET) ---
    # BPMN: "Busca horarios, vacunas y lugares disponibles" -> "Rescata datos relacionados"
    campanas_disponibles = Campana.objects.all() 
    puntos_disponibles = PuntoVacunacion.objects.all()
    vacunas_disponibles = TipoVacuna.objects.all()

    if request.method == 'GET':
        # BPMN: "Entrega al usuario las selecciones disponibles"
        contexto = {
            'campanas': campanas_disponibles,
            'puntos': puntos_disponibles,
            'vacunas': vacunas_disponibles,
            'min_fecha_hora': timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        }
        return render(request, 'mi_app/agendar.html', contexto)


    # --- BLOQUE DE PROCESAMIENTO (POST) ---
    # BPMN: "Manda confirmación de opciones al sistema"
    if request.method == 'POST':
        campana_id = request.POST.get('campana')
        vacuna_id = request.POST.get('vacuna')
        punto_id = request.POST.get('punto')
        fecha_hora_str = request.POST.get('fecha_hora')

        try:
            fecha_hora_naive = datetime.fromisoformat(fecha_hora_str)
            fecha_hora = timezone.make_aware(fecha_hora_naive, timezone.get_current_timezone())
        except (TypeError, ValueError):
            messages.error(request, "La fecha y hora seleccionada no es válida.")
            contexto = {
                'campanas': campanas_disponibles,
                'puntos': puntos_disponibles,
                'vacunas': vacunas_disponibles,
                'min_fecha_hora': timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
            }
            return render(request, 'mi_app/agendar.html', contexto)

        fecha_actual = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
        if fecha_hora < fecha_actual:
            messages.error(request, "No se puede agendar una cita en una fecha anterior a la actual.")
            contexto = {
                'campanas': campanas_disponibles,
                'puntos': puntos_disponibles,
                'vacunas': vacunas_disponibles,
                'min_fecha_hora': timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
            }
            return render(request, 'mi_app/agendar.html', contexto)

        # Buscamos la Persona asociada al usuario logueado en la BD
        persona_paciente = Persona.objects.get(rut=request.user.username)

        # BPMN: "Almacena la reserva en la BD" -> "Guarda reserva del usuario en el sistema"
        nueva_cita = Cita.objects.create(
            fecha_hora=fecha_hora,
            estado='Agendada', # Estado inicial del flujo
            persona=persona_paciente,
            punto_vacunacion_id=int(punto_id),
            campana_id=int(campana_id),
            tipo_vacuna_id=int(vacuna_id)
        )

        # BPMN: "Envia confirmación al sistema" -> "Manda confirmación al usuario"
        # Le pasamos la cita creada a una pantalla de éxito para cerrar el flujo de extremo a extremo
        return render(request, 'mi_app/cita_exitosa.html', {'cita': nueva_cita})
    
@login_required
def ver_reporte(request, campana_id):
    campana = Campana.objects.get(pk=campana_id)

    tipo = request.GET.get('tipo', 'completo')  # ?tipo=stock | adherencia | completo

    builder  = ReporteCampanaBuilder()
    director = DirectorReportes(builder)

    if tipo == 'stock':
        reporte = director.reporte_stock(campana_id, campana.nombre)
    elif tipo == 'adherencia':
        reporte = director.reporte_adherencia(campana_id, campana.nombre)
    else:
        reporte = director.reporte_completo(campana_id, campana.nombre)

    return render(request, 'mi_app/reporte.html', {'reporte': reporte})

@login_required
def mis_citas(request):
    """
    BPMN: "Usuario consulta sus citas"
    Muestra todas las citas del usuario logueado organizadas por fecha.
    """
    persona = Persona.objects.get(rut=request.user.username)
    citas = persona.citas.all().order_by('-fecha_hora')
    
    contexto = {
        'citas': citas
    }
    return render(request, 'mi_app/mis_citas.html', contexto)


@login_required
def cancelar_cita(request, cita_id):
    """
    BPMN: "Usuario solicita cancelación de cita" -> "Sistema verifica y cancela"
    Cancela una cita del usuario logueado.
    Solo permite cancelar citas en estado 'Agendada'.
    """
    try:
        cita = Cita.objects.get(id_cita=cita_id)
        
        # Verificar que la cita pertenece al usuario logueado
        persona = Persona.objects.get(rut=request.user.username)
        if cita.persona != persona:
            messages.error(request, "No tienes permiso para cancelar esta cita.")
            return redirect('mis_citas')
        
        # Validar que solo se puedan cancelar citas en estado 'Agendada'
        if cita.estado != 'Agendada':
            messages.error(request, f"No se puede cancelar una cita en estado '{cita.estado}'.")
            return redirect('mis_citas')
        
        # BPMN: "Sistema procesa cancelación" -> Usa el patrón State
        cita.cancelar()
        
        # BPMN: "Envía confirmación de cancelación"
        messages.success(
            request, 
            f"Cita del {cita.fecha_hora.strftime('%d/%m/%Y a las %H:%M')} cancelada exitosamente."
        )
        return redirect('mis_citas')
        
    except Cita.DoesNotExist:
        messages.error(request, "La cita no existe.")
        return redirect('mis_citas')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('mis_citas')