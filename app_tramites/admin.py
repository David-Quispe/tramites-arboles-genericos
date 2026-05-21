from django.contrib import admin
from .models import NodoTramite, Carrera, Alumno, Pension, Beca, Documento

@admin.register(NodoTramite)
class NodoTramiteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'padre', 'orden']
    list_filter = ['padre']
    search_fields = ['nombre']

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'duracion']
    search_fields = ['nombre', 'codigo']

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ['dni', 'apellido', 'nombre', 'carrera', 'anio', 'ciclo', 'activo']
    list_filter = ['carrera', 'activo', 'anio']
    search_fields = ['dni', 'nombre', 'apellido']

@admin.register(Pension)
class PensionAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'mes', 'anio', 'monto', 'estado', 'fecha_pago']
    list_filter = ['estado', 'anio']
    search_fields = ['alumno__dni', 'alumno__apellido']

@admin.register(Beca)
class BecaAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'tipo', 'porcentaje', 'estado', 'fecha_inicio', 'fecha_fin']
    list_filter = ['tipo', 'estado']
    search_fields = ['alumno__dni', 'alumno__apellido']

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'tipo', 'estado', 'fecha_solicitud', 'fecha_entrega']
    list_filter = ['tipo', 'estado']
    search_fields = ['alumno__dni', 'alumno__apellido']
