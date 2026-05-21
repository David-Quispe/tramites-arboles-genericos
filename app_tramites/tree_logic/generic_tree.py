# ============================================================
# ROL: LÓGICA — Árbol Genérico (desacoplado del ORM Django)
# ============================================================

class NodoArbol:
    def __init__(self, id, nombre, descripcion="", enlace="", hijos=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.enlace = enlace
        self.hijos = hijos or []


class ArbolGenerico:
    def __init__(self, raiz):
        self.raiz = raiz

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

    def buscar(self, nombre, nodo=None):
        if nodo is None:
            nodo = self.raiz
        if nodo.nombre.lower() == nombre.lower():
            return nodo
        for hijo in nodo.hijos:
            resultado = self.buscar(nombre, hijo)
            if resultado:
                return resultado
        return None

    def recorrido_dfs(self, nodo=None, nivel=0):
        """Recorrido en profundidad (DFS)"""
        if nodo is None:
            nodo = self.raiz
        resultado = [{"id": nodo.id, "nombre": nodo.nombre, "nivel": nivel}]
        for hijo in nodo.hijos:
            resultado.extend(self.recorrido_dfs(hijo, nivel + 1))
        return resultado

    def recorrido_bfs(self):
        """Recorrido por niveles (BFS)"""
        from collections import deque
        cola = deque([(self.raiz, 0)])
        resultado = []
        while cola:
            nodo, nivel = cola.popleft()
            resultado.append({"id": nodo.id, "nombre": nodo.nombre, "nivel": nivel})
            for hijo in nodo.hijos:
                cola.append((hijo, nivel + 1))
        return resultado

    def a_dict(self, nodo=None):
        """Serializa el árbol a diccionario (para JSON)"""
        if nodo is None:
            nodo = self.raiz
        return {
            "id": nodo.id,
            "nombre": nodo.nombre,
            "descripcion": nodo.descripcion,
            "enlace": nodo.enlace,
            "hijos": [self.a_dict(h) for h in nodo.hijos]
        }
