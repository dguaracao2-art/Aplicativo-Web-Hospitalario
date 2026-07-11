from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RolRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Restringe el acceso a una vista según el rol del usuario autenticado.

    Uso:
        class MiVista(RolRequeridoMixin, ListView):
            roles_permitidos = [User.Rol.ADMINISTRADOR, User.Rol.RECEPCIONISTA]
            ...

    Si el usuario no está autenticado -> redirige al login (comportamiento normal
    de LoginRequiredMixin). Si está autenticado pero no tiene el rol permitido
    -> lanza 403 Forbidden. Los superusuarios (is_superuser=True) siempre pasan.
    """

    roles_permitidos = []

    def test_func(self):
        usuario = self.request.user
        if not usuario.is_authenticated:
            return False
        if usuario.is_superuser:
            return True
        return usuario.rol in self.roles_permitidos

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied(
            "No tienes permiso para acceder a esta sección con tu rol actual."
        )