from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings

# <<interface>> INotificador
class INotificador(ABC):
    @abstractmethod
    def enviarAlerta(self, dest, mensaje):
        pass

# --- ADAPTADORES CONCRETOS (PROTOTIPOS) ---

'''class EmailAdapter(INotificador):
    def __init__(self):
        self.client = "SendGridSDK (Simulado)"

    def enviarAlerta(self, dest, mensaje):
        # Prototipo: Simulamos el envío imprimiendo en la consola de Django
        print("\n" + "="*50)
        print(f"[SERVICIO CORREO - {self.client}]")
        print(f"Para: {dest}")
        print(f"Contenido: {mensaje}")
        print("="*50 + "\n")
        return True '''
    
class EmailAdapter(INotificador):
    def enviarAlerta(self, destinatario, mensaje):
        asunto = 'Confirmación de Cita - Sistema de Vacunación'
        correo_origen = settings.EMAIL_HOST_USER
        
        try:
            # función  que interactúa con el servidor SMTP
            send_mail(
                asunto,
                mensaje,
                correo_origen,
                [destinatario],
                fail_silently=False,
            )
            print(f"Éxito: Correo enviado a {destinatario}")
        except Exception as e:
            print(f"Error al enviar el correo a {destinatario}: {e}")


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