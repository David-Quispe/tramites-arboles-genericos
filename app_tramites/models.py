from django.db import models

# ============================================================
# ROL: BACKEND — Modelos de datos
# ============================================================

class NodoTramite(models.Model):
    nombre      = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    padre       = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='hijos'
    )
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


# ------------------------------------------------------------
# Catálogos
# ------------------------------------------------------------

class Carrera(models.Model):
    nombre      = models.CharField(max_length=200)
    codigo      = models.CharField(max_length=20, unique=True)
    duracion    = models.IntegerField(choices=[(2, '2 años'), (3, '3 años')])

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ------------------------------------------------------------
# Alumno
# ------------------------------------------------------------

CICLO_CHOICES = [
    (1, 'Ciclo I'), (2, 'Ciclo II'), (3, 'Ciclo III'),
    (4, 'Ciclo IV'), (5, 'Ciclo V'), (6, 'Ciclo VI'),
]

AÑO_CHOICES = [(1, '1er año'), (2, '2do año'), (3, '3er año')]

class Alumno(models.Model):
    dni         = models.CharField(max_length=8, unique=True)
    nombre      = models.CharField(max_length=200)
    apellido    = models.CharField(max_length=200)
    carrera     = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name='alumnos')
    anio        = models.IntegerField(choices=AÑO_CHOICES)
    ciclo       = models.IntegerField(choices=CICLO_CHOICES)
    activo      = models.BooleanField(default=True)
    fecha_ingreso = models.DateField()

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.dni} - {self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.apellido} {self.nombre}"


# ------------------------------------------------------------
# Pensiones
# ------------------------------------------------------------

MES_CHOICES = [
    (1,'Enero'),(2,'Febrero'),(3,'Marzo'),(4,'Abril'),
    (5,'Mayo'),(6,'Junio'),(7,'Julio'),(8,'Agosto'),
    (9,'Septiembre'),(10,'Octubre'),(11,'Noviembre'),(12,'Diciembre'),
]

ESTADO_PENSION = [
    ('pendiente', 'Pendiente'),
    ('pagado',    'Pagado'),
    ('vencido',   'Vencido'),
]

class Pension(models.Model):
    alumno      = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='pensiones')
    mes         = models.IntegerField(choices=MES_CHOICES)
    anio        = models.IntegerField()
    monto       = models.DecimalField(max_digits=8, decimal_places=2)
    estado      = models.CharField(max_length=20, choices=ESTADO_PENSION, default='pendiente')
    fecha_pago  = models.DateField(null=True, blank=True)
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ['-anio', '-mes']
        unique_together = ['alumno', 'mes', 'anio']

    def __str__(self):
        return f"{self.alumno.dni} - {self.get_mes_display()} {self.anio} [{self.estado}]"


# ------------------------------------------------------------
# Becas
# ------------------------------------------------------------

TIPO_BECA = [
    ('excelencia',  'Beca Excelencia'),
    ('necesidad',   'Beca por Necesidad'),
    ('deportiva',   'Beca Deportiva'),
    ('convenio',    'Beca por Convenio'),
]

ESTADO_BECA = [
    ('solicitada', 'Solicitada'),
    ('aprobada',   'Aprobada'),
    ('rechazada',  'Rechazada'),
    ('vigente',    'Vigente'),
    ('finalizada', 'Finalizada'),
]

class Beca(models.Model):
    alumno      = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='becas')
    tipo        = models.CharField(max_length=30, choices=TIPO_BECA)
    porcentaje  = models.IntegerField(help_text='Porcentaje de descuento (ej: 50, 100)')
    estado      = models.CharField(max_length=20, choices=ESTADO_BECA, default='solicitada')
    fecha_inicio = models.DateField()
    fecha_fin    = models.DateField(null=True, blank=True)
    observacion  = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.alumno.dni} - {self.get_tipo_display()} [{self.estado}]"


# ------------------------------------------------------------
# Documentos (Certificados y Títulos)
# ------------------------------------------------------------

TIPO_DOCUMENTO = [
    ('certificado_notas',   'Certificado de Notas'),
    ('certificado_estudios','Certificado de Estudios'),
    ('constancia',          'Constancia de Estudios'),
    ('titulo',              'Título Profesional'),
]

ESTADO_DOCUMENTO = [
    ('solicitado',  'Solicitado'),
    ('en_proceso',  'En Proceso'),
    ('listo',       'Listo para recoger'),
    ('entregado',   'Entregado'),
]

class Documento(models.Model):
    alumno          = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='documentos')
    tipo            = models.CharField(max_length=40, choices=TIPO_DOCUMENTO)
    estado          = models.CharField(max_length=20, choices=ESTADO_DOCUMENTO, default='solicitado')
    fecha_solicitud = models.DateField(auto_now_add=True)
    fecha_entrega   = models.DateField(null=True, blank=True)
    observacion     = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.alumno.dni} - {self.get_tipo_display()} [{self.estado}]"
