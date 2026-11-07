from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto


def filtrar_por_estado(queryset, estado):
    """
    Filtra por estado según el selector de la barra superior.

    Por defecto solo muestra los activos: los registros dados de baja no
    desaparecen de la base (las facturas emitidas los siguen necesitando),
    pero tampoco estorban en el día a día.
    """
    if estado == 'inactivos':
        return queryset.filter(is_active=False)
    if estado == 'todos':
        return queryset
    return queryset.filter(is_active=True)


class CategoriaListView(PermissionRequiredMixin, ListView):
    permission_required = 'catalog.view_categoria'
    model = Categoria
    paginate_by = 10
    template_name = 'catalog/categoria_list.html'

    def get_queryset(self):
        qs = Categoria.all_objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        return qs.order_by('nombre')


class CategoriaCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_categoria'
    model = Categoria
    form_class = CategoriaForm
    template_name = 'catalog/categoria_form.html'
    success_url = reverse_lazy('catalog:categoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada correctamente.')
        return super().form_valid(form)


class CategoriaUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_categoria'
    model = Categoria
    form_class = CategoriaForm
    template_name = 'catalog/categoria_form.html'
    success_url = reverse_lazy('catalog:categoria_list')

    def get_queryset(self):
        # La lista muestra también las inactivas, así que deben poder abrirse.
        # Con el manager por defecto esto devolvía 404.
        return Categoria.all_objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada correctamente.')
        return super().form_valid(form)


class CategoriaDeactivateView(PermissionRequiredMixin, View):
    permission_required = 'catalog.delete_categoria'

    def post(self, request, pk):
        cat = Categoria.all_objects.get(pk=pk)
        if cat.productos.filter(is_active=True).exists():
            messages.error(request, 'No se puede desactivar: tiene productos activos.')
        else:
            cat.soft_delete()
            messages.success(request, f'Categoría "{cat.nombre}" desactivada.')
        return redirect('catalog:categoria_list')


class CategoriaActivateView(PermissionRequiredMixin, View):
    permission_required = 'catalog.change_categoria'

    def post(self, request, pk):
        cat = Categoria.all_objects.get(pk=pk)
        cat.restore()
        messages.success(request, f'Categoría "{cat.nombre}" reactivada.')
        return redirect('catalog:categoria_list')


class ProductoListView(PermissionRequiredMixin, ListView):
    permission_required = 'catalog.view_producto'
    model = Producto
    paginate_by = 10
    template_name = 'catalog/producto_list.html'

    def get_queryset(self):
        qs = Producto.all_objects.select_related('categoria').all()
        q = self.request.GET.get('q', '').strip()
        cat = self.request.GET.get('categoria', '').strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
        if cat:
            qs = qs.filter(categoria_id=cat)
        qs = filtrar_por_estado(qs, self.request.GET.get('estado', ''))
        return qs.order_by('nombre')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # El filtro de categorías del template necesita esta lista; sin ella
        # el desplegable salía vacío.
        ctx['categorias'] = Categoria.objects.order_by('nombre')
        ctx['estado_filtro'] = self.request.GET.get('estado', '')
        return ctx


class ProductoCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'catalog/producto_form.html'
    success_url = reverse_lazy('catalog:producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado correctamente.')
        return super().form_valid(form)


class ProductoUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'catalog/producto_form.html'
    success_url = reverse_lazy('catalog:producto_list')

    def get_queryset(self):
        # La lista muestra también los inactivos, así que deben poder abrirse.
        # Con el manager por defecto esto devolvía 404.
        return Producto.all_objects.select_related('categoria').all()

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)


class ProductoDeactivateView(PermissionRequiredMixin, View):
    permission_required = 'catalog.delete_producto'

    def post(self, request, pk):
        prod = Producto.all_objects.get(pk=pk)
        prod.soft_delete()
        messages.success(request, f'Producto "{prod.nombre}" desactivado.')
        return redirect('catalog:producto_list')


class ProductoActivateView(PermissionRequiredMixin, View):
    permission_required = 'catalog.change_producto'

    def post(self, request, pk):
        prod = Producto.all_objects.get(pk=pk)
        prod.restore()
        messages.success(request, f'Producto "{prod.nombre}" reactivado.')
        return redirect('catalog:producto_list')