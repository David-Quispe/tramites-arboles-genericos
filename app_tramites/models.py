from django.db import models
from django.utils import timezone

# ============================================================
# ROL: BACKEND — Modelos de datos
# ============================================================

TIPO_NODO_CHOICES = [
    ('categoria',  'Categoría'),
    ('tramite',    'Trámite'),
    ('documento',  'Documento'),
    ('accion',     'Acción'),
]

class NodoTramite(models.Model):
    nombre      = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo        = models.CharField(max_length=20, choices=TIPO_NODO_CHOICES, default='categoria')
    padre       = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='hijos')
    orden       = models.IntegerField(default=0)
    enlace      = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    def es_hoja(self):
        return not self.hijos.exists()

    def es_raiz(self):
        return self.padre is None

    def profundidad(self):
        depth, nodo = 0, self
        while nodo.padre is not None:
            depth += 1
            nodo = nodo.padre
        return depth

    def get_ancestros(self):
        ancestros, nodo = [], self.padre
        while nodo is not None:
            ancestros.insert(0, nodo)
            nodo = nodo.padre
        return ancestros

    def get_descendientes_ids(self):
        ids = set()
        stack = list(self.hijos.values_list('id', flat=True))
        while stack:
            nid = stack.pop()
            ids.add(nid)
            stack.extend(NodoTramite.objects.filter(padre_id=nid).values_list('id', flat=True))
        return ids

    def contar_hijos_directos(self):
        return self.hijos.count()

    @classmethod
    def validar_movimiento(cls, nodo_id, nuevo_padre_id):
        if nodo_id == nuevo_padre_id:
            return False, "Un nodo no puede ser hijo de sí mismo."
        nodo = cls.objects.get(pk=nodo_id)
        if nodo.padre is None:
            return False, "No se puede mover la raíz del árbol."
        if nuevo_padre_id in nodo.get_descendientes_ids():
            return False, "No se puede mover un nodo dentro de su propio subárbol."
        return True, "OK"


# ============================================================
# DOCENTE
# ============================================================

ESPECIALIDAD_CHOICES = [
    ('informatica',    'Informática'),
    ('administracion', 'Administración'),
    ('contabilidad',   'Contabilidad'),
    ('electronica',    'Electrónica'),
    ('mecanica',       'Mecánica'),
    ('enfermeria',     'Enfermería'),
    ('otro',           'Otro'),
]

class Docente(models.Model):
    dni                  = models.CharField(max_length=8, unique=True)
    nombre               = models.CharField(max_length=200)
    apellido             = models.CharField(max_length=200)
    especialidad         = models.CharField(max_length=30, choices=ESPECIALIDAD_CHOICES, default='otro')
    correo_institucional = models.EmailField(unique=True, blank=True, null=True)
    telefono             = models.CharField(max_length=15, blank=True)
    activo               = models.BooleanField(default=True)
    fecha_ingreso        = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.apellido} {self.nombre}"


# ============================================================
# CARRERA
# ============================================================

class Carrera(models.Model):
    nombre   = models.CharField(max_length=200)
    codigo   = models.CharField(max_length=20, unique=True)
    duracion = models.IntegerField(choices=[(2, '2 años'), (3, '3 años')])

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ============================================================
# CURSO
# ============================================================

class Curso(models.Model):
    codigo      = models.CharField(max_length=20, unique=True)
    nombre      = models.CharField(max_length=200)
    creditos    = models.IntegerField(default=3)
    horas_teoria   = models.IntegerField(default=2)
    horas_practica = models.IntegerField(default=2)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ============================================================
# CURSO POR CARRERA (malla curricular)
# ============================================================

class CursoCarrera(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='malla')
    curso   = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='carreras')
    ciclo   = models.IntegerField(choices=[
        (1,'Ciclo I'),(2,'Ciclo II'),(3,'Ciclo III'),
        (4,'Ciclo IV'),(5,'Ciclo V'),(6,'Ciclo VI'),
    ])
    docente = models.ForeignKey(Docente, null=True, blank=True, on_delete=models.SET_NULL, related_name='cursos_asignados')

    class Meta:
        ordering  = ['ciclo', 'curso__nombre']
        unique_together = ['carrera', 'curso', 'ciclo']

    def __str__(self):
        return f"{self.carrera.codigo} | C{self.ciclo} | {self.curso.nombre}"


# ============================================================
# ALUMNO
# ============================================================

CICLO_CHOICES = [
    (1,'Ciclo I'),(2,'Ciclo II'),(3,'Ciclo III'),
    (4,'Ciclo IV'),(5,'Ciclo V'),(6,'Ciclo VI'),
]
AÑO_CHOICES = [(1,'1er año'),(2,'2do año'),(3,'3er año')]

class Alumno(models.Model):
    dni                  = models.CharField(max_length=8, unique=True)
    nombre               = models.CharField(max_length=200)
    apellido             = models.CharField(max_length=200)
    carrera              = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name='alumnos')
    anio                 = models.IntegerField(choices=AÑO_CHOICES)
    ciclo                = models.IntegerField(choices=CICLO_CHOICES)
    activo               = models.BooleanField(default=True)
    fecha_ingreso        = models.DateField()
    correo_institucional = models.EmailField(unique=True, blank=True, null=True)
    telefono             = models.CharField(max_length=15, blank=True)
    direccion            = models.CharField(max_length=300, blank=True)
    fecha_nacimiento     = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.dni} - {self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.apellido} {self.nombre}"


# ============================================================
# MATRÍCULA
# ============================================================

ESTADO_MATRICULA = [
    ('activa',     'Activa'),
    ('retirada',   'Retirada'),
    ('observada',  'Observada'),
    ('finalizada', 'Finalizada'),
]

PERIODO_CHOICES = [
    ('2024-I','2024-I'),('2024-II','2024-II'),
    ('2025-I','2025-I'),('2025-II','2025-II'),
    ('2026-I','2026-I'),('2026-II','2026-II'),
]

class Matricula(models.Model):
    alumno        = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='matriculas')
    periodo       = models.CharField(max_length=10, choices=PERIODO_CHOICES)
    ciclo         = models.IntegerField(choices=CICLO_CHOICES)
    estado        = models.CharField(max_length=20, choices=ESTADO_MATRICULA, default='activa')
    fecha_registro= models.DateField(auto_now_add=True)
    observacion   = models.TextField(blank=True)
    cursos        = models.ManyToManyField(CursoCarrera, blank=True, related_name='matriculas')
    nodo_tramite  = models.ForeignKey(NodoTramite, null=True, blank=True, on_delete=models.SET_NULL, related_name='matriculas_asociadas')

    class Meta:
        ordering = ['-periodo']
        unique_together = ['alumno', 'periodo']

    def __str__(self):
        return f"{self.alumno.dni} | {self.periodo} | {self.get_estado_display()}"

    def save(self, *args, **kwargs):
        if not self.nodo_tramite:
            self.nodo_tramite = NodoTramite.objects.filter(nombre__iexact="Matrícula").first()
        super().save(*args, **kwargs)


# ============================================================
# NOTAS
# ============================================================

class Nota(models.Model):
    matricula   = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='notas')
    curso       = models.ForeignKey(CursoCarrera, on_delete=models.CASCADE, related_name='notas')
    nota_p1     = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name='Parcial 1')
    nota_p2     = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name='Parcial 2')
    nota_final  = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name='Final')
    promedio    = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    aprobado    = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['curso__curso__nombre']
        unique_together = ['matricula', 'curso']

    def __str__(self):
        return f"{self.matricula.alumno.dni} | {self.curso.curso.nombre} | {self.promedio}"

    def calcular_promedio(self):
        notas = [n for n in [self.nota_p1, self.nota_p2, self.nota_final] if n is not None]
        if notas:
            self.promedio = sum(notas) / len(notas)
            self.aprobado = self.promedio >= 11
        return self.promedio

    def save(self, *args, **kwargs):
        self.calcular_promedio()
        super().save(*args, **kwargs)


# ============================================================
# PENSIONES
# ============================================================

MES_CHOICES = [
    (1,'Enero'),(2,'Febrero'),(3,'Marzo'),(4,'Abril'),
    (5,'Mayo'),(6,'Junio'),(7,'Julio'),(8,'Agosto'),
    (9,'Septiembre'),(10,'Octubre'),(11,'Noviembre'),(12,'Diciembre'),
]
ESTADO_PENSION = [
    ('pendiente','Pendiente'),
    ('pagado',   'Pagado'),
    ('vencido',  'Vencido'),
]

class Pension(models.Model):
    alumno      = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='pensiones')
    mes         = models.IntegerField(choices=MES_CHOICES)
    anio        = models.IntegerField()
    monto       = models.DecimalField(max_digits=8, decimal_places=2)
    estado      = models.CharField(max_length=20, choices=ESTADO_PENSION, default='pendiente')
    fecha_pago  = models.DateField(null=True, blank=True)
    observacion = models.TextField(blank=True)
    nodo_tramite = models.ForeignKey(NodoTramite, null=True, blank=True, on_delete=models.SET_NULL, related_name='pensiones_asociadas')

    class Meta:
        ordering = ['-anio', '-mes']
        unique_together = ['alumno', 'mes', 'anio']

    def __str__(self):
        return f"{self.alumno.dni} - {self.get_mes_display()} {self.anio} [{self.estado}]"

    def save(self, *args, **kwargs):
        if not self.nodo_tramite:
            self.nodo_tramite = NodoTramite.objects.filter(nombre__iexact="Pensiones").first()
        super().save(*args, **kwargs)

    @property
    def esta_vencida(self):
        from datetime import date
        hoy = date.today()
        if self.estado == 'pendiente':
            ultimo_dia = date(self.anio, self.mes, 28)
            return hoy > ultimo_dia
        return self.estado == 'vencido'


# ============================================================
# PAGOS / FINANZAS
# ============================================================

TIPO_PAGO = [
    ('pension',      'Pensión'),
    ('matricula',    'Matrícula'),
    ('derecho',      'Derecho de examen'),
    ('certificado',  'Certificado'),
    ('otro',         'Otro'),
]
METODO_PAGO = [
    ('efectivo',     'Efectivo'),
    ('transferencia','Transferencia bancaria'),
    ('pos',          'POS / Tarjeta'),
    ('yape',         'Yape / Plin'),
]
ESTADO_PAGO = [
    ('pendiente',  'Pendiente'),
    ('completado', 'Completado'),
    ('anulado',    'Anulado'),
]

class Pago(models.Model):
    alumno        = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='pagos')
    tipo          = models.CharField(max_length=20, choices=TIPO_PAGO)
    concepto      = models.CharField(max_length=300)
    monto         = models.DecimalField(max_digits=9, decimal_places=2)
    metodo        = models.CharField(max_length=20, choices=METODO_PAGO, default='efectivo')
    estado        = models.CharField(max_length=20, choices=ESTADO_PAGO, default='pendiente')
    fecha         = models.DateField(default=timezone.now)
    num_operacion = models.CharField(max_length=50, blank=True, verbose_name='N° operación')
    observacion   = models.TextField(blank=True)
    # Relación opcional con pensión
    pension       = models.OneToOneField(Pension, null=True, blank=True, on_delete=models.SET_NULL, related_name='pago')

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.alumno.dni} | {self.get_tipo_display()} | S/{self.monto} | {self.get_estado_display()}"


# ============================================================
# BECAS
# ============================================================

TIPO_BECA = [
    ('excelencia','Beca Excelencia'),
    ('necesidad', 'Beca por Necesidad'),
    ('deportiva', 'Beca Deportiva'),
    ('convenio',  'Beca por Convenio'),
]
ESTADO_BECA = [
    ('solicitada','Solicitada'),
    ('aprobada',  'Aprobada'),
    ('rechazada', 'Rechazada'),
    ('vigente',   'Vigente'),
    ('finalizada','Finalizada'),
]

class Beca(models.Model):
    alumno       = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='becas')
    tipo         = models.CharField(max_length=30, choices=TIPO_BECA)
    porcentaje   = models.IntegerField()
    estado       = models.CharField(max_length=20, choices=ESTADO_BECA, default='solicitada')
    fecha_inicio = models.DateField()
    fecha_fin    = models.DateField(null=True, blank=True)
    observacion  = models.TextField(blank=True)
    nodo_tramite = models.ForeignKey(NodoTramite, null=True, blank=True, on_delete=models.SET_NULL, related_name='becas_asociadas')

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.alumno.dni} - {self.get_tipo_display()} [{self.estado}]"

    def save(self, *args, **kwargs):
        if not self.nodo_tramite:
            self.nodo_tramite = NodoTramite.objects.filter(nombre__iexact="Becas").first()
        super().save(*args, **kwargs)


# ============================================================
# DOCUMENTOS
# ============================================================

TIPO_DOCUMENTO = [
    ('certificado_notas',    'Certificado de Notas'),
    ('certificado_estudios', 'Certificado de Estudios'),
    ('constancia',           'Constancia de Estudios'),
    ('titulo',               'Título Profesional'),
]
ESTADO_DOCUMENTO = [
    ('solicitado','Solicitado'),
    ('en_proceso','En Proceso'),
    ('listo',     'Listo para recoger'),
    ('entregado', 'Entregado'),
]

class Documento(models.Model):
    alumno          = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='documentos')
    tipo            = models.CharField(max_length=40, choices=TIPO_DOCUMENTO)
    estado          = models.CharField(max_length=20, choices=ESTADO_DOCUMENTO, default='solicitado')
    fecha_solicitud = models.DateField(auto_now_add=True)
    fecha_entrega   = models.DateField(null=True, blank=True)
    observacion     = models.TextField(blank=True)
    nodo_tramite    = models.ForeignKey(NodoTramite, null=True, blank=True, on_delete=models.SET_NULL, related_name='documentos_asociados')

    class Meta:
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.alumno.dni} - {self.get_tipo_display()} [{self.estado}]"

    def save(self, *args, **kwargs):
        if not self.nodo_tramite:
            if self.tipo in ['certificado_notas', 'certificado_estudios']:
                self.nodo_tramite = NodoTramite.objects.filter(nombre__iexact="Certificados").first()
            elif self.tipo == 'constancia':
                self.nodo_tramite = NodoTramite.objects.filter(nombre__iexact="Constancias").first()
            elif self.tipo == 'titulo':
                self.nodo_tramite = NodoTramite.objects.filter(nombre__iexact="Títulos").first()
        super().save(*args, **kwargs)


# ============================================================
# COMUNICADOS
# ============================================================

TIPO_COMUNICADO = [
    ('general',    'General'),
    ('academico',  'Académico'),
    ('financiero', 'Financiero'),
    ('urgente',    'Urgente'),
]
DEST_COMUNICADO = [
    ('todos',     'Todos'),
    ('alumnos',   'Solo Alumnos'),
    ('docentes',  'Solo Docentes'),
    ('carrera',   'Por Carrera'),
]

class Comunicado(models.Model):
    titulo      = models.CharField(max_length=300)
    cuerpo      = models.TextField()
    tipo        = models.CharField(max_length=20, choices=TIPO_COMUNICADO, default='general')
    destinatario= models.CharField(max_length=20, choices=DEST_COMUNICADO, default='todos')
    carrera     = models.ForeignKey(Carrera, null=True, blank=True, on_delete=models.SET_NULL, related_name='comunicados')
    fecha       = models.DateTimeField(auto_now_add=True)
    activo      = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo}"


# ============================================================
# NOTIFICACIONES (bandeja de alertas)
# ============================================================

TIPO_NOTIF = [
    ('pago_vencido',  'Pago Vencido'),
    ('pago_proximo',  'Pago Próximo'),
    ('nota_cargada',  'Nota Cargada'),
    ('comunicado',    'Comunicado'),
    ('matricula',     'Matrícula'),
    ('sistema',       'Sistema'),
]

class Notificacion(models.Model):
    alumno    = models.ForeignKey(Alumno, null=True, blank=True, on_delete=models.CASCADE, related_name='notificaciones')
    docente   = models.ForeignKey(Docente, null=True, blank=True, on_delete=models.CASCADE, related_name='notificaciones')
    tipo      = models.CharField(max_length=20, choices=TIPO_NOTIF)
    titulo    = models.CharField(max_length=200)
    mensaje   = models.TextField()
    leida     = models.BooleanField(default=False)
    fecha     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        dest = self.alumno or self.docente
        return f"[{self.get_tipo_display()}] → {dest} | {self.titulo}"
