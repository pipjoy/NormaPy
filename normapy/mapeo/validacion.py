"""
Módulo para la validación de datos obligatorios y tipos.
"""

import pandas as pd
import logging
import sys

# Configuración básica de logger (usando utils/logger.py si está implementado)
logger = logging.getLogger("normapy.mapeo.validacion")
if not logger.hasHandlers():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def validar_columnas_tipo(df):
    """Valida que las columnas 'precio' y 'stock' tengan los tipos correctos."""
    if 'precio' in df.columns:
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
    if 'stock' in df.columns:
        df['stock'] = pd.to_numeric(df['stock'], errors='coerce')
    return df


def verificar_columnas_requeridas(mapeo):
    columnas_requeridas = ['nombre', 'precio', 'sku', 'marca', 'stock']
    for columna in columnas_requeridas:
        if columna not in mapeo:
            raise ValueError(f"Falta la columna obligatoria: {columna}")

def limpiar_columnas(df):
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()
    return df

def validar_datos(df, mapeo):
    acciones = {}
    # Validar que las columnas esenciales estén mapeadas
    verificar_columnas_requeridas(mapeo)
    df = limpiar_columnas(df)
    # Renombrar columnas de acuerdo al mapeo
    renombres = {mapeo[campo]: campo for campo in mapeo}
    df = df.rename(columns=renombres)
    df = validar_columnas_tipo(df)
    # Aquí agregaríamos más validaciones y transformaciones si es necesario
    return df, acciones
