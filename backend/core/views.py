from datetime import datetime, time, timedelta

from django.db.models import F, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from catalog.models import Producto
from customers.models import Cliente
from invoicing.models import Factura
from pacientes.models import Paciente, Cita


def dia_local(fecha):
    """Devuelve la medianoche de esa fecha, con la zona horaria local.

    MySQL no trae cargadas sus tablas de zonas horarias, así que no puede
    resolver consultas del tipo `fecha__date=...`: devuelve vacío sin avisar.
    Comparando rangos de fecha y hora, la conversión la hace Django en Python
    y el resultado es correcto en cualquier motor de base de datos.
    """
    return timezone.make_aware(datetime.combine(fecha, time.min))


class DashboardView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = timezone.localdate()
        manana = hoy + timedelta(days=1)
        inicio_mes = hoy.replace(day=1)

        # --- Estadísticas hospitalarias ---
        ctx['total_pacientes'] = Paciente.objects.filter(estado=True).count()
        ctx['consultas_hoy'] = Cita.objects.filter(fecha=hoy).count()
        ctx['citas_pendientes'] = Cita.objects.filter(estado='PRO', fecha__gte=hoy).count()

        ctx['proximas_citas'] = Cita.objects.select_related('paciente', 'medico').filter(
            estado='PRO', fecha__gte=hoy
        ).order_by('fecha', 'hora')[:5]

        # --- Facturación ---
        ctx['facturas_hoy'] = Factura.objects.filter(
            fecha_emision__gte=dia_local(hoy),
            fecha_emision__lt=dia_local(manana),
            is_active=True,
        ).count()

        ingresos_mes = Factura.objects.filter(
            fecha_emision__gte=dia_local(inicio_mes),
            fecha_emision__lt=dia_local(manana),
            is_active=True,
        ).aggregate(total=Sum('total'))
        ctx['ventas_mes'] = ingresos_mes['total'] or 0

        ctx['total_clientes'] = Cliente.objects.count()

        # Los servicios no llevan inventario, así que no pueden estar bajos.
        ctx['stock_bajo'] = Producto.objects.filter(
            es_servicio=False, stock__lt=F('stock_minimo')
        ).count()

        ctx['ultimas_facturas'] = Factura.objects.select_related('cliente').filter(
            is_active=True
        ).order_by('-fecha_emision')[:5]

        # --- Gráfico de los últimos 7 días ---
        desde = hoy - timedelta(days=6)
        emisiones = Factura.objects.filter(
            fecha_emision__gte=dia_local(desde),
            fecha_emision__lt=dia_local(manana),
            is_active=True,
        ).values_list('fecha_emision', 'total')

        # El agrupado por día también se hace aquí y no en la base, por lo mismo.
        por_dia = {}
        for emitida_en, total in emisiones:
            dia = timezone.localtime(emitida_en).date()
            por_dia[dia] = por_dia.get(dia, 0) + float(total)

        ctx['chart_labels'] = [(desde + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        ctx['chart_data'] = [por_dia.get(desde + timedelta(days=i), 0) for i in range(7)]

        return ctx