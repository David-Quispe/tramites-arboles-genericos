// ============================================================
// ROL: FRONTEND — Renderizado del árbol con collapse/expand
// ============================================================

function renderTree(nodo, container, nivel) {
  const iconosCls = ['ti-binary-tree', 'ti-folder', 'ti-file-text', 'ti-point'];
  const iconoCls  = iconosCls[Math.min(nivel, iconosCls.length - 1)];
  const tieneHijos = nodo.hijos && nodo.hijos.length > 0;

  const nodeDiv = document.createElement('div');
  nodeDiv.className = `tree-node nivel-${nivel}`;
  nodeDiv.dataset.id = nodo.id;

  const row = document.createElement('div');
  row.className = 'node-row';

  // Botón toggle
  const toggle = document.createElement('button');
  toggle.className = 'node-toggle';
  if (tieneHijos) {
    toggle.innerHTML = '<i class="ti ti-chevron-down" aria-hidden="true"></i>';
    toggle.setAttribute('aria-label', 'Contraer');
  } else {
    toggle.innerHTML = '<span style="display:inline-block;width:20px"></span>';
    toggle.disabled = true;
    toggle.style.cursor = 'default';
  }
  row.appendChild(toggle);

  // Etiqueta
  const label = document.createElement('span');
  label.className = 'node-label';
  label.innerHTML = `<i class="ti ${iconoCls}" style="font-size:14px" aria-hidden="true"></i>${nodo.nombre}`;
  if (nodo.descripcion) label.title = nodo.descripcion;
  row.appendChild(label);

  nodeDiv.appendChild(row);

  // Hijos
  if (tieneHijos) {
    const childrenDiv = document.createElement('div');
    childrenDiv.className = 'children';
    nodo.hijos.forEach(hijo => renderTree(hijo, childrenDiv, nivel + 1));
    nodeDiv.appendChild(childrenDiv);

    toggle.addEventListener('click', () => {
      const abierto = !childrenDiv.classList.contains('collapsed');
      childrenDiv.classList.toggle('collapsed', abierto);
      toggle.innerHTML = abierto
        ? '<i class="ti ti-chevron-right" aria-hidden="true"></i>'
        : '<i class="ti ti-chevron-down" aria-hidden="true"></i>';
      toggle.setAttribute('aria-label', abierto ? 'Expandir' : 'Contraer');
    });
  }

  container.appendChild(nodeDiv);
}

function highlightNode(id) {
  document.querySelectorAll('.node-label.highlighted')
    .forEach(el => el.classList.remove('highlighted'));
  const target = document.querySelector(`.tree-node[data-id="${id}"] > .node-row > .node-label`);
  if (target) {
    target.classList.add('highlighted');
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}
