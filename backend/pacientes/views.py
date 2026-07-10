from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import PacienteForm
from .models import Paciente


class PacienteListView(LoginRequiredMixin, ListView):
    """RF-003: consultar pacientes registrados. RF-007/RF-008: búsqueda."""

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


class PacienteDetailView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = "pacientes/paciente_detail.html"
    context_object_name = "paciente"
    pk_url_kwarg = "paciente_id"


class PacienteCreateView(LoginRequiredMixin, CreateView):
    """RF-002: registrar pacientes."""

    model = Paciente
    form_class = PacienteForm
    template_name = "pacientes/paciente_form.html"
    success_url = reverse_lazy("pacientes:listar")

    def form_valid(self, form):
        messages.success(self.request, "Paciente registrado correctamente.")
        return super().form_valid(form)


class PacienteUpdateView(LoginRequiredMixin, UpdateView):
    """RF-004: actualizar información de pacientes."""

    model = Paciente
    form_class = PacienteForm
    template_name = "pacientes/paciente_form.html"
    success_url = reverse_lazy("pacientes:listar")
    pk_url_kwarg = "paciente_id"

    def form_valid(self, form):
        messages.success(self.request, "Paciente actualizado correctamente.")
        return super().form_valid(form)


class PacienteDeleteView(LoginRequiredMixin, DeleteView):
    """Baja lógica: marca estado=False en lugar de borrar el registro."""

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