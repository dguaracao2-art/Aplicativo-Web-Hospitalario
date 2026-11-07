from datetime import timedelta

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from security.mixins import RolRequeridoMixin
from security.models import Rol
from .forms import PacienteForm, CitaForm, MedicoForm
from .models import Paciente, Cita, Medico


class PacienteListView(RolRequeridoMixin, ListView):
    """RF-003: consultar pacientes registrados. RF-007/RF-008: búsqueda."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA, Rol.MEDICO]
    model = Paciente
    template_name = "pacientes/paciente_list.html"
    context_object_name = "pacientes"
    paginate_by = 10

    def get_queryset(self):
        queryset = Paciente.objects.filter(estado=True)
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(nombres__icontains=q)
                | Q(apellidos__icontains=q)
                | Q(cedula__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class PacienteDetailView(RolRequeridoMixin, DetailView):
    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA, Rol.MEDICO]
    model = Paciente
    template_name = "pacientes/paciente_detail.html"
    context_object_name = "paciente"
    pk_url_kwarg = "paciente_id"


class PacienteCreateView(RolRequeridoMixin, CreateView):
    """RF-002: registrar pacientes."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA]
    model = Paciente
    form_class = PacienteForm
    template_name = "pacientes/paciente_form.html"
    success_url = reverse_lazy("pacientes:listar")

    def form_valid(self, form):
        messages.success(self.request, "Paciente registrado correctamente.")
        return super().form_valid(form)


class PacienteUpdateView(RolRequeridoMixin, UpdateView):
    """RF-004: actualizar información de pacientes."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA]
    model = Paciente
    form_class = PacienteForm
    template_name = "pacientes/paciente_form.html"
    success_url = reverse_lazy("pacientes:listar")
    pk_url_kwarg = "paciente_id"

    def form_valid(self, form):
        messages.success(self.request, "Paciente actualizado correctamente.")
        return super().form_valid(form)


class PacienteDeleteView(RolRequeridoMixin, DeleteView):
    """Baja lógica: marca estado=False en lugar de borrar el registro."""

    roles_permitidos = [Rol.ADMINISTRADOR]
    model = Paciente
    template_name = "pacientes/paciente_confirm_delete.html"
    success_url = reverse_lazy("pacientes:listar")
    pk_url_kwarg = "paciente_id"

    def form_valid(self, form):
        # Baja lógica: no se llama a super().form_valid() porque eso
        # ejecutaría self.object.delete() y borraría el registro físicamente.
        paciente = self.get_object()
        paciente.estado = False
        paciente.save()
        messages.success(self.request, "Paciente desactivado correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class CitaListView(RolRequeridoMixin, ListView):
    """RF-006: consultar citas agendadas."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA, Rol.MEDICO]
    model = Cita
    template_name = "pacientes/cita_list.html"
    context_object_name = "citas"
    paginate_by = 10

    def get_queryset(self):
        queryset = Cita.objects.select_related("paciente", "medico")
        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estado_filtro"] = self.request.GET.get("estado", "")
        return context


class CitaDetailView(RolRequeridoMixin, DetailView):
    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA, Rol.MEDICO]
    model = Cita
    template_name = "pacientes/cita_detail.html"
    context_object_name = "cita"
    pk_url_kwarg = "cita_id"


class CitaCreateView(RolRequeridoMixin, CreateView):
    """RF-005: agendar citas."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA]
    model = Cita
    form_class = CitaForm
    template_name = "pacientes/cita_form.html"
    success_url = reverse_lazy("pacientes:citas_listar")

    def form_valid(self, form):
        messages.success(self.request, "Cita agendada correctamente.")
        return super().form_valid(form)


class CitaUpdateView(RolRequeridoMixin, UpdateView):
    """RF-005: reprogramar una cita existente."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA]
    model = Cita
    form_class = CitaForm
    template_name = "pacientes/cita_form.html"
    success_url = reverse_lazy("pacientes:citas_listar")
    pk_url_kwarg = "cita_id"

    def form_valid(self, form):
        messages.success(self.request, "Cita actualizada correctamente.")
        return super().form_valid(form)


class CitaCancelView(RolRequeridoMixin, DeleteView):
    """Cancela la cita (estado=CAN) en lugar de borrarla físicamente."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA]
    model = Cita
    template_name = "pacientes/cita_confirm_cancel.html"
    success_url = reverse_lazy("pacientes:citas_listar")
    pk_url_kwarg = "cita_id"

    def form_valid(self, form):
        cita = self.get_object()
        cita.estado = "CAN"
        cita.save()
        messages.success(self.request, "Cita cancelada correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class MedicoListView(RolRequeridoMixin, ListView):
    """Consultar médicos registrados."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA, Rol.MEDICO]
    model = Medico
    template_name = "pacientes/medico_list.html"
    context_object_name = "medicos"
    paginate_by = 10

    def get_queryset(self):
        queryset = Medico.objects.filter(estado=True)
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(nombres__icontains=q)
                | Q(apellidos__icontains=q)
                | Q(cedula__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class MedicoDetailView(RolRequeridoMixin, DetailView):
    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA, Rol.MEDICO]
    model = Medico
    template_name = "pacientes/medico_detail.html"
    context_object_name = "medico"
    pk_url_kwarg = "medico_id"


class MedicoCreateView(RolRequeridoMixin, CreateView):
    """Registrar médicos. Solo el Administrador gestiona personal médico."""

    roles_permitidos = [Rol.ADMINISTRADOR]
    model = Medico
    form_class = MedicoForm
    template_name = "pacientes/medico_form.html"
    success_url = reverse_lazy("pacientes:medicos_listar")

    def form_valid(self, form):
        messages.success(self.request, "Médico registrado correctamente.")
        return super().form_valid(form)


class MedicoUpdateView(RolRequeridoMixin, UpdateView):
    roles_permitidos = [Rol.ADMINISTRADOR]
    model = Medico
    form_class = MedicoForm
    template_name = "pacientes/medico_form.html"
    success_url = reverse_lazy("pacientes:medicos_listar")
    pk_url_kwarg = "medico_id"

    def form_valid(self, form):
        messages.success(self.request, "Médico actualizado correctamente.")
        return super().form_valid(form)


class MedicoDeleteView(RolRequeridoMixin, DeleteView):
    """Baja lógica: marca estado=False en lugar de borrar el registro."""

    roles_permitidos = [Rol.ADMINISTRADOR]
    model = Medico
    template_name = "pacientes/medico_confirm_delete.html"
    success_url = reverse_lazy("pacientes:medicos_listar")
    pk_url_kwarg = "medico_id"

    def form_valid(self, form):
        medico = self.get_object()
        medico.estado = False
        medico.save()
        messages.success(self.request, "Médico desactivado correctamente.")
        return HttpResponseRedirect(self.get_success_url())

class RecordatoriosView(RolRequeridoMixin, ListView):
    """Citas próximas que todavía no se le han recordado al paciente."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA]
    model = Cita
    template_name = "pacientes/recordatorios.html"
    context_object_name = "citas"

    DIAS_ANTICIPACION = 2

    def get_queryset(self):
        hoy = timezone.localdate()
        limite = hoy + timedelta(days=self.DIAS_ANTICIPACION)
        return (
            Cita.objects.filter(estado="PRO", fecha__gte=hoy, fecha__lte=limite)
            .select_related("paciente", "medico")
            .order_by("fecha", "hora")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendientes"] = sum(
            1 for c in context["citas"] if not c.recordatorio_enviado
        )
        context["dias"] = self.DIAS_ANTICIPACION
        return context


class MarcarRecordatorioView(RolRequeridoMixin, View):
    """Deja constancia de que al paciente ya se le recordó su cita."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.RECEPCIONISTA]

    def post(self, request, cita_id):
        cita = get_object_or_404(Cita, pk=cita_id)
        cita.recordatorio_enviado = True
        cita.recordatorio_fecha = timezone.now()
        cita.save(update_fields=["recordatorio_enviado", "recordatorio_fecha"])
        messages.success(
            request,
            f"Recordatorio registrado para {cita.paciente.nombres} "
            f"{cita.paciente.apellidos}.",
        )
        return HttpResponseRedirect(reverse_lazy("pacientes:recordatorios"))