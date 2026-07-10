from django.urls import path
from . import views

app_name = "pacientes"

urlpatterns = [
    path("", views.PacienteListView.as_view(), name="listar"),
    path("nuevo/", views.PacienteCreateView.as_view(), name="crear"),
    path("<int:paciente_id>/", views.PacienteDetailView.as_view(), name="detalle"),
    path("<int:paciente_id>/editar/", views.PacienteUpdateView.as_view(), name="editar"),
    path("<int:paciente_id>/eliminar/", views.PacienteDeleteView.as_view(), name="eliminar"),
]