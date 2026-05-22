# ============================================================
# ROL: LÓGICA — Árbol Genérico extendido
# ============================================================

class NodoArbol:
    def __init__(self, id, nombre, descripcion="", enlace="", tipo="categoria", orden=0, hijos=None):
        self.id          = id
        self.nombre      = nombre
        self.descripcion = descripcion
        self.enlace      = enlace
        self.tipo        = tipo
        self.orden       = orden
        self.hijos       = hijos or []

    def contar_tramites_activos(self):
        # Recorrido Post-Orden:
        # Sumamos recursivamente la cantidad de trámites de todos sus hijos
        total_hijos = sum(h.contar_tramites_activos() for h in self.hijos)
        
        if self.hijos:
            # Si no es hoja, retorna el total acumulado de sus hijos
            return total_hijos
            
        # Si es hoja, realiza la consulta a la base de datos
        from app_tramites.models import Pension, Beca, Documento, Matricula
        
        pensiones_count = Pension.objects.filter(nodo_tramite_id=self.id, estado='pendiente').count()
        becas_count = Beca.objects.filter(nodo_tramite_id=self.id, estado='vigente').count()
        documentos_count = Documento.objects.filter(nodo_tramite_id=self.id, estado='en_proceso').count()
        matriculas_count = Matricula.objects.filter(nodo_tramite_id=self.id, estado='activa').count()
        
        return pensiones_count + becas_count + documentos_count + matriculas_count


class ArbolGenerico:
    def __init__(self, raiz):
        self.raiz = raiz

    # ── Altura / conteo ──────────────────────────────────────
    def altura(self, nodo=None):
        if nodo is None:
            nodo = self.raiz
        if not nodo.hijos:
            return 0
        return 1 + max(self.altura(h) for h in nodo.hijos)

    def contar_nodos(self, nodo=None):
        if nodo is None:
            nodo = self.raiz
        return 1 + sum(self.contar_nodos(h) for h in nodo.hijos)

    def contar_hojas(self, nodo=None):
        if nodo is None:
            nodo = self.raiz
        if not nodo.hijos:
            return 1
        return sum(self.contar_hojas(h) for h in nodo.hijos)

    # ── Búsqueda ─────────────────────────────────────────────
    def buscar(self, nombre, nodo=None):
        """Búsqueda por nombre exacto (case-insensitive). Retorna NodoArbol o None."""
        if nodo is None:
            nodo = self.raiz
        if nombre.lower() in nodo.nombre.lower():
            return nodo
        for hijo in nodo.hijos:
            resultado = self.buscar(nombre, hijo)
            if resultado:
                return resultado
        return None

    def buscar_con_ruta(self, nombre, nodo=None, ruta=None):
        """
        Busca un nodo y retorna su ruta completa desde la raíz.
        Retorna (NodoArbol, [ruta_de_nodos]) o (None, [])
        """
        if nodo is None:
            nodo = self.raiz
        if ruta is None:
            ruta = []
        ruta_actual = ruta + [{"id": nodo.id, "nombre": nodo.nombre, "tipo": nodo.tipo}]
        if nombre.lower() in nodo.nombre.lower():
            return nodo, ruta_actual
        for hijo in nodo.hijos:
            resultado, ruta_resultado = self.buscar_con_ruta(nombre, hijo, ruta_actual)
            if resultado:
                return resultado, ruta_resultado
        return None, []

    def buscar_por_id(self, nodo_id, nodo=None):
        """Búsqueda por ID. Retorna NodoArbol o None."""
        if nodo is None:
            nodo = self.raiz
        if nodo.id == nodo_id:
            return nodo
        for hijo in nodo.hijos:
            resultado = self.buscar_por_id(nodo_id, hijo)
            if resultado:
                return resultado
        return None

    # ── Info estructural del nodo ─────────────────────────────
    def info_nodo(self, nodo_id):
        """
        Retorna dict con información estructural completa del nodo:
        nombre, tipo, profundidad, num_hijos, padre.
        """
        info = self._info_nodo_rec(nodo_id, self.raiz, None, 0)
        return info

    def _info_nodo_rec(self, nodo_id, nodo_actual, padre, profundidad):
        if nodo_actual.id == nodo_id:
            return {
                "id":          nodo_actual.id,
                "nombre":      nodo_actual.nombre,
                "tipo":        nodo_actual.tipo,
                "descripcion": nodo_actual.descripcion,
                "profundidad": profundidad,
                "num_hijos":   len(nodo_actual.hijos),
                "es_hoja":     len(nodo_actual.hijos) == 0,
                "es_raiz":     padre is None,
                "padre":       {"id": padre.id, "nombre": padre.nombre} if padre else None,
                "orden":       nodo_actual.orden,
            }
        for hijo in nodo_actual.hijos:
            resultado = self._info_nodo_rec(nodo_id, hijo, nodo_actual, profundidad + 1)
            if resultado:
                return resultado
        return None

    # ── Recorridos ────────────────────────────────────────────
    def recorrido_dfs(self, nodo=None, nivel=0):
        if nodo is None:
            nodo = self.raiz
        resultado = [{"id": nodo.id, "nombre": nodo.nombre, "nivel": nivel, "tipo": nodo.tipo}]
        for hijo in nodo.hijos:
            resultado.extend(self.recorrido_dfs(hijo, nivel + 1))
        return resultado

    def recorrido_dfs_con_pasos(self):
        pila = [(self.raiz, 0)]
        pasos = []
        visitados = []
        
        while pila:
            # Estado actual de la pila (serializado)
            estado_pila = [{"id": n.id, "nombre": n.nombre, "nivel": nv, "tipo": n.tipo} for n, nv in pila]
            
            nodo, nivel = pila.pop()
            visitados.append(nodo.id)
            
            # Apilamos en orden inverso para que el recorrido sea de izquierda a derecha
            for hijo in reversed(nodo.hijos):
                pila.append((hijo, nivel + 1))
                
            pasos.append({
                "nodo_actual": {"id": nodo.id, "nombre": nodo.nombre, "nivel": nivel, "tipo": nodo.tipo},
                "pila": estado_pila,
                "visitados": list(visitados)
            })
        return pasos

    def recorrido_bfs(self):
        from collections import deque
        cola = deque([(self.raiz, 0)])
        resultado = []
        while cola:
            nodo, nivel = cola.popleft()
            resultado.append({"id": nodo.id, "nombre": nodo.nombre, "nivel": nivel, "tipo": nodo.tipo})
            for hijo in nodo.hijos:
                cola.append((hijo, nivel + 1))
        return resultado

    def recorrido_bfs_con_pasos(self):
        from collections import deque
        cola = deque([(self.raiz, 0)])
        pasos = []
        visitados = []
        
        while cola:
            estado_cola = [{"id": n.id, "nombre": n.nombre, "nivel": nv, "tipo": n.tipo} for n, nv in cola]
            
            nodo, nivel = cola.popleft()
            visitados.append(nodo.id)
            
            for hijo in nodo.hijos:
                cola.append((hijo, nivel + 1))
                
            pasos.append({
                "nodo_actual": {"id": nodo.id, "nombre": nodo.nombre, "nivel": nivel, "tipo": nodo.tipo},
                "cola": estado_cola,
                "visitados": list(visitados)
            })
        return pasos

    # ── Serialización ─────────────────────────────────────────
    def a_dict(self, nodo=None, nivel=0):
        if nodo is None:
            nodo = self.raiz
        return {
            "id":          nodo.id,
            "nombre":      nodo.nombre,
            "descripcion": nodo.descripcion,
            "enlace":      nodo.enlace,
            "tipo":        nodo.tipo,
            "orden":       nodo.orden,
            "nivel":       nivel,
            "cant_tramites": nodo.contar_tramites_activos(),
            "hijos":       [self.a_dict(h, nivel + 1) for h in nodo.hijos]
        }
