from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Campana, PuntoVacunacion, Cita, Persona, TipoVacuna
from .reportes import ReporteCampanaBuilder, DirectorReportes
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .notificadores import EmailAdapter
from django.utils.dateparse import parse_datetime

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

        # Control de errores básico (Verifica validez conceptual)
        if User.objects.filter(username=rut_user).exists():
            messages.error(request, "El RUT ya está registrado.")
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
            'vacunas': vacunas_disponibles

        }
        return render(request, 'mi_app/agendar.html', contexto)


    # --- BLOQUE DE PROCESAMIENTO (POST) ---
    # BPMN: "Manda confirmación de opciones al sistema"
    if request.method == 'POST':
        campana_id = request.POST.get('campana')
        vacuna_id = request.POST.get('vacuna')
        punto_id = request.POST.get('punto')
        fecha_hora = request.POST.get('fecha_hora')

        # Buscamos la Persona asociada al usuario logueado en la BD
        persona_paciente = Persona.objects.get(rut=request.user.username)

        # Obtener las instancias completas
        campana_instancia = Campana.objects.get(pk=campana_id)
        punto_instancia = PuntoVacunacion.objects.get(pk=punto_id)
        vacuna_instancia = TipoVacuna.objects.get(pk=vacuna_id)

        # Convertir el texto del formulario a un objeto datetime de Python
        fecha_hora_obj = parse_datetime(fecha_hora)

        # Instanciar la cita usando la fecha ya convertida
        nueva_cita = Cita(
            fecha_hora=fecha_hora_obj,  # Se usa la variable convertida
            persona=persona_paciente,
            punto_vacunacion=punto_instancia,
            campana=campana_instancia,
            tipo_vacuna=vacuna_instancia
        )

        try:
            # Delegar la acción al Patrón State
            nueva_cita.agendar() 
            
            return render(request, 'mi_app/cita_exitosa.html', {'cita': nueva_cita})
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('agendar')

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