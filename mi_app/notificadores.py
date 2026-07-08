from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings

# <<interface>> INotificador
class INotificador(ABC):
    @abstractmethod
    def enviarAlerta(self, dest, mensaje):
        pass

# --- ADAPTADORES CONCRETOS (PROTOTIPOS) ---

# Adaptador Concreto para Correo Electrónico Real
class EmailAdapter(INotificador):
    def enviarAlerta(self, destinatario, mensaje):
        """
        Envía un correo electrónico real utilizando la infraestructura SMTP configurada.
        """
        try:
            send_mail(
                subject='Confirmación de Reserva - Sistema de Vacunación',
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinatario],
                fail_silently=False, # Si falla, arrojará una excepción para capturarla en el log
            )
            print(f"[NOTIFICACIÓN] Correo real enviado exitosamente a: {destinatario}")
            return True
        except Exception as e:
            # Captura el error en la terminal por si las credenciales fallan, sin romper la app
            print(f"[ERROR ADAPTER] Falló el envío de correo real a {destinatario}: {e}")
            return False


class SMSAdapter(INotificador):
    def __init__(self):
        # self.client = TwilioSDK()
        self.client = "TwilioSDK (Simulado)"

    def enviarAlerta(self, dest, mensaje):
        print("\n" + "="*50)
        print(f"[SERVICIO SMS - {self.client}]")
        print(f"Para Celular: {dest}")
        print(f"Mensaje: {mensaje}")
        print("="*50 + "\n")
        return True


class WhatsappAdapter(INotificador):
    def __init__(self):
        # self.client = MetaWS_SDK()
        self.client = "MetaWS_SDK (Simulado)"

    def enviarAlerta(self, dest, mensaje):
        print("\n" + "="*50)
        print(f"[SERVICIO WHATSAPP - {self.client}]")
        print(f"Para Número: {dest}")
        print(f"Texto: {mensaje}")
        print("="*50 + "\n")
        return True