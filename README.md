# NormaPy

**Entrega de Python - Johaina Chavez**

NormaPy es una aplicación web desarrollada con Django que permite importar, normalizar y gestionar catálogos de productos provenientes de diferentes plataformas de e-commerce (como MercadoLibre, TiendaNube, WooCommerce, Shopify, PrestaShop, entre otras). El sistema facilita la integración de datos, el mapeo automático de columnas, la validación y la exportación de productos en formatos estándar.

---

## Características principales

- **Importación de archivos**: Sube archivos CSV o Excel con catálogos de productos de cualquier proveedor o plataforma.
- **Mapeo automático de columnas**: Detecta y asocia automáticamente los nombres de columnas gracias a un sistema de sinónimos configurable.
- **Validación y limpieza de datos**: El sistema revisa y limpia los datos, mostrando advertencias si hay problemas.
- **Vista previa antes de importar**: Permite revisar cómo quedarán los datos antes de guardarlos en la base de datos.
- **Historial de importaciones**: Lleva un registro de todos los archivos importados y sus estadísticas.
- **Exportación flexible**: Descarga los productos normalizados en formato Excel, CSV o JSON.
- **Dashboard**: Visualiza estadísticas clave del catálogo y las importaciones.

---

## ¿Cómo usar NormaPy?

1. **Sube un archivo**  
   Ingresa a la página principal y selecciona tu archivo CSV o Excel para importar productos.

2. **Revisa la vista previa**  
   El sistema te mostrará cómo se mapearon las columnas y los primeros productos detectados.

3. **Confirma la importación**  
   Si todo es correcto, confirma para guardar los productos en la base de datos.

4. **Gestiona y exporta productos**  
   Accede a la sección de productos para ver, filtrar y exportar el catálogo en el formato que prefieras.

5. **Consulta el historial y el dashboard**  
   Revisa el historial de importaciones y las estadísticas generales del sistema.

---

## Ejemplo de archivo compatible

**CSV/Excel en español:**
```
sku,nombre,precio,marca,stock
b1,Producto Uno,15.0,MarcaA,8
b2,Producto Dos,25.0,MarcaB,12
```

**CSV/Excel en inglés:**
```
sku,name,price,brand,stock
a1,Product One,10.5,BrandX,5
a2,Product Two,20.0,BrandY,10
```

**Archivo de MercadoLibre:**
```
product_id,title,price,manufacturer,available_stock
ml1,ML Producto,99.9,MLBrand,50
```

El sistema detecta automáticamente los nombres de columna gracias al archivo `sinonimos.json`.

---

## Instalación y ejecución

1. Clona el repositorio:
   ```
   git clone <URL-del-repositorio>
   cd NormaPy
   ```

2. Instala las dependencias definidas en `requirements.txt`:
   ```
   pip install -r requirements.txt
   ```

3. Realiza las migraciones:
   ```
   python manage.py migrate
   ```

4. Inicia el servidor de desarrollo:
   ```
   python manage.py runserver
   ```

5. Accede a la aplicación en tu navegador en `http://127.0.0.1:8000/`

---

## Pruebas automatizadas

Ejecuta las pruebas con:
```
python manage.py test normapy.tests
```

---

## Personalización

- Puedes editar `normapy/mapeo/sinonimos.json` para agregar más sinónimos o adaptar el sistema a nuevos proveedores.
- El código es extensible para agregar nuevas funcionalidades según tus necesidades.

---

**NormaPy** facilita la integración y gestión de catálogos de productos de cualquier plataforma de e-commerce de Latinoamérica y el mundo.