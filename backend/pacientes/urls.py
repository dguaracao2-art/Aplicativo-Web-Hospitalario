from django.urls import path
from . import views

app_name = "pacientes"

urlpatterns = [
    path("", views.PacienteListView.as_view(), name="listar"),
    path("nuevo/", views.PacienteCreateView.as_view(), name="crear"),
    path("<int:paciente_id>/", views.PacienteDetailView.as_view(), name="detalle"),
    path("<int:paciente_id>/editar/", views.PacienteUpdateView.as_view(), name="editar"),
    path("<int:paciente_id>/eliminar/", views.PacienteDeleteView.as_view(), name="eliminar"),

    # Citas
    path("citas/", views.CitaListView.as_view(), name="citas_listar"),
    path("citas/nueva/", views.CitaCreateView.as_view(), name="citas_crear"),
    path("citas/<int:cita_id>/", views.CitaDetailView.as_view(), name="citas_detalle"),
    path("citas/<int:cita_id>/editar/", views.CitaUpdateView.as_view(), name="citas_editar"),
    path("citas/<int:cita_id>/cancelar/", views.CitaCancelView.as_view(), name="citas_cancelar"),

    # Médicos
    path("medicos/", views.MedicoListView.as_view(), name="medicos_listar"),
    path("medicos/nuevo/", views.MedicoCreateView.as_view(), name="medicos_crear"),
    path("medicos/<int:medico_id>/", views.MedicoDetailView.as_view(), name="medicos_detalle"),
    path("medicos/<int:medico_id>/editar/", views.MedicoUpdateView.as_view(), name="medicos_editar"),
    path("medicos/<int:medico_id>/eliminar/", views.MedicoDeleteView.as_view(), name="medicos_eliminar"),
]