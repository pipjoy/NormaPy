"""
Vista para subir archivos y ejecutar la normalización de datos.
"""
import pandas as pd
from django.shortcuts import render
from .forms import UploadForm
from .models import Producto, Importacion
import json
import os
from django.db.models import Count
from django.http import HttpResponse
from .utils.limpieza import limpieza_basica
from .mapeo.normalizador import mapear_columnas  # Usar la versión extendida
import json as pyjson
from django.utils import timezone
import os
from django.http import FileResponse

# Cargar sinonimos.json desde disco
SINONIMOS_PATH = os.path.join(os.path.dirname(__file__), 'mapeo', 'sinonimos.json')
with open(SINONIMOS_PATH, encoding='utf-8') as f:
    sinonimos = json.load(f)

def limpiar_columnas(df):
    """Limpia los nombres de las columnas para evitar errores por espacios o caracteres invisibles."""
    df.columns = df.columns.str.strip()  # Elimina espacios al inicio y al final
    df.columns = df.columns.str.lower()  # Convierte a minúsculas para evitar problemas de mayúsculas
    return df

def renombrar_columnas(df, mapeo):
    """Renombra las columnas del DataFrame según el mapeo generado."""
    columnas_actuales = df.columns.tolist()
    columnas_a_renombrar = {}
    for campo, nuevo_nombre in mapeo.items():
        if nuevo_nombre in columnas_actuales:
            columnas_a_renombrar[nuevo_nombre] = campo
        else:
            print(f"⚠ Columna mapeada '{nuevo_nombre}' no encontrada en el archivo.")
            raise ValueError(f"Columna mapeada '{nuevo_nombre}' no encontrada en el archivo.")
    df = df.rename(columns=columnas_a_renombrar)
    return df

def limpiar_datos(df):
    """Convierte los valores de las columnas a los tipos correctos (float o int)."""
    if 'precio' in df.columns:
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
    if 'stock' in df.columns:
        df['stock'] = pd.to_numeric(df['stock'], errors='coerce')
    return df

def mostrar_estadisticas(df):
    total_productos = len(df)
    precio_promedio = df['precio'].mean() if 'precio' in df.columns else 0
    stock_total = df['stock'].sum() if 'stock' in df.columns else 0
    skus_generados = df[df['sku'].astype(str).str.startswith('AUTO')].shape[0] if 'sku' in df.columns else 0
    return {
        "total_productos": total_productos,
        "precio_promedio": precio_promedio,
        "stock_total": stock_total,
        "skus_generados": skus_generados,
    }

def verificar_columnas_requeridas(df):
    """Verifica que las columnas esenciales estén en el archivo."""
    columnas_requeridas = ['nombre', 'precio', 'sku', 'marca', 'stock']
    for columna in columnas_requeridas:
        if columna not in df.columns:
            raise ValueError(f"Falta la columna obligatoria: {columna}")
    return True

def validar_mapeo(mapeo, df_columns):
    """Verifica que las columnas esenciales estén mapeadas correctamente."""
    for columna in ['sku', 'nombre', 'precio', 'marca', 'stock']:
        if columna not in mapeo:
            raise ValueError(f"Falta la columna obligatoria en el mapeo: {columna}")
        if mapeo[columna] not in df_columns:
            raise ValueError(f"Columna mapeada '{columna}' no encontrada en el archivo.")
    print("🗺️ Mapeo generado:", mapeo)
    return True

def mapear_columnas(df, sinonimos_global, sinonimos_proveedor=None):
    """Mapea las columnas del archivo CSV/Excel a las columnas internas del sistema."""
    mapeo = {}
    for col in df.columns:
        # Intentar mapear las columnas usando los sinónimos globales
        for clave, sin in sinonimos_global.items():
            if col in sin:
                mapeo[clave] = col
                break
        # Si no se encuentra, intentar con sinónimos del proveedor (si existen)
        if clave not in mapeo and sinonimos_proveedor:
            for clave, sin in sinonimos_proveedor.items():
                if col in sin:
                    mapeo[clave] = col
                    break
    return mapeo

def validar_columnas_vacias(df):
    """Verifica que no haya valores vacíos en las columnas requeridas."""
    for col in ['nombre', 'precio', 'sku']:
        if col in df.columns and df[col].isnull().any():
            raise ValueError(f"La columna '{col}' tiene valores vacíos.")
    return True

def filtrar_columnas_relevantes(df):
    """Filtra las columnas necesarias para la importación."""
    columnas_requeridas = ['nombre', 'precio', 'sku', 'marca', 'stock']
    columnas_presentes = [col for col in columnas_requeridas if col in df.columns]
    df = df[columnas_presentes]
    return df

def depurar_datos(df, mapeo=None):
    print("[DEPURACIÓN] Primeras filas del archivo:")
    print(df.head())
    print("[DEPURACIÓN] Columnas leídas:", df.columns.tolist())
    if mapeo is not None:
        print("[DEPURACIÓN] Mapeo generado:", mapeo)
        for campo, col in mapeo.items():
            if col not in df.columns:
                print(f"[DEPURACIÓN][ADVERTENCIA] Columna mapeada '{col}' no encontrada en el DataFrame tras renombrar.")

def importar_archivo(request):
    form = UploadForm(request.POST, request.FILES)
    mensaje = None
    acciones = {}
    mapeo = {}
    preview_data = []
    if request.method == 'POST' and form.is_valid():
        archivo = request.FILES['archivo']
        try:
            # Leer archivo CSV o Excel (soporte para varias hojas)
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            elif archivo.name.endswith('.xlsx'):
                xl = pd.ExcelFile(archivo)
                hoja = xl.sheet_names[0]
                df = xl.parse(hoja)
            else:
                raise ValueError("El archivo debe ser CSV o Excel.")
            print("[DEPURACIÓN] Primeras filas del archivo:")
            print(df.head())
            print("[DEPURACIÓN] Columnas originales:", df.columns.tolist())

            from .mapeo.validacion import limpiar_columnas, validar_datos
            df = limpiar_columnas(df)
            print("[DEPURACIÓN] Columnas después de limpiar:", df.columns.tolist())

            from .mapeo.normalizador import mapear_columnas
            mapeo, columnas_no_mapeadas = mapear_columnas(df, sinonimos['global'], sinonimos.get('providers', {}))
            print("[DEPURACIÓN] Mapeo generado:", mapeo)
            if columnas_no_mapeadas:
                print(f"⚠ Columnas no mapeadas: {', '.join(columnas_no_mapeadas)}")

            df = renombrar_columnas(df, mapeo)
            print("[DEPURACIÓN] Columnas después de renombrar:", df.columns.tolist())
            print("[DEPURACIÓN] Primeras filas tras renombrar:")
            print(df.head())

            # Normalizar y limpiar datos
            df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
            df['stock'] = pd.to_numeric(df['stock'], errors='coerce').fillna(0).astype(int)
            df['marca'] = df['marca'].fillna('Sin Marca')

            if 'limpiar' in request.POST:
                df = limpieza_basica(df)

            # Vista previa
            preview_data = df.head(3).to_dict(orient='records')

            if 'confirmar' in request.POST:
                from .models import Producto, HistorialImportacion
                for fila in df.to_dict(orient='records'):
                    Producto.objects.update_or_create(
                        sku=fila.get("sku"),
                        defaults={
                            "nombre": fila.get("nombre"),
                            "precio": fila.get("precio"),
                            "stock": fila.get("stock"),
                            "marca": fila.get("marca"),
                        }
                    )
                HistorialImportacion.objects.create(
                    nombre_archivo=archivo.name,
                    productos_importados=len(df),
                    errores=", ".join(columnas_no_mapeadas) if columnas_no_mapeadas else ""
                )
                acciones['estadisticas'] = mostrar_estadisticas(df)
                mensaje = "¡Productos importados exitosamente!"
        except Exception as e:
            form.add_error('archivo', f'Error procesando el archivo: {e}')
            print("[ERROR]", e)
    return render(request, 'normapy/preview.html', {
        'form': form,
        'mapeo': mapeo,
        'acciones': acciones,
        'preview': preview_data,
        'mensaje': mensaje,
        'estadisticas': acciones.get('estadisticas')
    })

def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'normapy/productos.html', {'productos': productos})

def exportar_productos(request):
    formato = request.GET.get('formato', 'xlsx')
    productos = Producto.objects.all().values('sku', 'nombre', 'precio', 'marca', 'stock')
    df = pd.DataFrame(list(productos))

    if formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="productos_normapy.csv"'
        df.to_csv(response, index=False)
        return response
    else:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="productos_normapy.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Productos')
        return response

def exportar_json(request):
    # Exporta los productos normalizados a un archivo JSON
    productos = list(Producto.objects.all().values('sku', 'nombre', 'precio', 'marca', 'stock'))
    if not productos:
        return HttpResponse("No hay productos para exportar.")
    # Crear carpeta de salida si no existe
    output_dir = os.path.join('media', 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    # Nombre de archivo dinámico
    fecha = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"productos_{fecha}.json"
    filepath = os.path.join(output_dir, filename)
    # Guardar JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        pyjson.dump(productos, f, ensure_ascii=False, indent=2)
    # Descargar el archivo
    return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)

def descargar_normalizado(request):
    formato = request.GET.get('formato', 'csv')
    productos = Producto.objects.all().values('sku', 'nombre', 'precio', 'marca', 'stock')
    df = pd.DataFrame(list(productos))

    if formato == 'json':
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="productos_normalizados.json"'
        response.write(df.to_json(orient='records', force_ascii=False))
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="productos_normalizados.csv"'
        df.to_csv(path_or_buffer=response, index=False)
    return response

def dashboard(request):
    total_productos = Producto.objects.count()
    total_importaciones = Importacion.objects.count()
    ultimo_archivo = Importacion.objects.order_by('-fecha').first()
    productos_por_marca = Producto.objects.values('marca').annotate(total=Count('id')).order_by('-total')
    usuario_top = Importacion.objects.values('usuario__username').annotate(total=Count('id')).order_by('-total').first()
    importaciones_por_mes = (
        Importacion.objects.extra(select={'mes': "strftime('%%Y-%%m', fecha)"}).values('mes')
        .annotate(total=Count('id')).order_by('mes')
    )

    return render(request, 'normapy/dashboard.html', {
        'total_productos': total_productos,
        'total_importaciones': total_importaciones,
        'ultimo_archivo': ultimo_archivo,
        'productos_por_marca': productos_por_marca,
        'usuario_top': usuario_top,
        'importaciones_por_mes': importaciones_por_mes,
    })

def historial_importaciones(request):
    from .models import Importacion
    historial = Importacion.objects.all().order_by('-fecha')
    return render(request, 'normapy/historial.html', {'historial': historial})

def productos_por_importacion(request, importacion_id):
    from .models import Producto
    productos = Producto.objects.filter(importacion_id=importacion_id)
    return render(request, 'normapy/productos_por_importacion.html', {'productos': productos, 'importacion_id': importacion_id})
