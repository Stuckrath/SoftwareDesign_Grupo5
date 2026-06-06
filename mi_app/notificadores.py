from abc import ABC, abstractmethod

# <<interface>> INotificador
class INotificador(ABC):
    @abstractmethod
    def enviarAlerta(self, dest, mensaje):
        pass

# --- ADAPTADORES CONCRETOS (PROTOTIPOS) ---

class EmailAdapter(INotificador):
    def __init__(self):
        self.client = "SendGridSDK (Simulado)"

    def enviarAlerta(self, dest, mensaje):
        # Prototipo: Simulamos el envío imprimiendo en la consola de Django
        print("\n" + "="*50)
        print(f"[SERVICIO CORREO - {self.client}]")
        print(f"Para: {dest}")
        print(f"Contenido: {mensaje}")
        print("="*50 + "\n")
        return True


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