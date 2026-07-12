from django.urls import path
from .views import (
    ClienteCreateView, ClienteDeactivateView, ClienteListView, ClienteUpdateView,
    api_pacientes,
)

app_name = 'customers'
urlpatterns = [
    path('', ClienteListView.as_view(), name='cliente_list'),
    path('create/', ClienteCreateView.as_view(), name='cliente_create'),
    path('<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('<int:pk>/deactivate/', ClienteDeactivateView.as_view(), name='cliente_deactivate'),
    path('api/pacientes/', api_pacientes, name='api_pacientes'),
]