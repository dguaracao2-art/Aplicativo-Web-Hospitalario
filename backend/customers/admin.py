from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombre', 'email', 'telefono', 'paciente', 'is_active']
    list_filter = ['is_active']
    search_fields = ['cedula', 'nombre', 'email']
    autocomplete_fields = ['paciente']

    def get_queryset(self, request):
        return Cliente.all_objects.select_related('paciente').all()