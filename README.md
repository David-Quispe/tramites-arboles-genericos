# RutaTree 🌳
Aplicación de rutas jerárquicas — Trámites Administrativos  
**Curso:** Estructura de Datos y Algoritmos — Semana 9  
**Tema:** Árboles genéricos con Django

## Requisitos
- Python 3.10+
- MySQL instalado

## Setup
```bash
# 1. Crear entorno virtual (ya existe el venv)
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear BD en MySQL
# CREATE DATABASE rutaTree CHARACTER SET utf8mb4;

# 4. Configurar credenciales en core_project/settings.py

# 5. Migraciones
python manage.py makemigrations
python manage.py migrate

# 6. Poblar datos de ejemplo
python manage.py shell < seed.py

# 7. Correr servidor
python manage.py runserver
```

## Endpoints
| URL | Descripción |
|-----|-------------|
| `/` | Interfaz HTML principal |
| `/api/arbol/` | Árbol completo en JSON |
| `/api/nodo/<id>/` | Nodo + sus hijos |
| `/api/nodo/<id>/altura/` | Altura desde ese nodo |
| `/api/buscar/?q=nombre` | Buscar nodo por nombre |
| `/api/recorrido/?tipo=dfs\|bfs` | Recorrido DFS o BFS |
| `/api/estadisticas/` | Altura, total nodos, hojas |

## Roles
| Rol | Archivos |
|-----|----------|
| Frontend | `templates/`, `static/css/`, `static/js/` |
| Backend | `views.py`, `urls.py`, `models.py` |
| Lógica | `tree_logic/generic_tree.py` |
