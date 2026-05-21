# RutaTree 🌳
Aplicación de rutas jerárquicas — Trámites Administrativos  
**Curso:** Estructura de Datos y Algoritmos — Semana 9  
**Tema:** Árboles genéricos con Django

## Requisitos
- Python 3.10+
- MySQL 8.x (opcional, usa SQLite por defecto)

## Setup
```bash
# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env (opcional, valores por defecto funcionan)
# Copia y edita .env según tu base de datos:
# DEBUG=True
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3

# 4. Migraciones
python manage.py migrate

# 5. Poblar datos de ejemplo
python manage.py shell < seed.py

# 6. Crear superusuario (para el panel admin)
python manage.py createsuperuser

# 7. Correr servidor
python manage.py runserver
```

## Estructura del proyecto
```
├── app_tramites/
│   ├── models.py          # 6 modelos: NodoTramite, Carrera, Alumno, Pension, Beca, Documento
│   ├── views.py           # Vistas HTML + API JSON
│   ├── forms.py           # Formularios con validación
│   ├── urls.py            # Rutas de la aplicación
│   ├── admin.py           # Panel de administración
│   ├── templates/tramites/  # 11 templates HTML
│   └── tree_logic/        # Árbol genérico (desacoplado del ORM)
│       └── generic_tree.py # NodoArbol + ArbolGenerico: altura, DFS, BFS, búsqueda
├── core_project/
│   └── settings.py        # Configuración vía .env
├── static/
│   ├── css/styles.css     # Diseño completo con variables CSS
│   └── js/tree_render.js  # Renderizado interactivo del árbol
├── .env                   # Variables de entorno (secret key, DB, debug)
├── .gitignore
├── requirements.txt
└── seed.py                # Datos de ejemplo para el árbol
```

## Modelos
| Modelo | Descripción |
|--------|-------------|
| `NodoTramite` | Nodos del árbol jerárquico con nombre, descripción, orden y enlace opcional |
| `Carrera` | Programas académicos (código, nombre, duración) |
| `Alumno` | Estudiantes con DNI, carrera, año, ciclo |
| `Pension` | Pagos de pensión por alumno, mes y año |
| `Beca` | Becas asociadas a alumnos (excelencia, necesidad, deportiva, convenio) |
| `Documento` | Solicitudes de documentos (certificados, títulos) |

## URLs principales
### Interfaz HTML
| URL | Descripción |
|-----|-------------|
| `/` | Dashboard con estadísticas y árbol interactivo |
| `/admin/` | Panel de administración Django |
| `/alumnos/` | Lista de alumnos con búsqueda y paginación |
| `/alumnos/nuevo/` | Registrar alumno |
| `/alumnos/<dni>/` | Ficha del alumno (pensiones, becas, documentos) |
| `/carreras/` | Lista de carreras con estadísticas |
| `/nodos/nuevo/` | Crear nodo raíz del árbol |
| `/nodos/<id>/editar/` | Editar nodo del árbol |

### API REST (árbol genérico)
| URL | Descripción |
|-----|-------------|
| `/api/arbol/` | Árbol completo en JSON |
| `/api/nodo/<id>/` | Nodo + sus hijos |
| `/api/nodo/<id>/altura/` | Altura desde ese nodo |
| `/api/buscar/?q=nombre` | Buscar nodo por nombre |
| `/api/recorrido/?tipo=dfs\|bfs` | Recorrido DFS o BFS |
| `/api/estadisticas/` | Altura, total nodos, hojas |

## Características
- **Árbol genérico** implementado en Python puro, desacoplado del ORM
- **Dashboard** con estadísticas, tarjetas resumen y árbol interactivo (colapsar/expandir)
- **CRUD completo** con formularios validados y mensajes de feedback
- **Eliminación** con confirmación para todas las entidades
- **Paginación** (25 items por página) y búsqueda en listas
- **Panel admin** con list_display, search_fields y list_filter
- **Configuración segura** via `.env` con python-decouple
- **Diseño responsive** con sidebar, CSS custom properties y Tabler Icons

## Roles
| Rol | Archivos |
|-----|----------|
| Frontend | `templates/`, `static/css/`, `static/js/` |
| Backend | `views.py`, `urls.py`, `models.py`, `forms.py` |
| Lógica | `tree_logic/generic_tree.py` |
