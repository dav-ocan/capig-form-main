from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from datetime import datetime
import pytz

from ..services.google_sheets_service import insert_row_to_sheet, get_column_data


@require_http_methods(["GET", "POST"])
def diag_form_view(request):
    """Vista para el formulario de diagnóstico"""
    if request.method == "POST":
        SHEET_ID = 6

        # Obtener datos del formulario
        razon_social = request.POST.get('razon_social')
        tipo_diagnostico = request.POST.get('tipo_diagnostico')
        subtipo_diagnostico = request.POST.get('subtipo_diagnostico', '')
        otros_subtipo = request.POST.get('otros_subtipo', '')
        se_diagnostico = request.POST.get('se_diagnostico') == 'true'

        # Obtener fecha y hora en Ecuador
        ecuador_tz = pytz.timezone('America/Guayaquil')
        now_ecuador = datetime.now(ecuador_tz)
        fecha_str = now_ecuador.strftime('%Y-%m-%d')
        hora_str = now_ecuador.strftime('%H:%M:%S')

        # Imprimir datos en consola (para debugging)
        print("\n=== FORMULARIO DE DIAGNÓSTICO ===")
        print(f"Razón Social: {razon_social}")
        print(f"Tipo de Diagnóstico: {tipo_diagnostico}")
        print(f"Subtipo de Diagnóstico: {subtipo_diagnostico}")
        print(f"Otros Subtipo: {otros_subtipo}")
        print(f"Se Diagnosticó: {se_diagnostico}")
        print(f"Fecha: {fecha_str}")
        print(f"Hora: {hora_str}")
        print("================================\n")

        # Insertar en Google Sheets
        success = insert_row_to_sheet(settings.SHEET_PATH, [
            razon_social,
            tipo_diagnostico,
            subtipo_diagnostico,
            otros_subtipo,
            'Sí' if se_diagnostico else 'No',
            fecha_str,
            hora_str,
        ], SHEET_ID)

        if success:
            return redirect('forms:success')
        else:
            messages.error(
                request, 'Hubo un error al guardar los datos. Por favor, intente nuevamente.')

    # Obtener empresas desde Google Sheets (tab 0, columna A, desde fila 2)
    empresas = get_column_data(
        settings.SHEET_PATH, worksheet_index=0, column='C', start_row=3)
    # print(empresas)

    # Si no hay empresas, usar valores por defecto
    if not empresas:
        empresas = [
            'Empresa Ejemplo S.A.',
            'Corporación ABC Ltda.',
            'Inversiones XYZ S.A.S.',
            'Grupo Empresarial 123',
            'Soluciones Tecnológicas DEF'
        ]

    return render(request, 'diag_form.html', {'empresas': empresas})


@require_http_methods(["GET", "POST"])
def cap_form_view(request):
    """Vista para el formulario de capacitación"""
    if request.method == "POST":
        SHEET_ID = 5
        # Obtener datos del formulario
        razon_social = request.POST.get('razon_social')
        nombre_capacitacion = request.POST.get('nombre_capacitacion')
        tipo_capacitacion = request.POST.get('tipo_capacitacion')
        valor_pago = request.POST.get('valor_pago')

        # Obtener fecha y hora en Ecuador
        ecuador_tz = pytz.timezone('America/Guayaquil')
        now_ecuador = datetime.now(ecuador_tz)
        fecha_str = now_ecuador.strftime('%Y-%m-%d')
        hora_str = now_ecuador.strftime('%H:%M:%S')

        # Imprimir datos en consola (para debugging)
        print("\n=== FORMULARIO DE CAPACITACIÓN ===")
        print(f"Razón Social: {razon_social}")
        print(f"Nombre de la Capacitación: {nombre_capacitacion}")
        print(f"Tipo de Capacitación: {tipo_capacitacion}")
        print(f"Valor del Pago: ${valor_pago}")
        print(f"Fecha: {fecha_str}")
        print(f"Hora: {hora_str}")
        print("==================================\n")

        # Insertar en Google Sheets
        success = insert_row_to_sheet(settings.SHEET_PATH, [
            razon_social,
            nombre_capacitacion,
            tipo_capacitacion,
            valor_pago,
            fecha_str,
            hora_str,
        ], SHEET_ID)

        if success:
            return redirect('forms:success')
        else:
            messages.error(
                request, 'Hubo un error al guardar los datos. Por favor, intente nuevamente.')

    # Obtener empresas desde Google Sheets (tab 0, columna A, desde fila 2)
    empresas = get_column_data(
        settings.SHEET_PATH, worksheet_index=0, column='C', start_row=3)

    # Si no hay empresas, usar valores por defecto
    if not empresas:
        empresas = [
            'Empresa Ejemplo S.A.',
            'Corporación ABC Ltda.',
            'Inversiones XYZ S.A.S.',
            'Grupo Empresarial 123',
            'Soluciones Tecnológicas DEF'
        ]

    return render(request, 'cap_form.html', {'empresas': empresas})


def success_view(request):
    """Vista de éxito después de enviar el formulario"""
    return render(request, 'success.html')


def custom_404_view(request, exception):
    """Vista personalizada para error 404"""
    return render(request, '404.html', status=404)
