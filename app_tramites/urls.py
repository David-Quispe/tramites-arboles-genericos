from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'),

    # Nodos del árbol
    path('nodos/nuevo/',                views.nodo_nuevo,    name='nodo_nuevo'),
    path('nodos/nuevo/<int:padre_id>/', views.nodo_nuevo,    name='nodo_hijo_nuevo'),
    path('nodos/<int:pk>/editar/',      views.nodo_editar,   name='nodo_editar'),
    path('nodos/<int:pk>/eliminar/',    views.nodo_eliminar, name='nodo_eliminar'),

    # Alumnos
    path('alumnos/',                      views.alumnos_lista,  name='alumnos_lista'),
    path('alumnos/nuevo/',                views.alumno_nuevo,   name='alumno_nuevo'),
    path('alumnos/<str:dni>/',            views.alumno_detalle, name='alumno_detalle'),
    path('alumnos/<str:dni>/editar/',     views.alumno_editar,  name='alumno_editar'),
    path('alumnos/<str:dni>/eliminar/',   views.alumno_eliminar,name='alumno_eliminar'),

    # Pensiones
    path('alumnos/<str:dni>/pension/nueva/', views.pension_nueva,   name='pension_nueva'),
    path('pension/<int:pk>/editar/',         views.pension_editar,  name='pension_editar'),
    path('pension/<int:pk>/eliminar/',       views.pension_eliminar,name='pension_eliminar'),

    # Becas
    path('alumnos/<str:dni>/beca/nueva/', views.beca_nueva,   name='beca_nueva'),
    path('beca/<int:pk>/editar/',         views.beca_editar,  name='beca_editar'),
    path('beca/<int:pk>/eliminar/',       views.beca_eliminar,name='beca_eliminar'),

    # Documentos
    path('alumnos/<str:dni>/documento/nuevo/', views.documento_nuevo,   name='documento_nuevo'),
    path('documento/<int:pk>/editar/',         views.documento_editar,  name='documento_editar'),
    path('documento/<int:pk>/eliminar/',       views.documento_eliminar,name='documento_eliminar'),

    # Carreras
    path('carreras/',                      views.carreras_lista,  name='carreras_lista'),
    path('carreras/nueva/',                views.carrera_nueva,   name='carrera_nueva'),
    path('carreras/<str:codigo>/',         views.carrera_detalle, name='carrera_detalle'),
    path('carreras/<str:codigo>/eliminar/',views.carrera_eliminar,name='carrera_eliminar'),

    # ── DOCENTES ──────────────────────────────────────────
    path('docentes/',                               views.docentes_lista,      name='docentes_lista'),
    path('docentes/nuevo/',                         views.docente_nuevo,       name='docente_nuevo'),
    path('docentes/<str:dni>/',                     views.docente_detalle,     name='docente_detalle'),
    path('docentes/<str:dni>/editar/',              views.docente_editar,      name='docente_editar'),
    path('docentes/<str:dni>/eliminar/',            views.docente_eliminar,    name='docente_eliminar'),
    path('docentes/asignar/<int:cursocarrera_id>/', views.asignar_docente,     name='asignar_docente'),
    path('carreras/<str:codigo>/malla/agregar/',    views.malla_agregar_curso, name='malla_agregar_curso'),
    path('malla/<int:cursocarrera_id>/quitar/',     views.malla_quitar_curso,  name='malla_quitar_curso'),

    # ── FINANZAS ──────────────────────────────────────────
    path('finanzas/',                                 views.finanzas_dashboard, name='finanzas_dashboard'),
    path('finanzas/alumno/<str:dni>/',                views.finanzas_alumno,    name='finanzas_alumno'),
    path('finanzas/alumno/<str:dni>/pago/nuevo/',     views.pago_nuevo,         name='pago_nuevo'),
    path('finanzas/pago/<int:pk>/editar/',            views.pago_editar,        name='pago_editar'),
    path('finanzas/pago/<int:pk>/anular/',            views.pago_anular,        name='pago_anular'),
    path('finanzas/pensiones-vencidas/',              views.pensiones_vencidas, name='pensiones_vencidas'),

    # ── NOTIFICACIONES ────────────────────────────────────
    path('notificaciones/',                        views.notificaciones,              name='notificaciones'),
    path('notificaciones/<int:pk>/leida/',         views.notificacion_marcar_leida,   name='notificacion_leida'),
    path('notificaciones/marcar-todas/',           views.notificaciones_marcar_todas, name='notificaciones_todas'),

    # ── COMUNICADOS ───────────────────────────────────────
    path('comunicados/',        views.comunicados_lista, name='comunicados_lista'),
    path('comunicados/nuevo/',  views.comunicado_nuevo,  name='comunicado_nuevo'),

    # API árbol
    path('api/arbol/',                     views.api_arbol,        name='api_arbol'),
    path('api/nodo/<int:nodo_id>/',        views.api_nodo,         name='api_nodo'),
    path('api/nodo/<int:nodo_id>/altura/', views.api_altura,       name='api_altura'),
    path('api/buscar/',                    views.api_buscar,        name='api_buscar'),
    path('api/recorrido/',                 views.api_recorrido,     name='api_recorrido'),
    path('api/estadisticas/',              views.api_estadisticas,  name='api_estadisticas'),
    path('api/mover/',                     views.api_mover_nodo,    name='api_mover_nodo'),
    path('api/ordenar/',                   views.api_ordenar_hijos, name='api_ordenar_hijos'),
]
