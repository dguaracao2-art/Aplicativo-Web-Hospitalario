from django.db import models
from core.models import BaseModel


class Cliente(BaseModel):
    cedula = models.CharField("Cédula", max_length=10, unique=True)
    nombres = models.CharField("Nombres", max_length=100)
    apellidos = models.CharField("Apellidos", max_length=100)
    fecha_nacimiento = models.DateField("Fecha de nacimiento")
    sexo = models.CharField(
        "Sexo",
        max_length=10,
        choices=[
            ("Masculino", "Masculino"),
            ("Femenino", "Femenino"),
        ],
    )
    telefono = models.CharField("Teléfono", max_length=20)
    email = models.EmailField("Correo", blank=True)
    direccion = models.TextField("Dirección")
    foto = models.ImageField(
        "Fotografía",
        upload_to="pacientes/",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"