from django.db import models
from .states import EstadoAgendada,EstadoCancelada,EstadoVacuna

class TipoVacuna(models.Model):
    id_vacuna = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    desc_tipo = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Campana(models.Model):
    id_campana = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    estado = models.CharField(max_length=50)
    tipos_vacuna = models.ManyToManyField(TipoVacuna, related_name="campanas", blank=True)

    def __str__(self):
        return self.nombre


class PuntoVacunacion(models.Model):
    id_punto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=100)
    direccion = models.CharField(max_length=250)
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    # Relación 1..* con Campaña (Un punto participa en campañas)
    campanas = models.ManyToManyField(Campana, related_name="puntos_vacunacion")

    def __str__(self):
        return self.nombre


class Almacenamiento(models.Model):
    punto_vacunacion = models.ForeignKey(PuntoVacunacion, on_delete=models.CASCADE, related_name="inventarios")
    tipo_vacuna = models.ForeignKey(TipoVacuna, on_delete=models.CASCADE)
    stock_disponible = models.IntegerField(default=0)
    stock_reservado = models.IntegerField(default=0)

    class Meta:
        # Evita que se repita la combinación de punto y tipo de vacuna
        unique_together = ('punto_vacunacion', 'tipo_vacuna')


class Personal(models.Model):
    id_trabajador = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100)
    punto_vacunacion = models.ForeignKey(PuntoVacunacion, on_delete=models.CASCADE, related_name="personal")

    def __str__(self):
        return self.nombre_completo


class Persona(models.Model):
    rut = models.CharField(max_length=12, primary_key=True)  
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Cita(models.Model):
    id_cita = models.AutoField(primary_key=True)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=50, default='Agendada') # Guarda el string en la BD
    persona = models.ForeignKey('Persona', on_delete=models.CASCADE, related_name="citas")
    punto_vacunacion = models.ForeignKey('PuntoVacunacion', on_delete=models.CASCADE)
    campana = models.ForeignKey('Campana', on_delete=models.CASCADE)
    tipo_vacuna = models.ForeignKey(TipoVacuna, on_delete=models.CASCADE, null=True, blank=True)

    # Diccionario para mapear el string de la BD a la clase del Patrón State
    _MAPA_ESTADOS = {
        'Agendada': EstadoAgendada,
        'Cancelada': EstadoCancelada,
        'Vacunado': EstadoVacuna, # O 'EstadoVacuna' según tu diagrama
    }

    @property
    def estado_actual(self):
        """Devuelve la instancia de la clase State correspondiente"""
        clase_state = self._MAPA_ESTADOS.get(self.estado, EstadoAgendada)
        return clase_state()

    def guardar_estado_str(self, nuevo_estado_str):
        """Método auxiliar para que los States actualicen el string en la BD"""
        self.estado = nuevo_estado_str
        self.save()

    # --- Métodos del diagrama delegados al Patrón State ---
    
    def agendar(self):
        self.estado_actual.agendar(self)

    def reprogramar(self, nueva_fecha):
        self.estado_actual.reprogramar(self, nueva_fecha)

    def cancelar(self):
        self.estado_actual.cancelar(self)

    def registrarVacuna(self):
        self.estado_actual.registrar_vacuna(self)

    def __str__(self):
        return f"Cita {self.id_cita} - {self.persona.rut} ({self.estado})"

class Vacunacion(models.Model):
    id_vacunacion = models.AutoField(primary_key=True)
    fecha_hora = models.DateTimeField()
    observaciones = models.TextField(blank=True, null=True)
    cita = models.OneToOneField(Cita, on_delete=models.PROTECT, blank=True, null=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="vacunaciones")
    personal = models.ForeignKey(Personal, on_delete=models.PROTECT)
    tipo_vacuna = models.ForeignKey(TipoVacuna, on_delete=models.PROTECT)

    def __str__(self):
        return f"Vacunación {self.id_vacunacion} - {self.persona.rut}"