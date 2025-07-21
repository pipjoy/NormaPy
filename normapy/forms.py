"""
Formulario UploadForm para la carga de archivos.
"""

from django import forms

class UploadForm(forms.Form):
    archivo = forms.FileField(label="Archivo CSV o Excel")
    # Opcional: proveedor = forms.ChoiceField(choices=[...], required=False)
