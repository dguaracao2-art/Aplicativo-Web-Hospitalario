from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from invoicing.report_views import PDFMixin
from security.mixins import RolRequeridoMixin
from security.models import Rol
from .forms import PacienteForm, CitaForm, MedicoForm, RecetaForm, DetalleRecetaFormSet
from .models import Paciente, Cita, Medico, Receta


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



class RecetaListView(RolRequeridoMixin, ListView):
    """Recetas emitidas, de la más reciente a la más antigua."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.MEDICO, Rol.RECEPCIONISTA]
    model = Receta
    template_name = "pacientes/receta_list.html"
    context_object_name = "recetas"
    paginate_by = 10

    def get_queryset(self):
        qs = Receta.objects.select_related("paciente", "medico").all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(paciente__cedula__icontains=q)
                | Q(paciente__apellidos__icontains=q)
                | Q(diagnostico__icontains=q)
            )
        return qs


class RecetaCreateView(RolRequeridoMixin, CreateView):
    """Emite una receta con uno o varios medicamentos."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.MEDICO]
    model = Receta
    form_class = RecetaForm
    template_name = "pacientes/receta_form.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if self.request.POST:
            contexto["detalles"] = DetalleRecetaFormSet(self.request.POST)
        else:
            contexto["detalles"] = DetalleRecetaFormSet()
        return contexto

    def form_valid(self, form):
        detalles = self.get_context_data()["detalles"]

        if not detalles.is_valid():
            return self.form_invalid(form)

        # Una receta sin medicamentos no tiene sentido clínico.
        con_datos = [
            f for f in detalles
            if f.cleaned_data and not f.cleaned_data.get("DELETE")
        ]
        if not con_datos:
            form.add_error(None, "Agregue al menos un medicamento a la receta.")
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            detalles.instance = self.object
            detalles.save()

        messages.success(self.request, f"Receta #{self.object.receta_id} emitida correctamente.")
        return redirect("pacientes:recetas_detalle", receta_id=self.object.receta_id)


class RecetaDetailView(RolRequeridoMixin, DetailView):
    roles_permitidos = [Rol.ADMINISTRADOR, Rol.MEDICO, Rol.RECEPCIONISTA]
    model = Receta
    template_name = "pacientes/receta_detail.html"
    context_object_name = "receta"
    pk_url_kwarg = "receta_id"

    def get_queryset(self):
        return Receta.objects.select_related("paciente", "medico", "cita")


class RecetaPDFView(RolRequeridoMixin, PDFMixin, View):
    """Genera la receta imprimible que se lleva el paciente."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.MEDICO, Rol.RECEPCIONISTA]
    pdf_template = "pacientes/receta_pdf.html"

    def get(self, request, receta_id):
        receta = get_object_or_404(
            Receta.objects.select_related("paciente", "medico"), pk=receta_id
        )
        self.pdf_filename = f"receta_{receta.receta_id}_{receta.paciente.cedula}.pdf"
        return self.render_pdf({
            "receta": receta,
            "detalles": receta.detalles.all(),
        })


class RecetaAnularView(RolRequeridoMixin, View):
    """Anula una receta sin borrarla: el historial clínico no se altera."""

    roles_permitidos = [Rol.ADMINISTRADOR, Rol.MEDICO]

    def post(self, request, receta_id):
        receta = get_object_or_404(Receta, pk=receta_id)
        receta.estado = False
        receta.save(update_fields=["estado"])
        messages.success(request, f"Receta #{receta.receta_id} anulada.")
        return redirect("pacientes:recetas_listar")