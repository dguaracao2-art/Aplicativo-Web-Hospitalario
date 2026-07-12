from django.db import models
from core.models import BaseModel


class Cliente(BaseModel):
    cedula = models.CharField('Cédula/RUC', max_length=13, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    email = models.EmailField('Email', unique=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    direccion = models.TextField('Dirección', blank=True)
    paciente = models.ForeignKey(
        'pacientes.Paciente',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='clientes',
        verbose_name='Paciente vinculado',
        help_text='Opcional: relaciona este cliente con su registro de paciente para evitar datos duplicados.',
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'