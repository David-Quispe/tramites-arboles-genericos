"""
Script para poblar la BD con datos de ejemplo.
Ejecutar con: python manage.py shell < seed.py
"""
from app_tramites.models import NodoTramite

NodoTramite.objects.all().delete()

raiz = NodoTramite.objects.create(nombre="Trámites Administrativos", descripcion="Raíz del sistema de trámites", orden=0)

ac = NodoTramite.objects.create(nombre="Académicos",    descripcion="Trámites de índole académico",  padre=raiz, orden=1)
ec = NodoTramite.objects.create(nombre="Económicos",    descripcion="Trámites financieros",           padre=raiz, orden=2)
dc = NodoTramite.objects.create(nombre="Documentarios", descripcion="Emisión de documentos oficiales",padre=raiz, orden=3)

NodoTramite.objects.create(nombre="Matrícula",      descripcion="Proceso de matrícula regular", padre=ac, orden=1)
NodoTramite.objects.create(nombre="Convalidaciones",descripcion="Convalidación de cursos",      padre=ac, orden=2)
NodoTramite.objects.create(nombre="Constancias",    descripcion="Constancias de estudios",      padre=ac, orden=3)

NodoTramite.objects.create(nombre="Pensiones", descripcion="Pago y fraccionamiento de pensiones", padre=ec, orden=1)
NodoTramite.objects.create(nombre="Becas",     descripcion="Solicitud de becas y descuentos",     padre=ec, orden=2)

NodoTramite.objects.create(nombre="Certificados", descripcion="Certificados de notas",  padre=dc, orden=1)
NodoTramite.objects.create(nombre="Títulos",      descripcion="Proceso de titulación",  padre=dc, orden=2)

print(f"✅ BD poblada: {NodoTramite.objects.count()} nodos creados")
