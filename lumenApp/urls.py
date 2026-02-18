from . import views
from django.urls import path

from .views import *


urlpatterns = [
   path('', views.principal, name='principal' ),
   path('fichas_lista/', views.fichas_lista, name='fichas_lista' ),
   path('ficha/<int:pk>/', FichaDetalleView.as_view(), name='detalle_hermano'),
   path('ficha/<int:pk>/editar/', views.FichaUpdateView.as_view(), name='editar_hermano'),
   path('ficha/crear/', views.FichaCreateView.as_view(), name='crear_hermano'),
   path('ficha/<int:pk>/eliminar/', views.FichaDeleteView.as_view(), name='eliminar_hermano'),
   path('ficha/<int:pk>/asignar_rol/', views.asignar_rol, name='asignar_rol'),
   path('ficha/<int:pk>/eliminar_rol/', views.eliminar_rol, name='eliminar_rol'),
   path('cuotas/<int:hermano_pk>/', views.cuota_lista, name='cuota_lista'),
   path('hermano/<int:hermano_pk>/cuota/crear/', crear_cuota, name='crear_cuota'),
   path('cuota/crear-masiva/', views.crear_cuota_masiva, name='crear_cuota_masiva'),
   path('cuota/<int:pk>/eliminar/', CuotaDeleteView.as_view(), name='eliminar_cuota'),
   path('cuota/<int:pk>/editar/', CuotaUpdateView.as_view(), name='editar_cuota'),
   path('cultos/', CultoListView.as_view(), name='cultos_lista'),
   path('culto/<int:pk>/', CultoDetailView.as_view(), name='detalle_culto'),
   path('culto/crear/', CultoCreateView.as_view(), name='crear_culto'),
   path('culto/<int:pk>/eliminar/', CultoDeleteView.as_view(), name='eliminar_culto'),
   path('culto/<int:culto_pk>/asignar_participante/', views.asignar_participante, name='asignar_participante'),
   path('estadisticas', EstadisticasTemplateView.as_view(), name='estadisticas'),
   path('registro/', RegistroView.as_view(), name='registro'),

]
