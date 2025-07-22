"""
Vista para subir archivos y ejecutar la normalización de datos.
"""
import pandas as pd
from django.shortcuts import render, redirect
from .forms import UploadForm
from .models import Producto, Importacion
import json
import os
from django.db.models import Count
from django.http import HttpResponse
from .utils.limpieza import limpieza_basica
from .mapeo.normalizador import mapear_columnas  # Usar la versión extendida
from .mapeo.validacion import limpiar_columnas
from .utils.logger import logger
import json as pyjson
from django.utils import timezone
from django.http import FileResponse
from unidecode import unidecode
from datetime import datetime
from django.db.models import Avg, Sum

# Cargar sinonimos.json desde disco
SINONIMOS_PATH = os.path.join(os.path.dirname(__file__), 'mapeo', 'sinonimos.json')
with open(SINONIMOS_PATH, encoding='utf-8') as f:
    sinonimos = json.load(f)

def renombrar_columnas(df, mapeo):
    # mapeo: {'sku': 'sku', 'name': 'nombre', ...}
    columnas_actuales = df.columns.tolist()
    columnas_a_renombrar = {}
    for campo, original in mapeo.items():  # campo = interno (español), original = nombre en archivo
        if original in columnas_actuales:
            columnas_a_renombrar[original] = campo  # renombra a español
        else:
            logger.warning(
                "\u26a0 Columna mapeada '%s' no encontrada en el archivo.",
                original,
            )
            raise ValueError(
                f"Columna mapeada '{original}' no encontrada en el archivo."
            )
    df = df.rename(columns=columnas_a_renombrar)
    logger.info("Columnas despu\u00e9s de renombrar: %s", df.columns.tolist())
    return df

def limpiar_datos(df):
    """Convierte los valores de las columnas a los tipos correctos (float o int)."""
    if 'nombre' in df.columns:
        df['nombre'] = df['nombre'].astype(str).str.lower().apply(lambda x: unidecode(x.strip()))
    if 'marca' in df.columns:
        df['marca'] = df['marca'].astype(str).str.lower().apply(lambda x: unidecode(x.strip()))
    if 'precio' in df.columns:
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce').fillna(0)
    if 'stock' in df.columns:
        df['stock'] = pd.to_numeric(df['stock'], errors='coerce').fillna(0).astype(int)
    return df

def mostrar_estadisticas(df, archivo_nombre=None):
    total_productos = len(df)
    precio_promedio = df['precio'].mean() if 'precio' in df.columns else 0
    stock_total = df['stock'].sum() if 'stock' in df.columns else 0
    skus_generados = df['sku'].apply(lambda x: str(x).startswith("AUTO-")).sum() if 'sku' in df.columns else 0
    archivo_nombre = archivo_nombre or "Desconocido"
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        'total_productos': total_productos,
        'precio_promedio': precio_promedio,
        'stock_total': stock_total,
        'skus_generados': skus_generados,
        'archivo_nombre': archivo_nombre,
        'fecha_hora': fecha_hora,
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
    logger.info("\ud83d\uddfe\ufe0f Mapeo generado: %s", mapeo)
    return True


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
    logger.info("[DEPURACIÓN] Primeras filas del archivo:")
    logger.info("%s", df.head().to_string())
    logger.info("[DEPURACIÓN] Columnas leídas: %s", df.columns.tolist())
    if mapeo is not None:
        logger.info("[DEPURACIÓN] Mapeo generado: %s", mapeo)
        for campo, col in mapeo.items():
            if col not in df.columns:
                logger.warning(
                    "[DEPURACIÓN][ADVERTENCIA] Columna mapeada '%s' no encontrada en el DataFrame tras renombrar.",
                    col,
                )

def importar_archivo(request):
    hojas = []
    df = None
    preview_data = []
    mapeo = {}
    acciones = {}
    estadisticas = None
    mensaje = None
    form = UploadForm(request.POST, request.FILES)

    if request.method == 'POST' and request.POST.get('confirmar') == '1':
        # Confirmación de la importación: leer datos almacenados en sesión
        df_json = request.session.get('import_df')
        if df_json:
            df = pd.read_json(df_json)
            from django.core.files.base import ContentFile
            csv_content = df.to_csv(index=False)
            nombre_archivo = request.session.get('archivo_nombre', 'importacion.csv')
            archivo = ContentFile(csv_content.encode('utf-8'), name=nombre_archivo)
            importacion = Importacion.objects.create(
                archivo=archivo,
                nombre_original=nombre_archivo,
                cantidad_productos=0,
                columnas_detectadas=", ".join(df.columns.tolist()),
                se_generaron_skus=any(df['sku'].astype(str).str.startswith('AUTO')),
            )

            registros = df.to_dict(orient='records')
            skus = [r.get("sku") for r in registros]
            existentes = Producto.objects.filter(sku__in=skus)
            existentes_map = {p.sku: p for p in existentes}
            productos_nuevos = []
            productos_actualizar = []

            for fila in registros:
                sku = fila.get("sku")
                if sku in existentes_map:
                    prod = existentes_map[sku]
                    prod.nombre = fila.get("nombre")
                    prod.precio = fila.get("precio")
                    prod.stock = fila.get("stock")
                    prod.marca = fila.get("marca")
                    prod.importacion = importacion
                    productos_actualizar.append(prod)
                else:
                    productos_nuevos.append(
                        Producto(
                            importacion=importacion,
                            sku=sku,
                            nombre=fila.get("nombre"),
                            precio=fila.get("precio"),
                            stock=fila.get("stock"),
                            marca=fila.get("marca"),
                        )
                    )

            if productos_nuevos:
                Producto.objects.bulk_create(productos_nuevos)
            if productos_actualizar:
                Producto.objects.bulk_update(
                    productos_actualizar,
                    ["nombre", "precio", "stock", "marca", "importacion"],
                )

            procesados = len(productos_nuevos) + len(productos_actualizar)
            importacion.cantidad_productos = procesados
            importacion.save()
            request.session.pop('import_df', None)
            request.session.pop('archivo_nombre', None)
            return redirect('historial_importaciones')
        else:
            mensaje = "No hay datos para importar."

    elif request.method == 'POST':
        archivo = request.FILES.get('archivo')
        hoja_seleccionada = request.POST.get('hoja')
        if archivo:
            if archivo.name.endswith('.xlsx'):
                excel_file = pd.ExcelFile(archivo)
                hojas = excel_file.sheet_names
                if hoja_seleccionada:
                    df = excel_file.parse(hoja_seleccionada)
                else:
                    df = excel_file.parse(hojas[0])
            elif archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                mensaje = "El archivo debe ser CSV o Excel."
        elif hoja_seleccionada and 'archivo' not in request.FILES:
            mensaje = "Por favor, sube el archivo nuevamente para seleccionar otra hoja."

        if df is not None:
            df = limpiar_columnas(df)
            mapeo = mapear_columnas(df, sinonimos['global'], sinonimos.get('providers', {}))
            df = renombrar_columnas(df, mapeo)
            required_columns = ['sku', 'nombre', 'precio', 'stock']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                mensaje = f"Faltan las siguientes columnas obligatorias: {', '.join(missing_columns)}"
            else:
                df = limpiar_datos(df)
                df['marca'] = df['marca'].fillna('Sin Marca') if 'marca' in df.columns else 'Sin Marca'
                df['nombre'] = df['nombre'].fillna('Sin Nombre')
                df['sku'] = df['sku'].fillna('SIN-SKU')
                df_limpio = df.copy()
                # Guardar el DataFrame en la sesión para la confirmación posterior
                request.session['import_df'] = df_limpio.to_json(orient='records')
                request.session['archivo_nombre'] = archivo.name
                preview_data = df_limpio.head(3).to_dict(orient='records')
                estadisticas = mostrar_estadisticas(df_limpio, archivo_nombre=archivo.name)

        return render(
            request,
            'normapy/preview.html',
            {
                'form': form,
                'hojas': hojas,
                'mapeo': mapeo,
                'acciones': acciones,
                'preview': preview_data,
                'mensaje': mensaje,
                'estadisticas': estadisticas,
            },
        )

    return render(request, 'normapy/preview.html', {'form': form, 'hojas': hojas})

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

# Dashboard mejorado
def dashboard(request):
    total_importaciones = Importacion.objects.count()
    productos = Producto.objects.count()
    total_stock = Producto.objects.aggregate(Sum('stock'))['stock__sum'] or 0
    precio_promedio = Producto.objects.aggregate(Avg('precio'))['precio__avg'] or 0
    skus_generados = Producto.objects.filter(sku__startswith='AUTO').count()
    return render(request, 'normapy/dashboard.html', {
        'total_importaciones': total_importaciones,
        'productos': productos,
        'total_stock': total_stock,
        'precio_promedio': precio_promedio,
        'skus_generados': skus_generados
    })

def historial_importaciones(request):
    historial = Importacion.objects.all().order_by('-fecha_subida')
    return render(request, 'normapy/historial.html', {'historial': historial})

def productos_por_importacion(request, importacion_id):
    productos = Producto.objects.filter(importacion_id=importacion_id)
    return render(request, 'normapy/productos_por_importacion.html', {'productos': productos, 'importacion_id': importacion_id})

def bienvenida(request):
    return render(request, 'normapy/bienvenida.html')
