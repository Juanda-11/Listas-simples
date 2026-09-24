# Singly Linked Lists Workshop applied to a case study
**Course:** Data Structures
**Case study:** To-Do Task Manager
**Technologies:** Python (OOP) + Flask (Backend/API) + HTML/CSS/JS (Frontend)

---

## 1. Problem description

The goal is to create a Python script that manages a **to-do task list**,
where **each node represents a task** and holds a **reference (pointer) to
the next node** containing the following task in the list. The workshop
must include a **Frontend**.

This is exactly the definition of a **Singly Linked List**:

```
[Task A | *next] --> [Task B | *next] --> [Task C | NULL]
   head                                       tail
```

## 2. Project architecture

```
task_list_project/
├── linked_list.py         # Core of the workshop: Node + TaskList (pure OOP, no dependencies)
├── app.py                  # Flask backend: exposes the linked list as a REST API
├── templates/
│   └── index.html          # Frontend: page structure
├── static/
│   ├── style.css            # Frontend: styles
│   └── script.js              # Frontend: API consumption (fetch) and dynamic rendering
├── requirements.txt
└── README.md
```

**Why this architecture?**
- `linked_list.py` is **fully self-contained**: you can run it from the console
  (`python linked_list.py`) without needing Flask, ideal for demonstrating the
  data structure during the oral defense.
- `app.py` does NOT reimplement the logic: it only exposes it over HTTP,
  fulfilling the requirement of having a working Frontend that consumes the
  data structure.

## 3. Classes and OOP concepts applied

| Class | Role |
|---|---|
| `Node` | Represents an element of the list: task data + `next` pointer |
| `TaskList` | Container structure: keeps `head`, `tail` and `size`, and exposes the linked list's methods |
| `TaskNotFoundError`, `EmptyListError`, `InvalidPriorityError` | Custom exceptions for robust error handling |

OOP concepts used: **encapsulation** (attributes managed through methods),
**`__slots__`** to optimize node memory usage, **custom exception handling**,
**iterators** (`__iter__`, `__len__`) to allow traversing the list with
`for node in task_list:`.

## 4. Operations implemented on the linked list

| Method | Operation | Complexity |
|---|---|---|
| `add_task()` | Inserts a node at the end | O(1) |
| `add_to_start()` | Inserts a node at the start | O(1) |
| `find_task(id)` | Traverses the list looking for an id | O(n) |
| `remove_task(id)` | Unlinks a node, reconnecting the previous one with the next | O(n) |
| `update_task(id, ...)` | Modifies a node's data without touching pointers | O(n) |
| `mark_completed(id)` / `toggle_completed(id)` | Changes a task's status | O(n) |
| `move_to_start(id)` | Reorders the list by moving an existing node to the head | O(n) |
| `reverse()` | Reverses the direction of every `next` pointer | O(n) |
| `clear()` | Removes all nodes | O(1) |
| `get_statistics()` | Traverses the list and generates a summary (total, pending, completed, %) | O(n) |

## 5. REST API exposed by the Backend (`app.py`)

| Method | Route | Description |
|---|---|---|
| GET | `/api/tasks` | Lists all tasks (or filters by `?status=` / `?priority=`) |
| GET | `/api/tasks/statistics` | Returns the statistical summary |
| POST | `/api/tasks` | Creates a task (new node) |
| PUT | `/api/tasks/<id>` | Edits an existing task |
| PATCH | `/api/tasks/<id>/complete` | Toggles the completed/pending status |
| PATCH | `/api/tasks/<id>/move-to-start` | Moves the node to the start of the list |
| PATCH | `/api/tasks/reverse` | Reverses the entire linked list |
| DELETE | `/api/tasks/<id>` | Removes a specific node |
| DELETE | `/api/tasks` | Clears the entire list |

## 6. Frontend

A web interface that consumes the API through plain JavaScript `fetch()`
(no frameworks), and **visualizes the list as a chain of nodes connected by
arrows (→ ... → NULL)**, to visually reinforce the linked list concept. It
includes:
- A form to add tasks (at the start or at the end).
- Node cards showing priority, status and description.
- Filters (all / pending / completed).
- Buttons to reverse the list and clear it.
- A statistics panel with a progress bar.

## 7. How to run the project

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python app.py

# 3. Open in your browser
http://127.0.0.1:5000
```

### Running just the data structure from the console (no Frontend)
```bash
python linked_list.py
```

## 8. Possible defense questions (with quick answers)

- **Why is appending at the end O(1) if it's a singly linked list?**
  Because an extra `tail` pointer is kept, always referencing the last node,
  which avoids traversing the whole list.
- **What happens if I remove the head or the tail?**
  `remove_task()` handles both cases: if it's the head, `self.head` is
  updated; if it's the tail, `self.tail` is updated using the `previous`
  node tracked during the traversal.
- **How do you reverse a singly linked list?**
  By traversing the list once and, at each node, redirecting its `next`
  pointer to point to the previous node (`reverse()` method), in O(n) time
  and O(1) extra space.
