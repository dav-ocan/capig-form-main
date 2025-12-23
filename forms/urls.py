from django.urls import path
from .view.form_views import (
    dashboard_view,
    diag_form_view,
    cap_form_view,
    success_view,
    success_afiliado_view,
    success_estado_afiliado_view,
    estado_afiliado_view,
    nuevo_afiliado_view,
    ventas_afiliado_view,
    success_ventas_afiliado_view,
)

app_name = 'forms'

urlpatterns = [
    # === PÁGINA PRINCIPAL (Landing) ===
    path("", dashboard_view, name="home"),

    # === DASHBOARD (Inicio con layout) ===
    path("dashboard/", dashboard_view, name="dashboard"),

    # === SERVICIOS (Asesorías y Capacitaciones) ===
    path('asesorias/', diag_form_view, name='diag_form'),
    path('capacitacion/', cap_form_view, name='cap_form'),
    path('exito/', success_view, name='success'),  # Éxito para servicios

    # === GESTIÓN DE AFILIADOS - Registro ===
    path("registrar-afiliado/", nuevo_afiliado_view, name="nuevo_afiliado"),
    path("exito-afiliado/", success_afiliado_view, name="success_afiliado"),

    # === GESTIÓN DE AFILIADOS - Estado ===
    path("estado-afiliado/", estado_afiliado_view,
         name="estado_afiliado"),  # Búsqueda y actualización
    path("exito-estado-afiliado/", success_estado_afiliado_view,
         name="success_estado_afiliado"),

    # === GESTIÓN DE AFILIADOS - Ventas ===
    path("ventas-afiliado/", ventas_afiliado_view,
         name="ventas_afiliado"),  # Búsqueda y registro
    path("exito-ventas-afiliado/", success_ventas_afiliado_view,
         name="success_ventas_afiliado"),
]
