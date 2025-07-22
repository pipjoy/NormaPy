"""
Módulo para la detección de columnas por contenido usando heurísticas.
"""
from __future__ import annotations

import pandas as pd


def _es_numero(valor: str) -> bool:
    """Devuelve True si el valor puede interpretarse como un número."""
    if valor is None:
        return False
    if isinstance(valor, (int, float)):
        return True
    texto = str(valor)
    texto = texto.replace(',', '').replace('$', '')
    try:
        float(texto)
        return True
    except ValueError:
        return False


def detectar_columna_precio(df: pd.DataFrame) -> str | None:
    """Intenta detectar la columna de precio revisando valores numéricos."""
    for col in df.columns:
        serie = df[col].dropna().astype(str)
        muestra = serie.head(20)
        if not len(muestra):
            continue
        propor_numeros = sum(_es_numero(v) for v in muestra) / len(muestra)
        if propor_numeros >= 0.8:
            return col
    return None


def detectar_columna_stock(df: pd.DataFrame) -> str | None:
    """Intenta detectar la columna de stock (números enteros)."""
    for col in df.columns:
        serie = df[col].dropna().astype(str)
        muestra = serie.head(20)
        if not len(muestra):
            continue
        numeros = [v for v in muestra if _es_numero(v)]
        if not numeros:
            continue
        propor = len(numeros) / len(muestra)
        if propor >= 0.8:
            # Considerar entero si casi todos son enteros
            if all(float(str(v).replace(',', '').replace('$', '')) % 1 == 0 for v in numeros):
                return col
    return None


def detectar_columna_sku(df: pd.DataFrame) -> str | None:
    """Detecta la columna SKU por gran cantidad de valores únicos no numéricos."""
    for col in df.columns:
        serie = df[col].dropna().astype(str)
        if not len(serie):
            continue
        # Debe tener bastantes valores únicos y no ser numérica en su mayoría
        propor_no_num = sum(not _es_numero(v) for v in serie.head(20)) / min(len(serie), 20)
        if propor_no_num < 0.8:
            continue
        if serie.nunique() / len(serie) > 0.5:
            return col
    return None


def detectar_columna_nombre(df: pd.DataFrame) -> str | None:
    """Detecta la columna nombre como cadena textual con muchos valores únicos."""
    for col in df.columns:
        serie = df[col].dropna().astype(str)
        if not len(serie):
            continue
        propor_no_num = sum(not _es_numero(v) for v in serie.head(20)) / min(len(serie), 20)
        if propor_no_num >= 0.8 and serie.nunique() / len(serie) > 0.5:
            return col
    return None


def detectar_columna_marca(df: pd.DataFrame) -> str | None:
    """Detecta la columna marca como cadenas con pocos valores únicos."""
    for col in df.columns:
        serie = df[col].dropna().astype(str)
        if not len(serie):
            continue
        propor_no_num = sum(not _es_numero(v) for v in serie.head(20)) / min(len(serie), 20)
        if propor_no_num < 0.8:
            continue
        unique_ratio = serie.nunique() / len(serie)
        if 0.05 <= unique_ratio <= 0.5:
            return col
    return None


HEURISTICAS = {
    'precio': detectar_columna_precio,
    'stock': detectar_columna_stock,
    'sku': detectar_columna_sku,
    'nombre': detectar_columna_nombre,
    'marca': detectar_columna_marca,
}
