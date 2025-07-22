from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.importar_archivo, name='importar_archivo'),  # Página principal
    path('historial/', views.historial_importaciones, name='historial_importaciones'),
    path('productos/', views.listar_productos, name='listar_productos'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('exportar_productos/', views.exportar_productos, name='exportar_productos'),
    path('exportar_json/', views.exportar_json, name='exportar_json'),
    path('descargar_normalizado/', views.descargar_normalizado, name='descargar_normalizado'),
]

# Servir archivos media y estáticos en desarrollo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 