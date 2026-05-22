from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from decimal import Decimal
import json
from .models import (NodoTramite, Alumno, Carrera, Pension, Beca, Documento,
                     Pago, Notificacion, Comunicado, Docente, Curso, CursoCarrera,
                     Matricula, Nota)
from .tree_logic.generic_tree import NodoArbol, ArbolGenerico
from .forms import (NodoTramiteForm, AlumnoForm, CarreraForm, PensionForm,
                    BecaForm, DocumentoForm, PagoForm, DocenteForm,
                    CursoCarreraForm, AsignarDocenteForm)

# ============================================================
# ROL: BACKEND — Vistas y Endpoints
# ============================================================

def construir_arbol(nodo_db):
    nodo = NodoArbol(nodo_db.id, nodo_db.nombre, nodo_db.descripcion,
                     nodo_db.enlace, nodo_db.tipo, nodo_db.orden)
    for hijo in nodo_db.hijos.all():
        nodo.hijos.append(construir_arbol(hijo))
    return nodo

def get_arbol():
    raiz_db = NodoTramite.objects.filter(padre=None).first()
    if not raiz_db:
        return None
    return ArbolGenerico(construir_arbol(raiz_db))


# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------

def index(request):
    arbol = get_arbol()
    contexto = {}
    contexto['arbol_json'] = json.dumps(arbol.a_dict(), ensure_ascii=False) if arbol else 'null'
    if arbol:
        contexto['altura']      = arbol.altura()
        contexto['total_nodos'] = arbol.contar_nodos()
        contexto['total_hojas'] = arbol.contar_hojas()
    contexto['total_alumnos']    = Alumno.objects.filter(activo=True).count()
    contexto['total_pendientes'] = Pension.objects.filter(estado='pendiente').count()
    contexto['total_becas']      = Beca.objects.filter(estado='vigente').count()
    contexto['total_docs']       = Documento.objects.filter(estado='en_proceso').count()
    contexto['carreras']         = Carrera.objects.all()
    return render(request, 'tramites/index.html', contexto)


# ------------------------------------------------------------
# ALUMNOS
# ------------------------------------------------------------

def alumnos_lista(request):
    q          = request.GET.get('q', '').strip()
    carrera_id = request.GET.get('carrera', '').strip()
    anio       = request.GET.get('anio', '').strip()
    ciclo      = request.GET.get('ciclo', '').strip()
    carreras   = Carrera.objects.all()
    alumnos    = Alumno.objects.select_related('carrera').filter(activo=True)
    if q:
        alumnos = alumnos.filter(Q(dni__icontains=q)|Q(nombre__icontains=q)|Q(apellido__icontains=q))
    if carrera_id:
        alumnos = alumnos.filter(carrera_id=carrera_id)
    if anio in ['1','2','3']:
        alumnos = alumnos.filter(anio=anio)
    if ciclo in ['1','2','3','4','5','6']:
        alumnos = alumnos.filter(ciclo=ciclo)
    paginator    = Paginator(alumnos, 25)
    alumnos_page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'tramites/alumnos_lista.html', {
        'alumnos': alumnos_page, 'q': q, 'carreras': carreras,
        'carrera_id': carrera_id, 'anio': anio, 'ciclo': ciclo,
    })

def alumno_detalle(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    return render(request, 'tramites/alumno_detalle.html', {
        'alumno': alumno, 'pensiones': alumno.pensiones.all(),
        'becas': alumno.becas.all(), 'documentos': alumno.documentos.all(),
        'pagos': alumno.pagos.all(),
    })

def alumno_nuevo(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save()
            messages.success(request, f'Alumno {alumno.nombre_completo} registrado.')
            return redirect('alumno_detalle', dni=alumno.dni)
    else:
        form = AlumnoForm()
    return render(request, 'tramites/alumno_form.html', {'form': form, 'accion': 'Nuevo'})

def alumno_editar(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos actualizados.')
            return redirect('alumno_detalle', dni=alumno.dni)
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'tramites/alumno_form.html', {'form': form, 'alumno': alumno, 'accion': 'Editar'})

def alumno_eliminar(request, dni):
    obj = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, f'Alumno {obj.nombre_completo} eliminado.')
        except Exception as e:
            messages.error(request, f'No se pudo eliminar: {e}')
        return redirect('alumnos_lista')
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})


# ------------------------------------------------------------
# PENSIONES
# ------------------------------------------------------------

def pension_nueva(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        form = PensionForm(request.POST)
        if form.is_valid():
            form.instance.alumno = alumno
            form.save()
            messages.success(request, 'Pensión registrada.')
            return redirect('alumno_detalle', dni=dni)
    else:
        form = PensionForm()
    return render(request, 'tramites/pension_form.html', {'form': form, 'alumno': alumno})

def pension_editar(request, pk):
    pension = get_object_or_404(Pension, pk=pk)
    if request.method == 'POST':
        form = PensionForm(request.POST, instance=pension)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pensión actualizada.')
            return redirect('alumno_detalle', dni=pension.alumno.dni)
    else:
        form = PensionForm(instance=pension)
    return render(request, 'tramites/pension_form.html', {'form': form, 'pension': pension, 'alumno': pension.alumno})

def pension_eliminar(request, pk):
    obj = get_object_or_404(Pension, pk=pk)
    dni = obj.alumno.dni
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Pensión eliminada.')
        return redirect('alumno_detalle', dni=dni)
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})


# ------------------------------------------------------------
# BECAS
# ------------------------------------------------------------

def beca_nueva(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        form = BecaForm(request.POST)
        if form.is_valid():
            form.instance.alumno = alumno
            form.save()
            messages.success(request, 'Beca registrada.')
            return redirect('alumno_detalle', dni=dni)
    else:
        form = BecaForm()
    return render(request, 'tramites/beca_form.html', {'form': form, 'alumno': alumno})

def beca_editar(request, pk):
    beca = get_object_or_404(Beca, pk=pk)
    if request.method == 'POST':
        form = BecaForm(request.POST, instance=beca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Beca actualizada.')
            return redirect('alumno_detalle', dni=beca.alumno.dni)
    else:
        form = BecaForm(instance=beca)
    return render(request, 'tramites/beca_form.html', {'form': form, 'beca': beca, 'alumno': beca.alumno})

def beca_eliminar(request, pk):
    obj = get_object_or_404(Beca, pk=pk)
    dni = obj.alumno.dni
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Beca eliminada.')
        return redirect('alumno_detalle', dni=dni)
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})


# ------------------------------------------------------------
# DOCUMENTOS
# ------------------------------------------------------------

def documento_nuevo(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        form = DocumentoForm(request.POST)
        if form.is_valid():
            form.instance.alumno = alumno
            form.save()
            messages.success(request, 'Documento registrado.')
            return redirect('alumno_detalle', dni=dni)
    else:
        form = DocumentoForm()
    return render(request, 'tramites/documento_form.html', {'form': form, 'alumno': alumno})

def documento_editar(request, pk):
    doc = get_object_or_404(Documento, pk=pk)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento actualizado.')
            return redirect('alumno_detalle', dni=doc.alumno.dni)
    else:
        form = DocumentoForm(instance=doc)
    return render(request, 'tramites/documento_form.html', {'form': form, 'doc': doc, 'alumno': doc.alumno})

def documento_eliminar(request, pk):
    obj = get_object_or_404(Documento, pk=pk)
    dni = obj.alumno.dni
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Documento eliminado.')
        return redirect('alumno_detalle', dni=dni)
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})


# ------------------------------------------------------------
# CARRERAS
# ------------------------------------------------------------

def carreras_lista(request):
    q        = request.GET.get('q', '').strip()
    duracion = request.GET.get('duracion', '')
    carreras = Carrera.objects.all()
    if q:
        carreras = carreras.filter(Q(codigo__icontains=q)|Q(nombre__icontains=q))
    if duracion in ['2','3']:
        carreras = carreras.filter(duracion=duracion)
    carreras = carreras.annotate(
        total_alumnos=Count('alumnos', filter=Q(alumnos__activo=True), distinct=True),
        total_pendientes=Count('alumnos__pensiones', filter=Q(alumnos__pensiones__estado='pendiente'), distinct=True),
        total_becas=Count('alumnos__becas', filter=Q(alumnos__becas__estado='vigente'), distinct=True),
        total_docs=Count('alumnos__documentos', filter=Q(alumnos__documentos__estado='en_proceso'), distinct=True),
    )
    paginator     = Paginator(carreras, 25)
    carreras_page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'tramites/carreras_lista.html', {'carreras': carreras_page, 'q': q, 'duracion': duracion})

def carrera_detalle(request, codigo):
    carrera = get_object_or_404(Carrera, codigo__iexact=codigo)
    q       = request.GET.get('q', '').strip()
    anio    = request.GET.get('anio', '')
    ciclo   = request.GET.get('ciclo', '')
    alumnos = carrera.alumnos.filter(activo=True).select_related('carrera')
    if q:
        alumnos = alumnos.filter(Q(dni__icontains=q)|Q(nombre__icontains=q)|Q(apellido__icontains=q))
    if anio in ['1','2','3']:
        alumnos = alumnos.filter(anio=anio)
    if ciclo in ['1','2','3','4','5','6']:
        alumnos = alumnos.filter(ciclo=ciclo)
    paginator    = Paginator(alumnos, 25)
    alumnos_page = paginator.get_page(request.GET.get('page', 1))
    # Malla curricular agrupada por ciclo
    malla = {}
    for cc in carrera.malla.select_related('curso', 'docente').order_by('ciclo','curso__nombre'):
        malla.setdefault(cc.ciclo, []).append(cc)
    return render(request, 'tramites/carrera_detalle.html', {
        'carrera': carrera, 'alumnos': alumnos_page,
        'q': q, 'anio': anio, 'ciclo': ciclo,
        'malla': malla,
        'total_alumnos':    alumnos.count(),
        'total_pendientes': Pension.objects.filter(alumno__carrera=carrera, estado='pendiente').count(),
        'total_becas':      Beca.objects.filter(alumno__carrera=carrera, estado='vigente').count(),
        'total_docs':       Documento.objects.filter(alumno__carrera=carrera, estado='en_proceso').count(),
    })

def carrera_nueva(request):
    if request.method == 'POST':
        form = CarreraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carrera registrada.')
            return redirect('carreras_lista')
    else:
        form = CarreraForm()
    return render(request, 'tramites/carrera_form.html', {'form': form, 'accion': 'Nueva'})

def carrera_eliminar(request, codigo):
    obj = get_object_or_404(Carrera, codigo__iexact=codigo)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Carrera eliminada.')
        except Exception as e:
            messages.error(request, f'No se pudo eliminar: {e}')
        return redirect('carreras_lista')
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})


# ============================================================
# DOCENTES
# ============================================================

def docentes_lista(request):
    q            = request.GET.get('q', '').strip()
    especialidad = request.GET.get('especialidad', '')
    docentes     = Docente.objects.filter(activo=True).annotate(
        total_cursos=Count('cursos_asignados', distinct=True)
    )
    if q:
        docentes = docentes.filter(Q(dni__icontains=q)|Q(nombre__icontains=q)|Q(apellido__icontains=q))
    if especialidad:
        docentes = docentes.filter(especialidad=especialidad)
    paginator     = Paginator(docentes, 25)
    docentes_page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'tramites/docentes_lista.html', {
        'docentes':     docentes_page,
        'q':            q,
        'especialidad': especialidad,
        'especialidades': Docente._meta.get_field('especialidad').choices,
    })

def docente_detalle(request, dni):
    docente  = get_object_or_404(Docente, dni=dni)
    cursos   = docente.cursos_asignados.select_related('carrera', 'curso').order_by('carrera__nombre', 'ciclo')
    carreras = {cc.carrera for cc in cursos}
    return render(request, 'tramites/docente_detalle.html', {
        'docente':  docente,
        'cursos':   cursos,
        'carreras': carreras,
    })

def docente_nuevo(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            docente = form.save()
            messages.success(request, f'Docente {docente.nombre_completo} registrado.')
            return redirect('docente_detalle', dni=docente.dni)
    else:
        form = DocenteForm()
    return render(request, 'tramites/docente_form.html', {'form': form, 'accion': 'Nuevo'})

def docente_editar(request, dni):
    docente = get_object_or_404(Docente, dni=dni)
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos actualizados.')
            return redirect('docente_detalle', dni=docente.dni)
    else:
        form = DocenteForm(instance=docente)
    return render(request, 'tramites/docente_form.html', {'form': form, 'docente': docente, 'accion': 'Editar'})

def docente_eliminar(request, dni):
    obj = get_object_or_404(Docente, dni=dni)
    if request.method == 'POST':
        try:
            obj.activo = False
            obj.save()
            messages.success(request, f'Docente {obj.nombre_completo} desactivado.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('docentes_lista')
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj, 'accion': 'Desactivar'})


# ------------------------------------------------------------
# ASIGNACIÓN DE DOCENTES A CURSOS
# ------------------------------------------------------------

def asignar_docente(request, cursocarrera_id):
    cc = get_object_or_404(CursoCarrera, pk=cursocarrera_id)
    if request.method == 'POST':
        form = AsignarDocenteForm(request.POST, instance=cc)
        if form.is_valid():
            form.save()
            messages.success(request, f'Docente asignado a {cc.curso.nombre}.')
            return redirect('carrera_detalle', codigo=cc.carrera.codigo)
    else:
        form = AsignarDocenteForm(instance=cc)
    return render(request, 'tramites/asignar_docente_form.html', {
        'form':    form,
        'cc':      cc,
        'carrera': cc.carrera,
    })

def malla_agregar_curso(request, codigo):
    carrera = get_object_or_404(Carrera, codigo__iexact=codigo)
    if request.method == 'POST':
        form = CursoCarreraForm(request.POST)
        if form.is_valid():
            cc         = form.save(commit=False)
            cc.carrera = carrera
            try:
                cc.save()
                messages.success(request, f'{cc.curso.nombre} agregado a Ciclo {cc.ciclo}.')
            except Exception as e:
                messages.error(request, f'Error: {e}')
            return redirect('carrera_detalle', codigo=codigo)
    else:
        form = CursoCarreraForm()
    return render(request, 'tramites/malla_curso_form.html', {'form': form, 'carrera': carrera})

def malla_quitar_curso(request, cursocarrera_id):
    cc     = get_object_or_404(CursoCarrera, pk=cursocarrera_id)
    codigo = cc.carrera.codigo
    if request.method == 'POST':
        cc.delete()
        messages.success(request, 'Curso eliminado de la malla.')
        return redirect('carrera_detalle', codigo=codigo)
    return render(request, 'tramites/confirmar_eliminar.html', {
        'obj':    cc,
        'accion': 'Quitar de la malla',
    })


# ============================================================
# NODOS DEL ÁRBOL (CRUD)
# ============================================================

def nodo_nuevo(request, padre_id=None):
    padre = get_object_or_404(NodoTramite, pk=padre_id) if padre_id else None
    if request.method == 'POST':
        form = NodoTramiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nodo creado.')
            return redirect('index')
    else:
        form = NodoTramiteForm(initial={'padre': padre})
    return render(request, 'tramites/nodo_form.html', {'form': form, 'accion': 'Nuevo'})

def nodo_editar(request, pk):
    nodo = get_object_or_404(NodoTramite, pk=pk)
    if request.method == 'POST':
        form = NodoTramiteForm(request.POST, instance=nodo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nodo actualizado.')
            return redirect('index')
    else:
        form = NodoTramiteForm(instance=nodo)
    return render(request, 'tramites/nodo_form.html', {'form': form, 'nodo': nodo, 'accion': 'Editar'})

def nodo_eliminar(request, pk):
    nodo = get_object_or_404(NodoTramite, pk=pk)
    if nodo.padre is None:
        messages.error(request, 'No se puede eliminar la raíz del árbol.')
        return redirect('index')
    if request.method == 'POST':
        modo = request.POST.get('modo', 'subarbol')
        try:
            if modo == 'reasignar':
                NodoTramite.objects.filter(padre=nodo).update(padre=nodo.padre)
            nodo.delete()
            messages.success(request, 'Nodo eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'No se pudo eliminar: {e}')
        return redirect('index')
    return render(request, 'tramites/nodo_eliminar.html', {
        'nodo': nodo, 'num_hijos': nodo.hijos.count(),
        'num_desc': len(nodo.get_descendientes_ids()),
    })


# ============================================================
# FINANZAS
# ============================================================

def finanzas_dashboard(request):
    total_cobrado   = Pago.objects.filter(estado='completado').aggregate(t=Sum('monto'))['t'] or Decimal('0')
    total_pendiente = Pension.objects.filter(estado='pendiente').aggregate(t=Sum('monto'))['t'] or Decimal('0')
    total_vencido   = Pension.objects.filter(estado='vencido').aggregate(t=Sum('monto'))['t'] or Decimal('0')
    total_pagos     = Pago.objects.filter(estado='completado').count()
    ultimos_pagos   = Pago.objects.select_related('alumno').filter(estado='completado').order_by('-fecha')[:10]
    vencidas        = Pension.objects.select_related('alumno','alumno__carrera').filter(
        estado__in=['pendiente','vencido']).order_by('anio','mes')[:20]
    por_metodo      = Pago.objects.filter(estado='completado').values('metodo').annotate(
        total=Sum('monto'), cantidad=Count('id')).order_by('-total')
    return render(request, 'tramites/finanzas_dashboard.html', {
        'total_cobrado': total_cobrado, 'total_pendiente': total_pendiente,
        'total_vencido': total_vencido, 'total_pagos': total_pagos,
        'ultimos_pagos': ultimos_pagos, 'vencidas': vencidas, 'por_metodo': por_metodo,
    })

def finanzas_alumno(request, dni):
    alumno          = get_object_or_404(Alumno, dni=dni)
    pensiones       = alumno.pensiones.all()
    pagos           = alumno.pagos.select_related().all()
    becas           = alumno.becas.filter(estado__in=['aprobada','vigente'])
    total_pensiones = pensiones.aggregate(t=Sum('monto'))['t'] or Decimal('0')
    total_pagado    = pagos.filter(estado='completado').aggregate(t=Sum('monto'))['t'] or Decimal('0')
    total_pendiente = pensiones.filter(estado='pendiente').aggregate(t=Sum('monto'))['t'] or Decimal('0')
    total_vencido   = pensiones.filter(estado='vencido').aggregate(t=Sum('monto'))['t'] or Decimal('0')
    saldo           = total_pensiones - total_pagado
    return render(request, 'tramites/finanzas_alumno.html', {
        'alumno': alumno, 'pensiones': pensiones, 'pagos': pagos, 'becas': becas,
        'total_pensiones': total_pensiones, 'total_pagado': total_pagado,
        'total_pendiente': total_pendiente, 'total_vencido': total_vencido, 'saldo': saldo,
    })

def pago_nuevo(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago        = form.save(commit=False)
            pago.alumno = alumno
            pago.save()
            if pago.tipo == 'pension' and pago.estado == 'completado':
                pension_id = request.POST.get('pension_id')
                if pension_id:
                    try:
                        p           = Pension.objects.get(pk=pension_id, alumno=alumno)
                        p.estado    = 'pagado'
                        p.fecha_pago = pago.fecha
                        p.save()
                        pago.pension = p
                        pago.save()
                    except Pension.DoesNotExist:
                        pass
            messages.success(request, f'Pago de S/{pago.monto} registrado.')
            return redirect('finanzas_alumno', dni=dni)
    else:
        form = PagoForm()
    return render(request, 'tramites/pago_form.html', {
        'form': form, 'alumno': alumno,
        'pensiones_pendientes': alumno.pensiones.filter(estado__in=['pendiente','vencido']),
    })

def pago_editar(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    if request.method == 'POST':
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pago actualizado.')
            return redirect('finanzas_alumno', dni=pago.alumno.dni)
    else:
        form = PagoForm(instance=pago)
    return render(request, 'tramites/pago_form.html', {'form': form, 'pago': pago, 'alumno': pago.alumno})

def pago_anular(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    dni  = pago.alumno.dni
    if request.method == 'POST':
        pago.estado = 'anulado'
        pago.save()
        if pago.pension:
            pago.pension.estado     = 'pendiente'
            pago.pension.fecha_pago = None
            pago.pension.save()
        messages.success(request, 'Pago anulado.')
        return redirect('finanzas_alumno', dni=dni)
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': pago, 'accion': 'Anular'})

def pensiones_vencidas(request):
    q          = request.GET.get('q', '').strip()
    carrera_id = request.GET.get('carrera', '')
    estado     = request.GET.get('estado', '')
    pensiones  = Pension.objects.select_related('alumno','alumno__carrera').filter(estado__in=['pendiente','vencido'])
    if q:
        pensiones = pensiones.filter(Q(alumno__dni__icontains=q)|Q(alumno__nombre__icontains=q)|Q(alumno__apellido__icontains=q))
    if carrera_id:
        pensiones = pensiones.filter(alumno__carrera_id=carrera_id)
    if estado in ['pendiente','vencido']:
        pensiones = pensiones.filter(estado=estado)
    pensiones   = pensiones.order_by('anio','mes')
    total_monto = pensiones.aggregate(t=Sum('monto'))['t'] or Decimal('0')
    paginator   = Paginator(pensiones, 30)
    pens_page   = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'tramites/pensiones_vencidas.html', {
        'pensiones': pens_page, 'total_monto': total_monto,
        'carreras': Carrera.objects.all(),
        'q': q, 'carrera_id': carrera_id, 'estado': estado,
    })


# ------------------------------------------------------------
# NOTIFICACIONES
# ------------------------------------------------------------

def notificaciones(request):
    notifs      = Notificacion.objects.filter(alumno__isnull=False).select_related('alumno').order_by('-fecha')
    no_leidas   = notifs.filter(leida=False).count()
    paginator   = Paginator(notifs, 20)
    notifs_page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'tramites/notificaciones.html', {'notificaciones': notifs_page, 'no_leidas': no_leidas})

def notificacion_marcar_leida(request, pk):
    notif       = get_object_or_404(Notificacion, pk=pk)
    notif.leida = True
    notif.save()
    return redirect('notificaciones')

def notificaciones_marcar_todas(request):
    Notificacion.objects.filter(leida=False).update(leida=True)
    messages.success(request, 'Todas las notificaciones marcadas como leídas.')
    return redirect('notificaciones')


# ------------------------------------------------------------
# COMUNICADOS
# ------------------------------------------------------------

def comunicados_lista(request):
    comunicados = Comunicado.objects.filter(activo=True).select_related('carrera')
    return render(request, 'tramites/comunicados_lista.html', {'comunicados': comunicados})

def comunicado_nuevo(request):
    carreras = Carrera.objects.all()
    if request.method == 'POST':
        try:
            Comunicado.objects.create(
                titulo=request.POST['titulo'], cuerpo=request.POST['cuerpo'],
                tipo=request.POST['tipo'], destinatario=request.POST['destinatario'],
                carrera_id=request.POST.get('carrera') or None,
            )
            messages.success(request, 'Comunicado publicado.')
            return redirect('comunicados_lista')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/comunicado_form.html', {'carreras': carreras})


# ------------------------------------------------------------
# API — ÁRBOL
# ------------------------------------------------------------

def api_arbol(request):
    arbol = get_arbol()
    if not arbol:
        return JsonResponse({'error': 'Árbol vacío'}, status=404)
    return JsonResponse(arbol.a_dict())

def api_nodo(request, nodo_id):
    arbol = get_arbol()
    if not arbol:
        return JsonResponse({'error': 'Árbol vacío'}, status=404)
    info = arbol.info_nodo(nodo_id)
    if not info:
        return JsonResponse({'error': 'Nodo no encontrado'}, status=404)
    return JsonResponse(info)

def api_altura(request, nodo_id):
    try:
        nodo_db = NodoTramite.objects.get(id=nodo_id)
        arbol   = ArbolGenerico(construir_arbol(nodo_db))
        return JsonResponse({'nodo': nodo_db.nombre, 'altura': arbol.altura()})
    except NodoTramite.DoesNotExist:
        return JsonResponse({'error': 'Nodo no encontrado'}, status=404)

def api_buscar(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'error': 'Parámetro q requerido'}, status=400)
    arbol = get_arbol()
    if not arbol:
        return JsonResponse({'error': 'Árbol vacío'}, status=404)
    nodo, ruta = arbol.buscar_con_ruta(q)
    if nodo:
        return JsonResponse({'encontrado': True, 'id': nodo.id, 'nombre': nodo.nombre, 'tipo': nodo.tipo, 'ruta': ruta})
    return JsonResponse({'encontrado': False})

def api_recorrido(request):
    tipo  = request.GET.get('tipo', 'dfs')
    arbol = get_arbol()
    if not arbol:
        return JsonResponse({'error': 'Árbol vacío'}, status=404)
    if tipo == 'bfs':
        return JsonResponse({'tipo': 'BFS', 'recorrido': arbol.recorrido_bfs()})
    return JsonResponse({'tipo': 'DFS', 'recorrido': arbol.recorrido_dfs()})

def api_estadisticas(request):
    arbol = get_arbol()
    if not arbol:
        return JsonResponse({'error': 'Árbol vacío'}, status=404)
    return JsonResponse({'altura': arbol.altura(), 'total_nodos': arbol.contar_nodos(), 'total_hojas': arbol.contar_hojas()})

def api_mover_nodo(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        data           = json.loads(request.body)
        nodo_id        = int(data['nodo_id'])
        nuevo_padre_id = int(data['nuevo_padre_id'])
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    valido, mensaje = NodoTramite.validar_movimiento(nodo_id, nuevo_padre_id)
    if not valido:
        return JsonResponse({'error': mensaje}, status=400)
    nodo        = get_object_or_404(NodoTramite, pk=nodo_id)
    nuevo_padre = get_object_or_404(NodoTramite, pk=nuevo_padre_id)
    nodo.padre  = nuevo_padre
    nodo.save()
    return JsonResponse({'ok': True, 'mensaje': f'"{nodo.nombre}" movido a "{nuevo_padre.nombre}".'})

def api_ordenar_hijos(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        data      = json.loads(request.body)
        nodo_id   = int(data['nodo_id'])
        direccion = data['direccion']
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    nodo = get_object_or_404(NodoTramite, pk=nodo_id)
    if nodo.padre is None:
        return JsonResponse({'error': 'La raíz no tiene hermanos.'}, status=400)
    hermanos = list(NodoTramite.objects.filter(padre=nodo.padre).order_by('orden','nombre'))
    idx = next((i for i, h in enumerate(hermanos) if h.id == nodo_id), None)
    if idx is None:
        return JsonResponse({'error': 'Nodo no encontrado entre hermanos.'}, status=400)
    if direccion == 'arriba' and idx > 0:
        otro = hermanos[idx - 1]
    elif direccion == 'abajo' and idx < len(hermanos) - 1:
        otro = hermanos[idx + 1]
    else:
        return JsonResponse({'error': 'No se puede mover en esa dirección.'}, status=400)
    nodo.orden, otro.orden = otro.orden, nodo.orden
    nodo.save(); otro.save()
    return JsonResponse({'ok': True})
