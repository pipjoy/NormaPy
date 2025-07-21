from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage

# Ubicación para guardar los archivos originales
upload_storage = FileSystemStorage(location='uploads/')

class Importacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=now)
    archivo_nombre = models.CharField(max_length=255)
    archivo_original = models.FileField(upload_to='importaciones/', storage=upload_storage, null=True, blank=True)
    total_productos = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.usuario} – {self.archivo_nombre} ({self.fecha.date()})"

class Producto(models.Model):
    importacion = models.ForeignKey(Importacion, on_delete=models.SET_NULL, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    marca = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"
