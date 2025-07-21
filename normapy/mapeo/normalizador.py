"""
Módulo para la lógica de mapeo automático de columnas.
"""

import pandas as pd
import json
import os
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
    columnas_no_mapeadas = []
    for col in df.columns:
        mapeado = False
        for clave, sin in sinonimos_global.items():
            sin_flat = []
            if isinstance(sin, dict):
                for v in sin.values():
                    sin_flat.extend(v)
            elif isinstance(sin, list):
                sin_flat = sin
            else:
                sin_flat = [sin]
            if col.lower() in [nombre.lower() for nombre in sin_flat]:
                mapeo[clave] = col
                mapeado = True
                break
        if not mapeado and sinonimos_proveedor:
            for proveedor, sin in sinonimos_proveedor.items():
                if col.lower() in [nombre.lower() for nombre in sin]:
                    mapeo[clave] = col
                    mapeado = True
                    break
        if not mapeado:
            columnas_no_mapeadas.append(col)
    print("🔍 Mapeo generado:", mapeo)
    if columnas_no_mapeadas:
        print(f"⚠ Las siguientes columnas no se han mapeado: {', '.join(columnas_no_mapeadas)}")
    return mapeo, columnas_no_mapeadas


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
