import pandas as pd
from unidecode import unidecode


def limpieza_basica(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica una limpieza básica de valores para vista previa."""

    def _clean(value):
        if isinstance(value, str):
            val = unidecode(value).lower().strip()
            val = " ".join(val.split())
            return val if val else "Sin dato"
        if pd.isna(value):
            return "Sin dato"
        return value

    return df.applymap(_clean)
