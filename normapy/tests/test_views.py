from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from normapy.models import Importacion, Producto


class ProductosPorImportacionTests(TestCase):
    def setUp(self):
        upload_file = SimpleUploadedFile('test.csv', b'dummy', content_type='text/csv')
        self.importacion = Importacion.objects.create(
            archivo=upload_file,
            nombre_original='test.csv',
            cantidad_productos=1,
            columnas_detectadas='sku,nombre',
            se_generaron_skus=False
        )
        Producto.objects.create(
            importacion=self.importacion,
            sku='SKU1',
            nombre='Prod1',
            precio=1.0,
            stock=1,
            marca='Brand'
        )

    def test_template_renders(self):
        url = reverse('productos_por_importacion', args=[self.importacion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'normapy/productos_por_importacion.html')
        self.assertContains(response, 'Prod1')
