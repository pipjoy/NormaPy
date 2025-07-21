from django.urls import path
from . import views

urlpatterns = [
    path('', views.importar_archivo, name='importar_archivo'),
    path('productos/', views.listar_productos, name='listar_productos'),
    path('productos/exportar/', views.exportar_productos, name='exportar_productos'),
    path('productos/exportar_json/', views.exportar_json, name='exportar_json'),
    path('productos/descargar/', views.descargar_normalizado, name='descargar_normalizado'),
    path('importaciones/', views.historial_importaciones, name='historial_importaciones'),
    path('importaciones/<int:importacion_id>/productos/', views.productos_por_importacion, name='productos_por_importacion'),
    path('dashboard/', views.dashboard, name='dashboard'),
] 