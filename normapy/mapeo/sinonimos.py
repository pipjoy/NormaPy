import json
import os

def cargar_sinonimos():
    ruta = os.path.join(os.path.dirname(__file__), 'sinonimos.json')
    with open(ruta, encoding='utf-8') as f:
        return json.load(f) 