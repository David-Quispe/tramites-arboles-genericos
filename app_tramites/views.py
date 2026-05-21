from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import NodoTramite, Alumno, Carrera, Pension, Beca, Documento
from .tree_logic.generic_tree import NodoArbol, ArbolGenerico

# ============================================================
# ROL: BACKEND — Vistas y Endpoints
# ============================================================

def construir_arbol(nodo_db):
    nodo = NodoArbol(nodo_db.id, nodo_db.nombre, nodo_db.descripcion)
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
    q = request.GET.get('q', '')
    alumnos = Alumno.objects.select_related('carrera').filter(activo=True)
    if q:
        alumnos = alumnos.filter(dni__icontains=q) | alumnos.filter(nombre__icontains=q) | alumnos.filter(apellido__icontains=q)
    return render(request, 'tramites/alumnos_lista.html', {'alumnos': alumnos, 'q': q})

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
    carreras = Carrera.objects.all()
    if request.method == 'POST':
        try:
            alumno = Alumno.objects.create(
                dni           = request.POST['dni'],
                nombre        = request.POST['nombre'],
                apellido      = request.POST['apellido'],
                carrera_id    = request.POST['carrera'],
                anio          = request.POST['anio'],
                ciclo         = request.POST['ciclo'],
                fecha_ingreso = request.POST['fecha_ingreso'],
            )
            messages.success(request, f'Alumno {alumno.nombre_completo} registrado correctamente.')
            return redirect('alumno_detalle', dni=alumno.dni)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/alumno_form.html', {'carreras': carreras, 'accion': 'Nuevo'})

def alumno_editar(request, dni):
    alumno   = get_object_or_404(Alumno, dni=dni)
    carreras = Carrera.objects.all()
    if request.method == 'POST':
        try:
            alumno.nombre        = request.POST['nombre']
            alumno.apellido      = request.POST['apellido']
            alumno.carrera_id    = request.POST['carrera']
            alumno.anio          = request.POST['anio']
            alumno.ciclo         = request.POST['ciclo']
            alumno.fecha_ingreso = request.POST['fecha_ingreso']
            alumno.save()
            messages.success(request, 'Datos actualizados correctamente.')
            return redirect('alumno_detalle', dni=alumno.dni)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/alumno_form.html', {'alumno': alumno, 'carreras': carreras, 'accion': 'Editar'})


# ------------------------------------------------------------
# PENSIONES
# ------------------------------------------------------------

def pension_nueva(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        try:
            Pension.objects.create(
                alumno      = alumno,
                mes         = request.POST['mes'],
                anio        = request.POST['anio'],
                monto       = request.POST['monto'],
                estado      = request.POST['estado'],
                fecha_pago  = request.POST.get('fecha_pago') or None,
                observacion = request.POST.get('observacion', ''),
            )
            messages.success(request, 'Pensión registrada.')
            return redirect('alumno_detalle', dni=dni)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/pension_form.html', {'alumno': alumno})

def pension_editar(request, pk):
    pension = get_object_or_404(Pension, pk=pk)
    if request.method == 'POST':
        try:
            pension.mes         = request.POST['mes']
            pension.anio        = request.POST['anio']
            pension.monto       = request.POST['monto']
            pension.estado      = request.POST['estado']
            pension.fecha_pago  = request.POST.get('fecha_pago') or None
            pension.observacion = request.POST.get('observacion', '')
            pension.save()
            messages.success(request, 'Pensión actualizada.')
            return redirect('alumno_detalle', dni=pension.alumno.dni)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/pension_form.html', {'pension': pension, 'alumno': pension.alumno})


# ------------------------------------------------------------
# BECAS
# ------------------------------------------------------------

def beca_nueva(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        try:
            Beca.objects.create(
                alumno      = alumno,
                tipo        = request.POST['tipo'],
                porcentaje  = request.POST['porcentaje'],
                estado      = request.POST['estado'],
                fecha_inicio= request.POST['fecha_inicio'],
                fecha_fin   = request.POST.get('fecha_fin') or None,
                observacion = request.POST.get('observacion', ''),
            )
            messages.success(request, 'Beca registrada.')
            return redirect('alumno_detalle', dni=dni)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/beca_form.html', {'alumno': alumno})

def beca_editar(request, pk):
    beca = get_object_or_404(Beca, pk=pk)
    if request.method == 'POST':
        try:
            beca.tipo         = request.POST['tipo']
            beca.porcentaje   = request.POST['porcentaje']
            beca.estado       = request.POST['estado']
            beca.fecha_inicio = request.POST['fecha_inicio']
            beca.fecha_fin    = request.POST.get('fecha_fin') or None
            beca.observacion  = request.POST.get('observacion', '')
            beca.save()
            messages.success(request, 'Beca actualizada.')
            return redirect('alumno_detalle', dni=beca.alumno.dni)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/beca_form.html', {'beca': beca, 'alumno': beca.alumno})


# ------------------------------------------------------------
# DOCUMENTOS
# ------------------------------------------------------------

def documento_nuevo(request, dni):
    alumno = get_object_or_404(Alumno, dni=dni)
    if request.method == 'POST':
        try:
            Documento.objects.create(
                alumno      = alumno,
                tipo        = request.POST['tipo'],
                estado      = request.POST['estado'],
                observacion = request.POST.get('observacion', ''),
            )
            messages.success(request, 'Documento registrado.')
            return redirect('alumno_detalle', dni=dni)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/documento_form.html', {'alumno': alumno})

def documento_editar(request, pk):
    doc = get_object_or_404(Documento, pk=pk)
    if request.method == 'POST':
        try:
            doc.tipo          = request.POST['tipo']
            doc.estado        = request.POST['estado']
            doc.fecha_entrega = request.POST.get('fecha_entrega') or None
            doc.observacion   = request.POST.get('observacion', '')
            doc.save()
            messages.success(request, 'Documento actualizado.')
            return redirect('alumno_detalle', dni=doc.alumno.dni)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/documento_form.html', {'doc': doc, 'alumno': doc.alumno})


# ------------------------------------------------------------
# CARRERAS
# ------------------------------------------------------------

def carreras_lista(request):
    carreras = Carrera.objects.all()
    return render(request, 'tramites/carreras_lista.html', {'carreras': carreras})

def carrera_nueva(request):
    if request.method == 'POST':
        try:
            Carrera.objects.create(
                nombre   = request.POST['nombre'],
                codigo   = request.POST['codigo'],
                duracion = request.POST['duracion'],
            )
            messages.success(request, 'Carrera registrada.')
            return redirect('carreras_lista')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'tramites/carrera_form.html', {'accion': 'Nueva'})


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
