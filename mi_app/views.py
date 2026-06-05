from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Campana, PuntoVacunacion, Cita, Persona, TipoVacuna
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