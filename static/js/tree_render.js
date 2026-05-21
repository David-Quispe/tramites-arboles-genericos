function renderTree(nodo, container, nivel) {
  const iconosCls = ['ti-binary-tree', 'ti-folder', 'ti-file-text', 'ti-point'];
  const iconoCls  = iconosCls[Math.min(nivel, iconosCls.length - 1)];
  const tieneHijos = nodo.hijos && nodo.hijos.length > 0;
  const esHoja = !tieneHijos;

  const nodeDiv = document.createElement('div');
  nodeDiv.className = `tree-node nivel-${nivel}`;
  nodeDiv.dataset.id = nodo.id;

  const row = document.createElement('div');
  row.className = 'node-row';

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

  const label = document.createElement('span');
  label.className = 'node-label';
  if (nodo.enlace) {
    const link = document.createElement('a');
    link.href = nodo.enlace;
    link.className = 'node-link';
    link.innerHTML = `<i class="ti ${iconoCls}" style="font-size:14px" aria-hidden="true"></i>${nodo.nombre}`;
    if (nodo.descripcion) link.title = nodo.descripcion;
    label.appendChild(link);
  } else {
    label.innerHTML = `<i class="ti ${iconoCls}" style="font-size:14px" aria-hidden="true"></i>${nodo.nombre}`;
    if (nodo.descripcion) label.title = nodo.descripcion;
  }
  row.appendChild(label);

  const actions = document.createElement('span');
  actions.className = 'node-actions';

  const addBtn = document.createElement('a');
  addBtn.href = `/nodos/nuevo/${nodo.id}/`;
  addBtn.className = 'node-btn';
  addBtn.title = 'Añadir hijo';
  addBtn.innerHTML = '<i class="ti ti-plus" aria-hidden="true"></i>';
  actions.appendChild(addBtn);

  const editBtn = document.createElement('a');
  editBtn.href = `/nodos/${nodo.id}/editar/`;
  editBtn.className = 'node-btn';
  editBtn.title = 'Editar';
  editBtn.innerHTML = '<i class="ti ti-edit" aria-hidden="true"></i>';
  actions.appendChild(editBtn);

  const delBtn = document.createElement('a');
  delBtn.href = `/nodos/${nodo.id}/eliminar/`;
  delBtn.className = 'node-btn node-btn-del';
  delBtn.title = 'Eliminar';
  delBtn.innerHTML = '<i class="ti ti-trash" aria-hidden="true"></i>';
  actions.appendChild(delBtn);

  row.appendChild(actions);
  nodeDiv.appendChild(row);

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
