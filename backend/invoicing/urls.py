from django.urls import path
from .views import (
    InvoiceAnnulView,
    InvoiceCreateView,
    InvoiceDetailView,
    InvoiceListView,
    api_productos,
    api_clientes,
)
from .report_views import (
    DailyClosePDFView, InvoiceListPDFView, InvoicePDFView, ReportsIndexView,
)

app_name = 'invoicing'
urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice_list'),
    path('create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('<int:pk>/annul/', InvoiceAnnulView.as_view(), name='invoice_annul'),
    path('<int:pk>/pdf/', InvoicePDFView.as_view(), name='invoice_pdf'),
    path('api/productos/', api_productos, name='api_productos'),
    path('api/clientes/', api_clientes, name='api_clientes'),
    # Reportes
    path('reports/', ReportsIndexView.as_view(), name='reports_index'),
    path('reports/daily-close/', DailyClosePDFView.as_view(), name='daily_close_pdf'),
    path('reports/invoice-list/', InvoiceListPDFView.as_view(), name='invoice_list_pdf'),
]