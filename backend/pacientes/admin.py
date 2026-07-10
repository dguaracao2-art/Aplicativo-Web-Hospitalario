from django.contrib import admin
from .models import Paciente, Medico, Cita


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("paciente_id", "cedula", "nombres", "apellidos", "telefono", "estado")
    search_fields = ("cedula", "nombres", "apellidos")  # RF-007, RF-008
    list_filter = ("estado", "genero")


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("medico_id", "cedula", "nombres", "apellidos", "especialidad", "estado")
    search_fields = ("cedula", "nombres", "apellidos")
    list_filter = ("especialidad", "estado")


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("cita_id", "paciente", "medico", "fecha", "hora", "estado")
    list_filter = ("estado", "fecha", "medico")
    date_hierarchy = "fecha"