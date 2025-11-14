from django.urls import path
from .view.form_views import diag_form_view, cap_form_view, success_view

app_name = 'forms'

urlpatterns = [
    path('diagnostico/', diag_form_view, name='diag_form'),
    path('capacitacion/', cap_form_view, name='cap_form'),
    path('exito/', success_view, name='success'),
]
