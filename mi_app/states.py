from abc import ABC, abstractmethod
from django.contrib import messages

# <<interface>> EstadoCita
class EstadoCita(ABC):
    @abstractmethod
    def agendar(self, cita):
        pass

    @abstractmethod
    def reprogramar(self, cita, nueva_fecha):
        pass

    @abstractmethod
    def cancelar(self, cita):
        pass

    @abstractmethod
    def registrar_vacuna(self, cita):
        pass


class EstadoAgendada(EstadoCita):
    def agendar(self, cita):
        raise ValueError("La cita ya se encuentra agendada.")

    def reprogramar(self, cita, nueva_fecha):
        cita.fecha_hora = nueva_fecha
        # Se mantiene en el mismo estado, solo cambia la fecha
        cita.guardar_estado_str('Agendada') 

    def cancelar(self, cita):
        cita.guardar_estado_str('Cancelada')

    def registrar_vacuna(self, cita):
        cita.guardar_estado_str('Vacunado')


class EstadoCancelada(EstadoCita):
    def agendar(self, cita):
        raise ValueError("No se puede agendar una cita cancelada. Cree una nueva.")

    def reprogramar(self, cita, nueva_fecha):
        raise ValueError("No se puede reprogramar una cita que ya fue cancelada.")

    def cancelar(self, cita):
        raise ValueError("La cita ya se encuentra cancelada.")

    def registrar_vacuna(self, cita):
        raise ValueError("No se puede registrar una vacuna en una cita cancelada.")


class EstadoVacuna(EstadoCita):
    def agendar(self, cita):
        raise ValueError("El paciente ya fue vacunado en esta cita.")

    def reprogramar(self, cita, nueva_fecha):
        raise ValueError("No se puede reprogramar una cita de un paciente ya vacunado.")

    def cancelar(self, cita):
        raise ValueError("No se puede cancelar una cita si el paciente ya fue vacunado.")

    def registrar_vacuna(self, cita):
        raise ValueError("La vacuna ya fue registrada exitosamente.")