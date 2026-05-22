// ============================================================
// ROL: FRONTEND — Árbol Genérico
// ============================================================

// ── Configuración de tipos de nodo ───────────────────────────
const TIPO_CONFIG = {
  categoria: { icono: 'ti-folder',      etiqueta: 'Categoría', color: 'tipo-categoria' },
  tramite:   { icono: 'ti-file-check',  etiqueta: 'Trámite',   color: 'tipo-tramite'   },
  documento: { icono: 'ti-file-text',   etiqueta: 'Documento', color: 'tipo-documento' },
  accion:    { icono: 'ti-bolt',        etiqueta: 'Acción',    color: 'tipo-accion'    },
};

let nodoSeleccionado = null;

// ── Renderizado principal ─────────────────────────────────────
function renderTree(nodo, container, nivel) {
  const cfg        = TIPO_CONFIG[nodo.tipo] || TIPO_CONFIG['categoria'];
  const tieneHijos = nodo.hijos && nodo.hijos.length > 0;

  const nodeDiv = document.createElement('div');
  nodeDiv.className = `tree-node nivel-${Math.min(nivel, 3)}`;
  nodeDiv.dataset.id     = nodo.id;
  nodeDiv.dataset.nivel  = nivel;
  nodeDiv.dataset.tipo   = nodo.tipo;
  nodeDiv.dataset.nombre = nodo.nombre;
  nodeDiv.dataset.padre  = nodo.padre_id || '';

  const row = document.createElement('div');
  row.className = 'node-row';

  // Botón toggle colapsar/expandir
  const toggle = document.createElement('button');
  toggle.className = 'node-toggle';
  toggle.setAttribute('aria-label', tieneHijos ? 'Contraer' : '');
  toggle.innerHTML = tieneHijos
    ? '<i class="ti ti-chevron-down"></i>'
    : '<span style="width:20px;display:inline-block"></span>';
  toggle.disabled = !tieneHijos;
  row.appendChild(toggle);

  // Badge de nivel
  const nivelBadge = document.createElement('span');
  nivelBadge.className   = 'nivel-badge';
  nivelBadge.textContent = `N${nivel}`;
  nivelBadge.title       = nivelLabel(nivel);
  row.appendChild(nivelBadge);

  // Ícono del tipo (solo ícono, sin texto)
  const tipoIcono = document.createElement('span');
  tipoIcono.className = 'tipo-icono';
  tipoIcono.innerHTML = `<i class="ti ${cfg.icono}" title="${cfg.etiqueta}" style="color:var(--primary); font-size:.95rem;"></i>`;
  row.appendChild(tipoIcono);

  // Etiqueta del nodo
  const label = document.createElement('span');
  label.className = 'node-label';
  label.textContent = nodo.nombre;
  if (nodo.descripcion) label.title = nodo.descripcion;
  label.addEventListener('click', () => seleccionarNodo(nodo, nivel, nodeDiv));

  // Indicador visual de enlace
  if (nodo.enlace) {
    const linkIcon = document.createElement('i');
    linkIcon.className = 'ti ti-external-link';
    linkIcon.style.cssText = 'font-size:.72rem; color:var(--primary); margin-left:5px; opacity:.7;';
    linkIcon.title = `Enlace: ${nodo.enlace}`;
    label.appendChild(linkIcon);
  }

  if (nodo.cant_tramites > 0) {
    const countBadge = document.createElement('span');
    countBadge.className   = 'tramites-badge';
    countBadge.textContent = nodo.cant_tramites;
    countBadge.title       = `${nodo.cant_tramites} trámites en este subárbol`;
    label.appendChild(countBadge);
  }
  row.appendChild(label);

  nodeDiv.appendChild(row);

  // ── Hijos ──
  if (tieneHijos) {
    const childrenDiv = document.createElement('div');
    childrenDiv.className = 'children';

    nodo.hijos.forEach(hijo => {
      hijo.padre_id     = nodo.id;
      hijo.padre_nombre = nodo.nombre;
      renderTree(hijo, childrenDiv, nivel + 1);
    });

    nodeDiv.appendChild(childrenDiv);

    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const abierto = !childrenDiv.classList.contains('collapsed');
      childrenDiv.classList.toggle('collapsed', abierto);
      toggle.innerHTML = abierto
        ? '<i class="ti ti-chevron-right"></i>'
        : '<i class="ti ti-chevron-down"></i>';
      toggle.setAttribute('aria-label', abierto ? 'Expandir' : 'Contraer');
    });
  }

  container.appendChild(nodeDiv);
}

// ── Etiqueta de nivel ─────────────────────────────────────────
function nivelLabel(n) {
  const labels = ['Raíz', 'Categoría', 'Subtrámite', 'Documento'];
  return labels[n] || `Nivel ${n}`;
}

// ── Selección de nodo → panel de info ────────────────────────
function seleccionarNodo(nodo, nivel, div) {
  document.querySelectorAll('.tree-node.selected').forEach(el => el.classList.remove('selected'));
  div.classList.add('selected');
  nodoSeleccionado = { ...nodo, nivel };

  const panel = document.getElementById('nodeInfoPanel');
  if (!panel) return;

  const cfg = TIPO_CONFIG[nodo.tipo] || TIPO_CONFIG['categoria'];

  const filaEnlace = nodo.enlace
    ? `<tr>
        <td class="ik">Enlace</td>
        <td class="iv">
          <a href="${nodo.enlace}" target="_blank" rel="noopener"
             style="display:inline-flex; align-items:center; gap:4px; color:var(--primary); font-weight:500;">
            <i class="ti ti-external-link"></i> ${nodo.enlace}
          </a>
        </td>
       </tr>`
    : `<tr><td class="ik">Enlace</td><td class="iv" style="color:var(--text-muted);">—</td></tr>`;

  panel.innerHTML = `
    <div class="info-panel-title">
      <i class="ti ${cfg.icono}" style="color:var(--primary)"></i>
      ${nodo.nombre}
    </div>
    <table class="info-table">
      <tr><td class="ik">Tipo</td><td class="iv"><span class="tipo-badge ${cfg.color}"><i class="ti ${cfg.icono}"></i> ${cfg.etiqueta}</span></td></tr>
      <tr><td class="ik">Nivel</td><td class="iv"><span class="nivel-badge">N${nivel}</span> — ${nivelLabel(nivel)}</td></tr>
      <tr><td class="ik">Hijos directos</td><td class="iv">${nodo.hijos ? nodo.hijos.length : 0}</td></tr>
      <tr><td class="ik">Padre</td><td class="iv">${nodo.padre_nombre ? nodo.padre_nombre : '<em>raíz</em>'}</td></tr>
      ${nodo.descripcion ? `<tr><td class="ik">Descripción</td><td class="iv">${nodo.descripcion}</td></tr>` : ''}
      ${filaEnlace}
    </table>
    ${nivel > 0 ? `
    <div class="info-panel-actions">
      <a href="/nodos/${nodo.id}/editar/"   class="btn btn-secondary btn-xs"><i class="ti ti-edit"></i> Editar</a>
      <a href="/nodos/${nodo.id}/eliminar/" class="btn btn-danger btn-xs"><i class="ti ti-trash"></i> Eliminar</a>
      <button onclick="mostrarMoverNodo(${nodo.id})" class="btn btn-secondary btn-xs"><i class="ti ti-arrows-move"></i> Mover</button>
      <a href="/nodos/nuevo/${nodo.id}/"    class="btn btn-primary btn-xs"><i class="ti ti-plus"></i> Hijo</a>
    </div>` : `
    <div class="info-panel-actions">
      <a href="/nodos/${nodo.id}/editar/"   class="btn btn-secondary btn-xs"><i class="ti ti-edit"></i> Editar</a>
      <a href="/nodos/nuevo/${nodo.id}/"    class="btn btn-primary btn-xs"><i class="ti ti-plus"></i> Agregar hijo</a>
    </div>`}
  `;
  panel.style.display = 'block';
}

// ── Búsqueda con ruta ─────────────────────────────────────────
function buscarNodo() {
  const q        = document.getElementById('searchInput').value.trim();
  const resultEl = document.getElementById('searchResult');
  const rutaEl   = document.getElementById('rutaOutput');
  if (!q) return;

  fetch(`/api/buscar/?q=${encodeURIComponent(q)}`)
    .then(r => r.json())
    .then(data => {
      document.querySelectorAll('.node-label.highlighted').forEach(el => el.classList.remove('highlighted'));
      document.querySelectorAll('.node-label.highlight-path').forEach(el => el.classList.remove('highlight-path'));

      if (data.encontrado) {
        resultEl.className   = 'found';
        resultEl.textContent = `✓ "${data.nombre}" encontrado`;

        if (data.ruta) {
          data.ruta.forEach((item, index) => {
            const nodeDiv = document.querySelector(`.tree-node[data-id="${item.id}"]`);
            if (nodeDiv) {
              const labelEl = nodeDiv.querySelector('.node-row > .node-label');
              if (labelEl) {
                if (index === data.ruta.length - 1) {
                  labelEl.classList.add('highlighted');
                  labelEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                  labelEl.classList.add('highlight-path');
                }
              }
              let parent = nodeDiv.parentElement;
              while (parent) {
                if (parent.classList.contains('children') && parent.classList.contains('collapsed')) {
                  parent.classList.remove('collapsed');
                  const toggleBtn = parent.previousElementSibling?.querySelector('.node-toggle');
                  if (toggleBtn) toggleBtn.innerHTML = '<i class="ti ti-chevron-down"></i>';
                }
                parent = parent.parentElement;
              }
            }
          });
        }

        if (data.ruta && rutaEl) {
          rutaEl.style.display = 'block';
          rutaEl.innerHTML = '<div class="ruta-label">Ruta:</div>' +
            data.ruta.map((n, i) => {
              const c = TIPO_CONFIG[n.tipo] || TIPO_CONFIG['categoria'];
              const indent = '&nbsp;'.repeat(i * 4) + (i > 0 ? '└── ' : '');
              return `<div class="ruta-item">${indent}<i class="ti ${c.icono}"></i> ${n.nombre}</div>`;
            }).join('');
        }
      } else {
        resultEl.className   = 'notfound';
        resultEl.textContent = `✗ "${q}" no encontrado`;
        if (rutaEl) rutaEl.style.display = 'none';
      }
    });
}

// ── Mover subárbol ────────────────────────────────────────────
function mostrarMoverNodo(nodoId) {
  const modal = document.getElementById('moverModal');
  if (!modal) return;
  document.getElementById('moverNodoId').value = nodoId;
  document.getElementById('moverNombreNodo').textContent =
    document.querySelector(`.tree-node[data-id="${nodoId}"] .node-label`)?.textContent || '';
  document.getElementById('moverMsg').textContent = '';
  document.getElementById('moverMsg').className   = 'mover-msg';

  const sel = document.getElementById('moverNuevoPadre');
  sel.innerHTML = '<option value="">Cargando...</option>';
  fetch('/api/recorrido/?tipo=bfs')
    .then(r => r.json())
    .then(data => {
      sel.innerHTML = '<option value="">— Selecciona el nuevo padre —</option>';
      data.recorrido.forEach(n => {
        if (n.id === nodoId) return;
        const opt = document.createElement('option');
        opt.value       = n.id;
        opt.textContent = '\u00A0'.repeat(n.nivel * 3) + (n.nivel > 0 ? '\u2514 ' : '') + n.nombre;
        sel.appendChild(opt);
      });
    })
    .catch(() => { sel.innerHTML = '<option value="">Error al cargar</option>'; });

  modal.style.display = 'flex';
}

function cerrarMoverModal() {
  const modal = document.getElementById('moverModal');
  if (modal) modal.style.display = 'none';
}

function confirmarMoverNodo() {
  const nodoId       = parseInt(document.getElementById('moverNodoId').value);
  const nuevoPadreId = parseInt(document.getElementById('moverNuevoPadre').value);
  const msgEl        = document.getElementById('moverMsg');

  if (!nuevoPadreId) {
    msgEl.textContent = 'Selecciona el nuevo padre.';
    msgEl.className   = 'mover-msg error';
    return;
  }
  if (nodoId === nuevoPadreId) {
    msgEl.textContent = '❌ Un nodo no puede ser hijo de sí mismo.';
    msgEl.className   = 'mover-msg error';
    return;
  }

  fetch('/api/mover/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
    body: JSON.stringify({ nodo_id: nodoId, nuevo_padre_id: nuevoPadreId }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        msgEl.textContent = '✅ ' + data.mensaje;
        msgEl.className   = 'mover-msg ok';
        setTimeout(() => { cerrarMoverModal(); location.reload(); }, 1200);
      } else {
        msgEl.textContent = '❌ ' + data.error;
        msgEl.className   = 'mover-msg error';
      }
    });
}

// ── Resaltado por ID ──────────────────────────────────────────
function highlightNode(id) {
  document.querySelectorAll('.node-label.highlighted').forEach(el => el.classList.remove('highlighted'));
  const target = document.querySelector(`.tree-node[data-id="${id}"] > .node-row > .node-label`);
  if (target) {
    target.classList.add('highlighted');
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// ── Utilidad CSRF ─────────────────────────────────────────────
function getCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}
