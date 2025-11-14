import logging
import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from gspread.exceptions import APIError, SpreadsheetNotFound
import json
import base64
import sys

from django.conf import settings

logger = logging.getLogger(__name__)

# Decodificar credenciales del JSON base64
json_str = base64.b64decode(settings.SERVICE).decode("utf-8")
SERVICE_ACCOUNT_INFO = json.loads(json_str)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_google_sheet(sheet_id, worksheet_index=0):
    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).get_worksheet(worksheet_index)


def insert_row_to_sheet(sheet_id, data, worksheet_index=0):
    try:
        sheet = get_google_sheet(sheet_id, worksheet_index)
        sheet.append_row(data)
        return True  # éxito
    except DefaultCredentialsError:
        logger.error(
            "❌ No se pudieron cargar las credenciales de la cuenta de servicio.")
    except RefreshError:
        logger.error(
            "❌ No se pudieron refrescar las credenciales (token expirado o inválido).")
    except SpreadsheetNotFound:
        logger.error(
            f"❌ El Spreadsheet con ID {sheet_id} no se encontró o no hay acceso.")
    except APIError as e:
        logger.error(f"❌ Error de API de Google Sheets: {e}")
    except SystemExit:
        logger.error("⚠️ SystemExit detectado (bloqueado).")
    except Exception as e:
        logger.error(
            f"⚠️ Error inesperado al insertar fila en Google Sheets: {e}")
    return False  # falló


def get_column_data(sheet_id, worksheet_index=0, column='A', start_row=2):
    """
    Obtiene datos de una columna específica desde una fila inicial.
    
    Args:
        sheet_id: ID del spreadsheet
        worksheet_index: Índice de la hoja (0 por defecto)
        column: Letra de la columna (ej: 'A', 'B', 'C')
        start_row: Fila inicial desde donde empezar a leer (2 por defecto, asumiendo header en fila 1)
    
    Returns:
        Lista de valores de la columna o lista vacía en caso de error
    """
    try:
        sheet = get_google_sheet(sheet_id, worksheet_index)
        # Obtener todos los valores de la columna
        column_values = sheet.col_values(ord(column.upper()) - ord('A') + 1)
        
        # Retornar desde start_row en adelante (ajustando el índice a 0-based)
        # Filtrar valores vacíos
        result = [value.strip() for value in column_values[start_row - 1:] if value.strip()]
        
        logger.info(f"✅ Se obtuvieron {len(result)} valores de la columna {column}")
        return result
    except DefaultCredentialsError:
        logger.error(
            "❌ No se pudieron cargar las credenciales de la cuenta de servicio.")
    except RefreshError:
        logger.error(
            "❌ No se pudieron refrescar las credenciales (token expirado o inválido).")
    except SpreadsheetNotFound:
        logger.error(
            f"❌ El Spreadsheet con ID {sheet_id} no se encontró o no hay acceso.")
    except APIError as e:
        logger.error(f"❌ Error de API de Google Sheets: {e}")
    except Exception as e:
        logger.error(
            f"⚠️ Error inesperado al obtener datos de Google Sheets: {e}")
    return []  # retornar lista vacía en caso de error
