// =====================================================================================
// FRONTEND - REST API consumption logic (Singly Linked List)
// =====================================================================================

const API_BASE = "/api/tasks";
let currentFilter = "all";

const elList = document.getElementById("task-list");
const elEmptyMessage = document.getElementById("empty-message");
const elForm = document.getElementById("task-form");

// ---------------------------------------------------------------------------
// LOAD AND RENDER TASKS
// ---------------------------------------------------------------------------
async function loadTasks() {
  let url = API_BASE;
  if (currentFilter === "pending") url += "?status=pending";
  if (currentFilter === "completed") url += "?status=completed";

  const resp = await fetch(url);
  const data = await resp.json();
  renderTasks(data.tasks || []);
  await loadStatistics();
}

function renderTasks(tasks) {
  elList.innerHTML = "";

  if (tasks.length === 0) {
    elEmptyMessage.style.display = "block";
    return;
  }
  elEmptyMessage.style.display = "none";

  tasks.forEach((task, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "node";

    const card = document.createElement("div");
    card.className = `node-card priority-${task.priority}` + (task.completed ? " completed" : "");
    card.innerHTML = `
      <div class="node-header">
        <span class="node-title ${task.completed ? "strikethrough" : ""}">${escapeHtml(task.title)}</span>
      </div>
      <div class="node-desc">${escapeHtml(task.description || "")}</div>
      <div class="node-footer">
        <span class="node-id">node #${task.id}</span>
        <div class="node-actions">
          <button title="Mark as completed" onclick="toggleCompleted(${task.id})">${task.completed ? "↺" : "✔️"}</button>
          <button title="Move to start" onclick="moveToStart(${task.id})">⬆️</button>
          <button title="Delete node" onclick="deleteTask(${task.id})">🗑️</button>
        </div>
      </div>
    `;
    wrapper.appendChild(card);

    // "next" pointer arrow between nodes, just like in a real linked list
    if (index < tasks.length - 1) {
      const arrow = document.createElement("span");
      arrow.className = "pointer";
      arrow.textContent = "→";
      wrapper.appendChild(arrow);
    } else {
      const arrow = document.createElement("span");
      arrow.className = "pointer";
      arrow.textContent = "→";
      wrapper.appendChild(arrow);
      const nullBox = document.createElement("div");
      nullBox.className = "null-end";
      nullBox.textContent = "NULL";
      wrapper.appendChild(nullBox);
    }

    elList.appendChild(wrapper);
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// STATISTICS
// ---------------------------------------------------------------------------
async function loadStatistics() {
  const resp = await fetch(`${API_BASE}/statistics`);
  const data = await resp.json();
  const s = data.statistics;

  document.getElementById("stat-total").textContent = s.total;
  document.getElementById("stat-pending").textContent = s.pending;
  document.getElementById("stat-completed").textContent = s.completed;
  document.getElementById("stat-percentage").textContent = `${s.completion_percentage}% completed`;
  document.getElementById("progress-fill").style.width = `${s.completion_percentage}%`;
}

// ---------------------------------------------------------------------------
// ACTIONS (create, complete, delete, move, reverse, clear)
// ---------------------------------------------------------------------------
elForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const title = document.getElementById("input-title").value.trim();
  const description = document.getElementById("input-description").value.trim();
  const priority = document.getElementById("input-priority").value;
  const atStart = document.getElementById("input-at-start").checked;

  if (!title) return;

  const resp = await fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description, priority, at_start: atStart }),
  });

  if (resp.ok) {
    elForm.reset();
    document.getElementById("input-priority").value = "medium";
    await loadTasks();
  } else {
    const err = await resp.json();
    alert("Error: " + err.error);
  }
});

async function toggleCompleted(id) {
  await fetch(`${API_BASE}/${id}/complete`, { method: "PATCH" });
  await loadTasks();
}

async function deleteTask(id) {
  if (!confirm("Delete this node from the list?")) return;
  await fetch(`${API_BASE}/${id}`, { method: "DELETE" });
  await loadTasks();
}

async function moveToStart(id) {
  await fetch(`${API_BASE}/${id}/move-to-start`, { method: "PATCH" });
  await loadTasks();
}

document.getElementById("btn-reverse").addEventListener("click", async () => {
  await fetch(`${API_BASE}/reverse`, { method: "PATCH" });
  await loadTasks();
});

document.getElementById("btn-clear").addEventListener("click", async () => {
  if (!confirm("Clear the entire task list? This action cannot be undone.")) return;
  await fetch(API_BASE, { method: "DELETE" });
  await loadTasks();
});

// ---------------------------------------------------------------------------
// FILTERS
// ---------------------------------------------------------------------------
document.querySelectorAll(".filter-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.dataset.filter;
    loadTasks();
  });
});

// ---------------------------------------------------------------------------
// INITIALIZATION
// ---------------------------------------------------------------------------
loadTasks();
