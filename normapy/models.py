from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage

# Ubicación para guardar los archivos originales
upload_storage = FileSystemStorage(location='uploads/')

class Importacion(models.Model):
    archivo = models.FileField(upload_to='importaciones/')
    nombre_original = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    cantidad_productos = models.PositiveIntegerField()
    columnas_detectadas = models.TextField()
    se_generaron_skus = models.BooleanField(default=False)

    def __str__(self):
        return f"Importación del {self.fecha_subida.strftime('%Y-%m-%d %H:%M')}"

class Producto(models.Model):
    importacion = models.ForeignKey(Importacion, on_delete=models.SET_NULL, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    marca = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"


class HistorialImportacion(models.Model):
    nombre_archivo = models.CharField(max_length=255)
    fecha_importacion = models.DateTimeField(auto_now_add=True)
    productos_importados = models.IntegerField()
    errores = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_archivo} ({self.fecha_importacion.date()})"
