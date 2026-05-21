from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import NodoTramite, Alumno, Carrera, Pension, Beca, Documento
from .tree_logic.generic_tree import NodoArbol, ArbolGenerico
from .forms import NodoTramiteForm, AlumnoForm, CarreraForm, PensionForm, BecaForm, DocumentoForm

# ============================================================
# ROL: BACKEND — Vistas y Endpoints
# ============================================================

def construir_arbol(nodo_db):
    nodo = NodoArbol(nodo_db.id, nodo_db.nombre, nodo_db.descripcion, nodo_db.enlace)
    for hijo in nodo_db.hijos.all():
        nodo.hijos.append(construir_arbol(hijo))
    return nodo

def get_arbol():
    raiz_db = NodoTramite.objects.filter(padre=None).first()
    if not raiz_db:
        return None
    return ArbolGenerico(construir_arbol(raiz_db))


# ------------------------------------------------------------
# DASHBOARD PRINCIPAL
# ------------------------------------------------------------

def index(request):
    arbol = get_arbol()
    contexto = {}
    if arbol:
        contexto['arbol_json']  = arbol.a_dict()
        contexto['altura']      = arbol.altura()
        contexto['total_nodos'] = arbol.contar_nodos()
        contexto['total_hojas'] = arbol.contar_hojas()
    contexto['total_alumnos']   = Alumno.objects.filter(activo=True).count()
    contexto['total_pendientes']= Pension.objects.filter(estado='pendiente').count()
    contexto['total_becas']     = Beca.objects.filter(estado='vigente').count()
    contexto['total_docs']      = Documento.objects.filter(estado='en_proceso').count()
    return render(request, 'tramites/index.html', contexto)


# ------------------------------------------------------------
# ALUMNOS
# ------------------------------------------------------------

def alumnos_lista(request):
    q = request.GET.get('q', '').strip()
    carrera_cod = request.GET.get('carrera', '').strip()
    anio = request.GET.get('anio', '').strip()
    ciclo = request.GET.get('ciclo', '').strip()
    carreras = Carrera.objects.all()
    alumnos = Alumno.objects.select_related('carrera').filter(activo=True)
    if q:
        alumnos = alumnos.filter(
            Q(dni__icontains=q) | Q(nombre__icontains=q) | Q(apellido__icontains=q)
        )
    if carrera_cod:
        alumnos = alumnos.filter(carrera__codigo__icontains=carrera_cod)
    if anio in ['1', '2', '3']:
        alumnos = alumnos.filter(anio=anio)
    if ciclo in ['1', '2', '3', '4', '5', '6']:
        alumnos = alumnos.filter(ciclo=ciclo)
    paginator = Paginator(alumnos, 25)
    page = request.GET.get('page', 1)
    alumnos_page = paginator.get_page(page)
    return render(request, 'tramites/alumnos_lista.html', {
        'alumnos': alumnos_page,
        'q': q,
        'carreras': carreras,
        'carrera_cod': carrera_cod,
        'anio': anio,
        'ciclo': ciclo,
    })

def alumno_detalle(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    pensiones  = alumno.pensiones.all()
    becas      = alumno.becas.all()
    documentos = alumno.documentos.all()
    return render(request, 'tramites/alumno_detalle.html', {
        'alumno': alumno,
        'pensiones': pensiones,
        'becas': becas,
        'documentos': documentos,
    })

def alumno_nuevo(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save()
            messages.success(request, f'Alumno {alumno.nombre_completo} registrado correctamente.')
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
            messages.success(request, 'Datos actualizados correctamente.')
            return redirect('alumno_detalle', dni=alumno.dni)
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'tramites/alumno_form.html', {'form': form, 'alumno': alumno, 'accion': 'Editar'})


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


# ------------------------------------------------------------
# CARRERAS
# ------------------------------------------------------------

def carreras_lista(request):
    q = request.GET.get('q', '').strip()
    duracion = request.GET.get('duracion', '')
    carreras = Carrera.objects.all()
    if q:
        carreras = carreras.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q))
    if duracion in ['2', '3']:
        carreras = carreras.filter(duracion=duracion)
    carreras = carreras.annotate(
        total_alumnos=Count('alumnos', filter=Q(alumnos__activo=True), distinct=True),
        total_pendientes=Count('alumnos__pensiones', filter=Q(alumnos__pensiones__estado='pendiente'), distinct=True),
        total_becas=Count('alumnos__becas', filter=Q(alumnos__becas__estado='vigente'), distinct=True),
        total_docs=Count('alumnos__documentos', filter=Q(alumnos__documentos__estado='en_proceso'), distinct=True),
    )
    paginator = Paginator(carreras, 25)
    page = request.GET.get('page', 1)
    carreras_page = paginator.get_page(page)
    return render(request, 'tramites/carreras_lista.html', {
        'carreras': carreras_page,
        'q': q,
        'duracion': duracion,
    })


def carrera_detalle(request, codigo):
    carrera = get_object_or_404(Carrera, codigo__iexact=codigo)
    q = request.GET.get('q', '').strip()
    anio = request.GET.get('anio', '')
    ciclo = request.GET.get('ciclo', '')
    alumnos = carrera.alumnos.filter(activo=True).select_related('carrera')
    if q:
        alumnos = alumnos.filter(
            Q(dni__icontains=q) | Q(nombre__icontains=q) | Q(apellido__icontains=q)
        )
    if anio in ['1', '2', '3']:
        alumnos = alumnos.filter(anio=anio)
    if ciclo in ['1', '2', '3', '4', '5', '6']:
        alumnos = alumnos.filter(ciclo=ciclo)

    total_alumnos = alumnos.count()
    total_pendientes = Pension.objects.filter(alumno__carrera=carrera, estado='pendiente').count()
    total_becas = Beca.objects.filter(alumno__carrera=carrera, estado='vigente').count()
    total_docs = Documento.objects.filter(alumno__carrera=carrera, estado='en_proceso').count()

    paginator = Paginator(alumnos, 25)
    page = request.GET.get('page', 1)
    alumnos_page = paginator.get_page(page)

    return render(request, 'tramites/carrera_detalle.html', {
        'carrera': carrera,
        'alumnos': alumnos_page,
        'q': q,
        'anio': anio,
        'ciclo': ciclo,
        'total_alumnos': total_alumnos,
        'total_pendientes': total_pendientes,
        'total_becas': total_becas,
        'total_docs': total_docs,
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


# ------------------------------------------------------------
# NODOS DEL ÁRBOL (CRUD)
# ------------------------------------------------------------

def nodo_nuevo(request, padre_id=None):
    padre = None
    if padre_id:
        padre = get_object_or_404(NodoTramite, pk=padre_id)
    if request.method == 'POST':
        form = NodoTramiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nodo creado correctamente.')
            return redirect('index')
    else:
        initial = {'padre': padre}
        form = NodoTramiteForm(initial=initial)
    return render(request, 'tramites/nodo_form.html', {'form': form, 'accion': 'Nuevo'})

def nodo_editar(request, pk):
    nodo = get_object_or_404(NodoTramite, pk=pk)
    if request.method == 'POST':
        form = NodoTramiteForm(request.POST, instance=nodo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nodo actualizado correctamente.')
            return redirect('index')
    else:
        form = NodoTramiteForm(instance=nodo)
    return render(request, 'tramites/nodo_form.html', {'form': form, 'nodo': nodo, 'accion': 'Editar'})

def nodo_eliminar(request, pk):
    obj = get_object_or_404(NodoTramite, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Nodo eliminado.')
        except Exception as e:
            messages.error(request, f'No se pudo eliminar: {e}')
        return redirect('index')
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})


# ------------------------------------------------------------
# ELIMINAR
# ------------------------------------------------------------

def confirmar_eliminar(request, modelo, pk, redirect_url):
    obj = get_object_or_404(modelo, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'No se pudo eliminar: {e}')
        return redirect(redirect_url)
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})

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

def pension_eliminar(request, pk):
    obj = get_object_or_404(Pension, pk=pk)
    dni = obj.alumno.dni
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Pensión eliminada.')
        return redirect('alumno_detalle', dni=dni)
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})

def beca_eliminar(request, pk):
    obj = get_object_or_404(Beca, pk=pk)
    dni = obj.alumno.dni
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Beca eliminada.')
        return redirect('alumno_detalle', dni=dni)
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})

def documento_eliminar(request, pk):
    obj = get_object_or_404(Documento, pk=pk)
    dni = obj.alumno.dni
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Documento eliminado.')
        return redirect('alumno_detalle', dni=dni)
    return render(request, 'tramites/confirmar_eliminar.html', {'obj': obj})

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


# ------------------------------------------------------------
# API ENDPOINTS (árbol genérico)
# ------------------------------------------------------------

def api_arbol(request):
    arbol = get_arbol()
    if not arbol:
        return JsonResponse({'error': 'Árbol vacío'}, status=404)
    return JsonResponse(arbol.a_dict())

def api_nodo(request, nodo_id):
    try:
        nodo_db = NodoTramite.objects.get(id=nodo_id)
        arbol   = ArbolGenerico(construir_arbol(nodo_db))
        data    = arbol.a_dict()
        data['altura']      = arbol.altura()
        data['total_hijos'] = arbol.contar_nodos() - 1
        return JsonResponse(data)
    except NodoTramite.DoesNotExist:
        return JsonResponse({'error': 'Nodo no encontrado'}, status=404)

def api_altura(request, nodo_id):
    try:
        nodo_db = NodoTramite.objects.get(id=nodo_id)
        arbol   = ArbolGenerico(construir_arbol(nodo_db))
        return JsonResponse({'nodo': nodo_db.nombre, 'altura': arbol.altura()})
    except NodoTramite.DoesNotExist:
        return JsonResponse({'error': 'Nodo no encontrado'}, status=404)

def api_buscar(request):
    q = request.GET.get('q', '')
    if not q:
        return JsonResponse({'error': 'Parámetro q requerido'}, status=400)
    arbol = get_arbol()
    if not arbol:
        return JsonResponse({'error': 'Árbol vacío'}, status=404)
    resultado = arbol.buscar(q)
    if resultado:
        return JsonResponse({'encontrado': True, 'id': resultado.id, 'nombre': resultado.nombre})
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
    return JsonResponse({
        'altura':      arbol.altura(),
        'total_nodos': arbol.contar_nodos(),
        'total_hojas': arbol.contar_hojas(),
    })
