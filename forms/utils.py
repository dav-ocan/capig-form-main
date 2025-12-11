import os
import logging
from datetime import datetime
from typing import Dict

from django.conf import settings

from capig_form.services.google_sheets_service import get_google_sheet

# Encabezados mínimos usados en la hoja SOCIOS
EXPECTED_BASE_HEADERS = [
    "RUC",
    "RAZON_SOCIAL",
    "CIUDAD",
    "FECHA_AFILIACION",
]


def limpiar_ruc(valor):
    """Normaliza el RUC removiendo comillas y espacios."""
    return str(valor).replace("'", "").replace('"', "").strip()


def _get_estado_sheet():
    """Obtiene la hoja de ESTADO_SOCIO desde Google Sheets."""
    sheet_id = os.getenv("SHEET_PATH") or getattr(settings, "SHEET_PATH", "")
    if not sheet_id:
        raise RuntimeError("SHEET_PATH no esta configurado.")
    return get_google_sheet(sheet_id, "ESTADO_SOCIO")


def _get_base_datos_sheet():
    """Obtiene la hoja SOCIOS desde Google Sheets."""
    sheet_id = os.getenv("SHEET_PATH") or getattr(settings, "SHEET_PATH", "")
    if not sheet_id:
        raise RuntimeError("SHEET_PATH no esta configurado.")
    return get_google_sheet(sheet_id, "SOCIOS")


def buscar_afiliado_por_ruc(ruc):
    """
    Busca primero en ESTADO_SOCIO; si falta info, completa desde SOCIOS.
    """
    ruc = limpiar_ruc(ruc)

    estado_sheet = _get_estado_sheet()
    estado_rows = estado_sheet.get_all_records()

    afiliado = next(
        (row for row in estado_rows if limpiar_ruc(row.get("RUC", "")) == ruc),
        None,
    )

    if afiliado and all(
        afiliado.get(key) for key in ["RAZON_SOCIAL", "CIUDAD", "FECHA_AFILIACION", "ESTADO"]
    ):
        return {
            "razon_social": afiliado.get("RAZON_SOCIAL", ""),
            "ciudad": afiliado.get("CIUDAD", ""),
            "fecha_afiliacion": afiliado.get("FECHA_AFILIACION", ""),
            "estado": afiliado.get("ESTADO", ""),
        }

    # Buscar en la hoja SOCIOS sin validar encabezados
    base_sheet = _get_base_datos_sheet()
    all_values = base_sheet.get_all_values()
    
    if len(all_values) < 2:
        if afiliado:
            return {
                "razon_social": afiliado.get("RAZON_SOCIAL", ""),
                "ciudad": afiliado.get("CIUDAD", ""),
                "fecha_afiliacion": afiliado.get("FECHA_AFILIACION", ""),
                "estado": afiliado.get("ESTADO", ""),
            }
        return None
    
    headers = all_values[0]
    
    # Buscar índices de las columnas
    try:
        ruc_idx = headers.index("RUC")
        razon_idx = headers.index("RAZON_SOCIAL")
        ciudad_idx = headers.index("CIUDAD")
        fecha_idx = headers.index("FECHA_AFILIACION")
    except ValueError:
        # Si no encuentra las columnas en SOCIOS, usar lo que hay en ESTADO_SOCIO
        if afiliado:
            return {
                "razon_social": afiliado.get("RAZON_SOCIAL", ""),
                "ciudad": afiliado.get("CIUDAD", ""),
                "fecha_afiliacion": afiliado.get("FECHA_AFILIACION", ""),
                "estado": afiliado.get("ESTADO", ""),
            }
        return None
    
    # Buscar el RUC en los datos
    base_row = None
    for row in all_values[1:]:
        if len(row) > ruc_idx and limpiar_ruc(row[ruc_idx]) == ruc:
            base_row = {
                "RAZON_SOCIAL": row[razon_idx] if len(row) > razon_idx else "",
                "CIUDAD": row[ciudad_idx] if len(row) > ciudad_idx else "",
                "FECHA_AFILIACION": row[fecha_idx] if len(row) > fecha_idx else "",
            }
            break

    if afiliado:
        return {
            "razon_social": afiliado.get("RAZON_SOCIAL", ""),
            "ciudad": afiliado.get("CIUDAD", ""),
            "fecha_afiliacion": afiliado.get("FECHA_AFILIACION", ""),
            "estado": afiliado.get("ESTADO", ""),
        }

    if not base_row:
        return None

    return {
        "razon_social": base_row.get("RAZON_SOCIAL", ""),
        "ciudad": base_row.get("CIUDAD", ""),
        "fecha_afiliacion": base_row.get("FECHA_AFILIACION", ""),
        "estado": "",
    }


def actualizar_estado_afiliado(ruc, nuevo_estado):
    sheet = _get_estado_sheet()
    data = sheet.get_all_records()
    header = [col.strip().upper() for col in sheet.row_values(1)]

    def _col_index(nombre):
        try:
            return header.index(nombre) + 1
        except ValueError:
            return None

    col_estado = _col_index("ESTADO")
    col_actualizacion = _col_index("ACTUALIZACION_ESTADO")
    encontrado = False

    for idx, row in enumerate(data, start=2):
        if limpiar_ruc(row.get("RUC", "")) == limpiar_ruc(ruc):
            encontrado = True
            if col_estado:
                sheet.update_cell(idx, col_estado, nuevo_estado)
            if col_actualizacion:
                sheet.update_cell(
                    idx,
                    col_actualizacion,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                )
            break

    # Si no se encontro el RUC, agregar nueva fila con datos base y estado actualizado
    if not encontrado:
        base_sheet = _get_base_datos_sheet()
        all_values = base_sheet.get_all_values()
        
        if len(all_values) < 2:
            return
        
        headers = all_values[0]
        
        # Buscar índices de las columnas
        try:
            ruc_idx = headers.index("RUC")
            razon_idx = headers.index("RAZON_SOCIAL")
            ciudad_idx = headers.index("CIUDAD")
            fecha_idx = headers.index("FECHA_AFILIACION")
        except ValueError:
            return
        
        # Buscar el RUC en los datos
        base_row = {}
        for row in all_values[1:]:
            if len(row) > ruc_idx and limpiar_ruc(row[ruc_idx]) == limpiar_ruc(ruc):
                base_row = {
                    "RAZON_SOCIAL": row[razon_idx] if len(row) > razon_idx else "",
                    "CIUDAD": row[ciudad_idx] if len(row) > ciudad_idx else "",
                    "FECHA_AFILIACION": row[fecha_idx] if len(row) > fecha_idx else "",
                }
                break

        # Orden esperado: RUC | RAZON_SOCIAL | FECHA_AFILIACION | ESTADO | CIUDAD | ACTUALIZACION_ESTADO
        new_row = [
            limpiar_ruc(ruc),
            base_row.get("RAZON_SOCIAL", ""),
            base_row.get("FECHA_AFILIACION", ""),
            nuevo_estado,
            base_row.get("CIUDAD", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ]
        sheet.append_row(new_row)


def buscar_afiliado_por_ruc_base_datos(ruc):
    """Busca un afiliado únicamente en la hoja SOCIOS."""
    ruc = limpiar_ruc(ruc)
    sheet = _get_base_datos_sheet()
    
    # Obtener encabezados de la fila 1 y datos desde la fila 2
    all_values = sheet.get_all_values()
    if len(all_values) < 2:
        return None
    
    headers = all_values[0]  # Primera fila como encabezados
    
    # Buscar índices de las columnas que necesitamos
    try:
        ruc_idx = headers.index("RUC")
        razon_idx = headers.index("RAZON_SOCIAL")
        ciudad_idx = headers.index("CIUDAD")
        fecha_idx = headers.index("FECHA_AFILIACION")
    except ValueError:
        # Si no encuentra alguna columna, retornar None
        return None
    
    # Buscar en los datos (desde fila 2 en adelante)
    for row in all_values[1:]:
        if len(row) > ruc_idx and limpiar_ruc(row[ruc_idx]) == ruc:
            return {
                "razon_social": row[razon_idx] if len(row) > razon_idx else "",
                "ciudad": row[ciudad_idx] if len(row) > ciudad_idx else "",
                "fecha_afiliacion": row[fecha_idx] if len(row) > fecha_idx else "",
            }
    return None


def guardar_ventas_afiliado(data: Dict[str, str]):
    """
    Inserta un registro en la hoja VENTAS_SOCIO con el orden exacto:
    RUC | RAZON_SOCIAL | CIUDAD | FECHA_AFILIACION | REGISTRO_VENTAS |
    COMPARATIVO | MONTO_ESTIMADO | OBSERVACIONES | FECHA_REGISTRO | ANIO
    """
    logging.info("Datos recibidos para guardar ventas: %s", data)

    sheet_id = os.getenv("SHEET_PATH") or getattr(settings, "SHEET_PATH", "")
    if not sheet_id:
        raise RuntimeError("SHEET_PATH no esta configurado.")

    sheet = get_google_sheet(sheet_id, "VENTAS_SOCIO")

    fila = [
        data.get("ruc", ""),
        data.get("razon_social", ""),
        data.get("ciudad", ""),
        data.get("fecha_afiliacion", ""),
        data.get("registro_ventas", ""),
        data.get("comparativo", ""),
        data.get("ventas_estimadas", ""),
        data.get("observaciones", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        data.get("anio", ""),
    ]

    if len(fila) != 10:
        raise ValueError(f"Fila con columnas inesperadas: {fila}")

    # Inserta asegurando que se respeten las primeras columnas (A-J) en la siguiente fila disponible
    next_row = len(sheet.get_all_values()) + 1
    start = f"A{next_row}"
    end = f"J{next_row}"
    sheet.update(f"{start}:{end}", [fila], value_input_option="USER_ENTERED")
    try:
        # Forzar formato de fecha dd/MM/YYYY en la columna D a partir de la fila 2
        sheet.format(f"D2:D{next_row}", {"numberFormat": {
                     "type": "DATE", "pattern": "dd/MM/yyyy"}})
    except Exception:
        logging.warning(
            "No se pudo aplicar formato de fecha a la columna D en VENTAS_SOCIO.")
