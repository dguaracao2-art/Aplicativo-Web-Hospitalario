from django.contrib import admin
from .models import DetalleFactura, Factura, SecuenciaFactura


@admin.register(SecuenciaFactura)
class SecuenciaFacturaAdmin(admin.ModelAdmin):
    list_display = ['year', 'correlativo']

    def has_module_permission(self, request):
        # Contador interno de numeración de facturas: editarlo a mano
        # puede duplicar números de factura. Solo superusuarios lo ven.
        return request.user.is_superuser