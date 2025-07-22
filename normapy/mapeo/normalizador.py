"""
Módulo para la lógica de mapeo automático de columnas.
"""

import pandas as pd
import json
import os
import re
from unidecode import unidecode
from rapidfuzz import fuzz
import logging
import sys
import hashlib

# Configuración básica de logger (usando utils/logger.py si está implementado)
logger = logging.getLogger("normapy.mapeo.normalizador")
if not logger.hasHandlers():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def normalizar_texto(s):
    """
    Normaliza un texto: minúsculas, sin acentos, sin caracteres especiales, espacios limpios.
    """
    if not isinstance(s, str):
        return ""
    s = s.lower()
    s = unidecode(s)
    s = s.replace("-", " ").replace("_", " ")
    s = " ".join(s.split())
    return s


def aplanar_sinonimos(sin):
    """Convierte un dict de idiomas a una lista plana de sinónimos."""
    if isinstance(sin, dict):
        lista = []
        for v in sin.values():
            if isinstance(v, list):
                lista.extend(v)
            else:
                lista.append(v)
        return lista
    elif isinstance(sin, list):
        return sin
    else:
        return [sin]

def mapear_columnas(df, sinonimos_global, sinonimos_proveedor=None):
    """Mapea las columnas del archivo CSV/Excel a las columnas internas del sistema utilizando sinónimos."""
    mapeo = {}
    campos_no_mapeados = []
    columnas_archivo = [normalizar_texto(col) for col in df.columns]
    for campo, lista_sinonimos in sinonimos_global.items():
        encontrado = False
        for sin in lista_sinonimos:
            sin_norm = normalizar_texto(sin)
            for idx, col_norm in enumerate(columnas_archivo):
                if col_norm == sin_norm:
                    mapeo[campo] = df.columns[idx]
                    encontrado = True
                    break
            if encontrado:
                break
        if not encontrado:
            campos_no_mapeados.append(campo)
    return mapeo, campos_no_mapeados


def generar_sku(nombre, marca="", precio=""):
    """Genera un SKU hash basado en el contenido si no se encuentra uno real."""
    clave = f"{nombre}-{marca}-{precio}"
    hash_result = hashlib.md5(clave.encode()).hexdigest()[:10]
    return f"AUTO-{hash_result.upper()}"


def normalizar_df(df: pd.DataFrame, mapping: dict) -> tuple[pd.DataFrame, dict, bool]:
    df_normalizado = pd.DataFrame()
    # Campos obligatorios
    df_normalizado['nombre'] = df[mapping['nombre']]
    df_normalizado['precio'] = df[mapping['precio']]
    # Campo opcional: stock
    if 'stock' in mapping:
        df_normalizado['stock'] = df[mapping['stock']]
    else:
        df_normalizado['stock'] = 0
    # Campo opcional: marca
    if 'marca' in mapping:
        df_normalizado['marca'] = df[mapping['marca']]
    else:
        df_normalizado['marca'] = "Sin marca"
    # Campo opcional pero sensible: SKU
    if 'sku' in mapping:
        df_normalizado['sku'] = df[mapping['sku']]
        sku_generado = False
    else:
        # Generar SKU para cada fila
        df_normalizado['sku'] = df_normalizado.apply(
            lambda row: generar_sku(row['nombre'], row['marca'], row['precio']),
            axis=1
        )
        sku_generado = True
    return df_normalizado, mapping, sku_generado
