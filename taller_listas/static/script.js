// =====================================================================================
// FRONTEND - Lógica de consumo de la API REST del Backend (Lista Enlazada Simple)
// =====================================================================================

const API_BASE = "/api/tareas";
let filtroActual = "todas";

const elLista = document.getElementById("lista-tareas");
const elMensajeVacio = document.getElementById("mensaje-vacio");
const elForm = document.getElementById("form-tarea");

// ---------------------------------------------------------------------------
// CARGA Y RENDER DE TAREAS
// ---------------------------------------------------------------------------
async function cargarTareas() {
  let url = API_BASE;
  if (filtroActual === "pendientes") url += "?estado=pendientes";
  if (filtroActual === "completadas") url += "?estado=completadas";

  const resp = await fetch(url);
  const data = await resp.json();
  renderTareas(data.tareas || []);
  await cargarEstadisticas();
}

function renderTareas(tareas) {
  elLista.innerHTML = "";

  if (tareas.length === 0) {
    elMensajeVacio.style.display = "block";
    return;
  }
  elMensajeVacio.style.display = "none";

  tareas.forEach((tarea, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "nodo";

    const card = document.createElement("div");
    card.className = `nodo-card prioridad-${tarea.prioridad}` + (tarea.completada ? " completada" : "");
    card.innerHTML = `
      <div class="nodo-header">
        <span class="nodo-titulo ${tarea.completada ? "tachado" : ""}">${escapeHtml(tarea.titulo)}</span>
      </div>
      <div class="nodo-desc">${escapeHtml(tarea.descripcion || "")}</div>
      <div class="nodo-footer">
        <span class="nodo-id">nodo #${tarea.id}</span>
        <div class="nodo-actions">
          <button title="Marcar completada" onclick="toggleCompletada(${tarea.id})">${tarea.completada ? "↺" : "✔️"}</button>
          <button title="Mover al inicio" onclick="moverAlInicio(${tarea.id})">⬆️</button>
          <button title="Eliminar nodo" onclick="eliminarTarea(${tarea.id})">🗑️</button>
        </div>
      </div>
    `;
    wrapper.appendChild(card);

    // Flecha de puntero "siguiente" entre nodos, como en la lista enlazada real
    if (index < tareas.length - 1) {
      const flecha = document.createElement("span");
      flecha.className = "puntero";
      flecha.textContent = "→";
      wrapper.appendChild(flecha);
    } else {
      const flecha = document.createElement("span");
      flecha.className = "puntero";
      flecha.textContent = "→";
      wrapper.appendChild(flecha);
      const nulo = document.createElement("div");
      nulo.className = "null-final";
      nulo.textContent = "NULL";
      wrapper.appendChild(nulo);
    }

    elLista.appendChild(wrapper);
  });
}

function escapeHtml(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// ESTADÍSTICAS
// ---------------------------------------------------------------------------
async function cargarEstadisticas() {
  const resp = await fetch(`${API_BASE}/estadisticas`);
  const data = await resp.json();
  const s = data.estadisticas;

  document.getElementById("stat-total").textContent = s.total;
  document.getElementById("stat-pendientes").textContent = s.pendientes;
  document.getElementById("stat-completadas").textContent = s.completadas;
  document.getElementById("stat-porcentaje").textContent = `${s.porcentaje_completado}% completado`;
  document.getElementById("progress-fill").style.width = `${s.porcentaje_completado}%`;
}

// ---------------------------------------------------------------------------
// ACCIONES (crear, completar, eliminar, mover, invertir, vaciar)
// ---------------------------------------------------------------------------
elForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const titulo = document.getElementById("input-titulo").value.trim();
  const descripcion = document.getElementById("input-descripcion").value.trim();
  const prioridad = document.getElementById("input-prioridad").value;
  const alInicio = document.getElementById("input-al-inicio").checked;

  if (!titulo) return;

  const resp = await fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titulo, descripcion, prioridad, al_inicio: alInicio }),
  });

  if (resp.ok) {
    elForm.reset();
    document.getElementById("input-prioridad").value = "media";
    await cargarTareas();
  } else {
    const err = await resp.json();
    alert("Error: " + err.error);
  }
});

async function toggleCompletada(id) {
  await fetch(`${API_BASE}/${id}/completar`, { method: "PATCH" });
  await cargarTareas();
}

async function eliminarTarea(id) {
  if (!confirm("¿Eliminar este nodo de la lista?")) return;
  await fetch(`${API_BASE}/${id}`, { method: "DELETE" });
  await cargarTareas();
}

async function moverAlInicio(id) {
  await fetch(`${API_BASE}/${id}/mover-inicio`, { method: "PATCH" });
  await cargarTareas();
}

document.getElementById("btn-invertir").addEventListener("click", async () => {
  await fetch(`${API_BASE}/invertir`, { method: "PATCH" });
  await cargarTareas();
});

document.getElementById("btn-vaciar").addEventListener("click", async () => {
  if (!confirm("¿Vaciar toda la lista de tareas? Esta acción no se puede deshacer.")) return;
  await fetch(API_BASE, { method: "DELETE" });
  await cargarTareas();
});

// ---------------------------------------------------------------------------
// FILTROS
// ---------------------------------------------------------------------------
document.querySelectorAll(".filter-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    filtroActual = btn.dataset.filtro;
    cargarTareas();
  });
});

// ---------------------------------------------------------------------------
// INICIALIZACIÓN
// ---------------------------------------------------------------------------
cargarTareas();
