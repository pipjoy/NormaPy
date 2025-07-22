from django.test import TestCase
from django.urls import reverse
from io import BytesIO
from normapy.models import Producto, Importacion

class ImportFlowTests(TestCase):
    def test_preview_then_confirm(self):
        csv_content = (
            "sku,nombre,precio,marca,stock\n"
            "A1,Producto1,10.5,M1,5\n"
            "A2,Producto2,20.0,M2,3\n"
        )
        file = BytesIO(csv_content.encode("utf-8"))
        file.name = "test.csv"
        # Preview step
        response = self.client.post(reverse('importar_archivo'), {'archivo': file})
        self.assertEqual(response.status_code, 200)
        self.assertIn('preview', response.context)
        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(Importacion.objects.count(), 0)
        # Confirm step using same session
        response = self.client.post(reverse('importar_archivo'), {'confirmar': '1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Producto.objects.count(), 2)
        self.assertEqual(Importacion.objects.count(), 1)
