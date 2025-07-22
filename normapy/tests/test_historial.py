from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from normapy.models import Importacion

class HistorialViewTests(TestCase):
    def test_historial_muestra_importacion(self):
        Importacion.objects.create(
            archivo=SimpleUploadedFile('test.csv', b'data'),
            nombre_original='test.csv',
            cantidad_productos=1,
            columnas_detectadas='sku',
            se_generaron_skus=False,
        )
        response = self.client.get(reverse('historial_importaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test.csv')
