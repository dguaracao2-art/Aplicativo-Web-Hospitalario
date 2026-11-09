"""
Modelos del Sistema de Registro y Gestión de Pacientes y Consultas Médicas.

Basado en:
- Diccionario de datos (Tabla 31) del documento del proyecto.
- Requerimientos funcionales RF-001 a RF-009.

Nota: si esta app vive dentro del proyecto Django del repo
POO-4TO-CURSO-DJANGO-POSTGRES-REACT, ajusta el nombre de la app
("pacientes") según tu estructura real (backend/apps/...).
"""

from django.core.exceptions import ValidationError
from django.db import models


class Paciente(models.Model):
    """Tabla de pacientes (RF-002, RF-003, RF-004, RF-007, RF-008)."""

    GENERO_CHOICES = [
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
    ]

    paciente_id = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES)
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    correo_electronico = models.EmailField(max_length=100, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)  # activo / inactivo

    class Meta:
        db_table = "paciente"
        ordering = ["apellidos", "nombres"]
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        indexes = [
            models.Index(fields=["cedula"]),
            models.Index(fields=["apellidos", "nombres"]),
        ]

    def __str__(self):
        return f"{self.apellidos} {self.nombres} ({self.cedula})"


class Medico(models.Model):
    """Tabla de médicos (necesaria para RF-005: agendar citas)."""

    ESPECIALIDAD_CHOICES = [
        ("MG", "Medicina General"),
        ("PED", "Pediatría"),
        ("GIN", "Ginecología"),
        ("CAR", "Cardiología"),
        ("DER", "Dermatología"),
        ("TRA", "Traumatología"),
    ]

    medico_id = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=3, choices=ESPECIALIDAD_CHOICES)
    telefono = models.CharField(max_length=15, blank=True)
    correo_electronico = models.EmailField(max_length=100, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)  # activo / inactivo

    class Meta:
        db_table = "medico"
        ordering = ["apellidos", "nombres"]
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        return f"Dr(a). {self.apellidos} {self.nombres} - {self.get_especialidad_display()}"


class Cita(models.Model):
    """Tabla de citas médicas (RF-005, RF-006)."""

    ESTADO_CHOICES = [
        ("PRO", "Programada"),
        ("ATE", "Atendida"),
        ("CAN", "Cancelada"),
    ]

    cita_id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name="citas"
    )
    medico = models.ForeignKey(
        Medico, on_delete=models.CASCADE, related_name="citas"
    )
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=3, choices=ESTADO_CHOICES, default="PRO")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    recordatorio_enviado = models.BooleanField('Recordatorio enviado', default=False)
    recordatorio_fecha = models.DateTimeField('Fecha del recordatorio', null=True, blank=True)

    class Meta:
        db_table = "cita"
        ordering = ["-fecha", "-hora"]
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        # Evita doble reserva del mismo médico en la misma fecha/hora
        constraints = [
            models.UniqueConstraint(
                fields=["medico", "fecha", "hora"], name="unica_cita_medico_horario"
            )
        ]
    def clean(self):
        """Impide dos citas activas del mismo médico en la misma fecha y hora.

        Reemplaza a la restricción de base de datos anterior, que no distinguía
        entre citas activas y canceladas: al cancelar una cita, su horario
        quedaba bloqueado para siempre. En MySQL no se puede expresar esa
        condición en la base, porque no soporta índices condicionales.
        """
        if not (self.medico_id and self.fecha and self.hora):
            return

        if self.estado == "CAN":
            return

        choque = Cita.objects.filter(
            medico_id=self.medico_id, fecha=self.fecha, hora=self.hora
        ).exclude(estado="CAN")

        if self.pk:
            choque = choque.exclude(pk=self.pk)

        if choque.exists():
            raise ValidationError(
                {"hora": "Este médico ya tiene una cita activa en esa fecha y hora."}
            )     
    def __str__(self):
        return f"{self.paciente} con {self.medico} el {self.fecha} {self.hora}"


class Receta(models.Model):
    """Receta médica emitida tras una consulta."""

    receta_id = models.AutoField(primary_key=True)
    cita = models.ForeignKey(
        Cita, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="recetas", verbose_name="Cita asociada",
    )
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name="recetas")
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name="recetas")
    fecha = models.DateField("Fecha de emisión")
    diagnostico = models.CharField("Diagnóstico", max_length=300)
    indicaciones = models.TextField("Indicaciones generales", blank=True)
    estado = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "receta"
        ordering = ["-fecha", "-receta_id"]
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"

    def __str__(self):
        return f"Receta #{self.receta_id} - {self.paciente}"


class DetalleReceta(models.Model):
    """Cada medicamento recetado, con su posología."""

    detalle_id = models.AutoField(primary_key=True)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="detalles")
    medicamento = models.CharField("Medicamento", max_length=200)
    dosis = models.CharField("Dosis", max_length=100, help_text="Ej: 500 mg")
    frecuencia = models.CharField("Frecuencia", max_length=100, help_text="Ej: cada 8 horas")
    duracion = models.CharField("Duración", max_length=100, help_text="Ej: 7 días")

    class Meta:
        db_table = "detalle_receta"
        verbose_name = "Medicamento recetado"
        verbose_name_plural = "Medicamentos recetados"

    def __str__(self):
        return f"{self.medicamento} {self.dosis}"