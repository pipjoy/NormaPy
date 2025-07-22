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

    def test_xls_multiple_sheets_preview(self):
        import xlwt
        workbook = xlwt.Workbook()
        headers = ["sku", "nombre", "precio", "marca", "stock"]
        sheet1 = workbook.add_sheet("Hoja1")
        for idx, h in enumerate(headers):
            sheet1.write(0, idx, h)
        sheet1.write(1, 0, "A1")
        sheet1.write(1, 1, "Producto1")
        sheet1.write(1, 2, 10.0)
        sheet1.write(1, 3, "M1")
        sheet1.write(1, 4, 1)

        sheet2 = workbook.add_sheet("Hoja2")
        for idx, h in enumerate(headers):
            sheet2.write(0, idx, h)
        sheet2.write(1, 0, "A2")
        sheet2.write(1, 1, "Producto2")
        sheet2.write(1, 2, 20.0)
        sheet2.write(1, 3, "M2")
        sheet2.write(1, 4, 2)

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        buffer.name = "test.xls"

        response = self.client.post(reverse("importar_archivo"), {"archivo": buffer})
        self.assertEqual(response.status_code, 200)
        self.assertIn("preview", response.context)
        self.assertEqual(len(response.context["hojas"]), 2)

