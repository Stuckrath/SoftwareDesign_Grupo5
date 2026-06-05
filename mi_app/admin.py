from django.contrib import admin

from .models import Campana, TipoVacuna, PuntoVacunacion, Almacenamiento, Personal, Persona, Cita, Vacunacion

admin.site.register(Campana)
admin.site.register(TipoVacuna)
admin.site.register(PuntoVacunacion)
admin.site.register(Almacenamiento)
admin.site.register(Personal)
admin.site.register(Persona)
admin.site.register(Cita)
admin.site.register(Vacunacion)