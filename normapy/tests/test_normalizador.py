"""
Tests iniciales para la lógica de mapeo automático de columnas.
"""

import os
import pandas as pd
import pytest
from django.test import TestCase
from normapy.mapeo.normalizador import mapear_columnas
from normapy.mapeo.validacion import validar_datos
from normapy.models import Producto

class TestImportacion(TestCase):
    def setUp(self):
        # Crear un DataFrame de prueba con columnas en inglés
        self.df = pd.DataFrame([
            {"sku": "A1", "name": "Producto Uno", "price": 10.5, "brand": "MarcaX", "stock": 5},
            {"sku": "A2", "name": "Producto Dos", "price": 20.0, "brand": "MarcaY", "stock": 10},
        ])
        # Cargar sinonimos.json
        sinonimos_path = os.path.join(os.path.dirname(__file__), '../mapeo/sinonimos.json')
        import json
        with open(sinonimos_path, encoding='utf-8') as f:
            self.sinonimos = json.load(f)

    def test_mapeo_columnas_ingles(self):
        mapeo = mapear_columnas(self.df, self.sinonimos['global'], self.sinonimos.get('providers', {}))
        assert 'nombre' in mapeo and mapeo['nombre'] == 'name'
        assert 'precio' in mapeo and mapeo['precio'] == 'price'
        assert 'marca' in mapeo and mapeo['marca'] == 'brand'
        assert 'sku' in mapeo and mapeo['sku'] == 'sku'
        assert 'stock' in mapeo and mapeo['stock'] == 'stock'

    def test_validar_datos_y_guardado(self):
        mapeo = mapear_columnas(self.df, self.sinonimos['global'], self.sinonimos.get('providers', {}))
        df_limpio, acciones = validar_datos(self.df, mapeo)
        # Guardar productos
        for fila in df_limpio.to_dict(orient='records'):
            Producto.objects.update_or_create(
                sku=fila.get("sku"),
                defaults={
                    "nombre": fila.get("nombre"),
                    "precio": fila.get("precio"),
                    "stock": fila.get("stock"),
                    "marca": fila.get("marca"),
                }
            )
        # Verificar que los productos se guardaron
        assert Producto.objects.count() == 2
        p1 = Producto.objects.get(sku="A1")
        assert p1.nombre == "Producto Uno"
        assert float(p1.precio) == 10.5
        assert p1.marca == "MarcaX"
        assert p1.stock == 5

    def test_exportar_json(self):
        # Prepara productos
        Producto.objects.create(sku="B1", nombre="Test", precio=1.0, stock=1, marca="M1")
        from django.utils import timezone
        import json as pyjson
        output_dir = os.path.join('media', 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        fecha = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"productos_{fecha}_test.json"
        filepath = os.path.join(output_dir, filename)
        productos = list(Producto.objects.all().values('sku', 'nombre', 'precio', 'marca', 'stock'))
        with open(filepath, 'w', encoding='utf-8') as f:
            pyjson.dump(productos, f, ensure_ascii=False, indent=2)
        # Verifica que el archivo existe y contiene el producto
        assert os.path.exists(filepath)
        with open(filepath, encoding='utf-8') as f:
            data = pyjson.load(f)
            assert any(p['sku'] == 'B1' for p in data)
