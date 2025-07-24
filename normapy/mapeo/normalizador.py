"""
Módulo para la lógica de mapeo automático de columnas.
"""

import pandas as pd
from unidecode import unidecode
import logging
import sys
import hashlib
from .sinonimos import cargar_sinonimos
from .heuristicas import HEURISTICAS
import unicodedata
import re

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


def normalizar_nombre(nombre: str) -> str:
    """
    Normaliza un nombre eliminando acentos, guiones, espacios y convirtiendo a minúsculas.
    Ejemplo: "Precio Venta" → "precioventa"
    """
    nombre = unicodedata.normalize('NFKD', nombre)
    nombre = nombre.encode('ascii', 'ignore').decode('utf-8')
    nombre = re.sub(r'[^a-zA-Z0-9]', '', nombre)
    return nombre.lower()


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

def mapear_columnas(columnas_archivo: list[str], df: pd.DataFrame) -> dict[str, str]:
    """
    Devuelve un mapeo campo_interno → nombre_columna_archivo usando sinónimos + heurísticas.
    """
    sinonimos = cargar_sinonimos()  # {"nombre": ["producto", ...], ...}
    columnas_normalizadas = {normalizar_texto(c): c for c in columnas_archivo}
    mapeo = {}

    # 1. Buscar coincidencias exactas con sinónimos
    for campo_interno, alias_posibles in sinonimos.items():
        for alias in alias_posibles:
            alias_normalizado = normalizar_texto(alias)
            if alias_normalizado in columnas_normalizadas:
                mapeo[campo_interno] = columnas_normalizadas[alias_normalizado]
                break

    # 2. Fallback: heurísticas para campos no mapeados
    campos_faltantes = [c for c in sinonimos if c not in mapeo]
    if campos_faltantes:
        from .heuristicas import aplicar_heuristicas
        heuristicas_resultado = aplicar_heuristicas(columnas_archivo, df)
        for campo in campos_faltantes:
            if campo in heuristicas_resultado:
                mapeo[campo] = heuristicas_resultado[campo]

    return mapeo


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
