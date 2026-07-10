from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = [
        'cedula',
        'nombres',
        'apellidos',
        'telefono',
        'email',
        'is_active'
    ]

    search_fields = [
        'cedula',
        'nombres',
        'apellidos',
        'email'
    ]

    list_filter = [
        'sexo',
        'is_active'
    ]

    ordering = [
        'apellidos',
        'nombres'
    ]