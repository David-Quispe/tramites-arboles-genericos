from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'),

    # Nodos del árbol
    path('nodos/nuevo/',                    views.nodo_nuevo,   name='nodo_nuevo'),
    path('nodos/nuevo/<int:padre_id>/',     views.nodo_nuevo,   name='nodo_hijo_nuevo'),
    path('nodos/<int:pk>/editar/',          views.nodo_editar,  name='nodo_editar'),
    path('nodos/<int:pk>/eliminar/',        views.nodo_eliminar,name='nodo_eliminar'),

    # Alumnos
    path('alumnos/',                views.alumnos_lista,  name='alumnos_lista'),
    path('alumnos/nuevo/',          views.alumno_nuevo,   name='alumno_nuevo'),
    path('alumnos/<str:dni>/',      views.alumno_detalle, name='alumno_detalle'),
    path('alumnos/<str:dni>/editar/', views.alumno_editar, name='alumno_editar'),

    # Pensiones
    path('alumnos/<str:dni>/pension/nueva/', views.pension_nueva,  name='pension_nueva'),
    path('pension/<int:pk>/editar/',         views.pension_editar, name='pension_editar'),

    # Becas
    path('alumnos/<str:dni>/beca/nueva/', views.beca_nueva,  name='beca_nueva'),
    path('beca/<int:pk>/editar/',         views.beca_editar, name='beca_editar'),

    # Documentos
    path('alumnos/<str:dni>/documento/nuevo/', views.documento_nuevo,  name='documento_nuevo'),
    path('documento/<int:pk>/editar/',         views.documento_editar, name='documento_editar'),

    # Carreras
    path('carreras/',            views.carreras_lista,   name='carreras_lista'),
    path('carreras/nueva/',      views.carrera_nueva,    name='carrera_nueva'),
    path('carreras/<str:codigo>/', views.carrera_detalle,  name='carrera_detalle'),

    # Eliminar
    path('alumnos/<str:dni>/eliminar/',        views.alumno_eliminar,    name='alumno_eliminar'),
    path('pension/<int:pk>/eliminar/',         views.pension_eliminar,   name='pension_eliminar'),
    path('beca/<int:pk>/eliminar/',            views.beca_eliminar,      name='beca_eliminar'),
    path('documento/<int:pk>/eliminar/',       views.documento_eliminar, name='documento_eliminar'),
    path('carreras/<str:codigo>/eliminar/',    views.carrera_eliminar,   name='carrera_eliminar'),

    # API árbol
    path('api/arbol/',                     views.api_arbol,        name='api_arbol'),
    path('api/nodo/<int:nodo_id>/',        views.api_nodo,         name='api_nodo'),
    path('api/nodo/<int:nodo_id>/altura/', views.api_altura,       name='api_altura'),
    path('api/buscar/',                    views.api_buscar,        name='api_buscar'),
    path('api/recorrido/',                 views.api_recorrido,     name='api_recorrido'),
    path('api/estadisticas/',              views.api_estadisticas,  name='api_estadisticas'),
]
