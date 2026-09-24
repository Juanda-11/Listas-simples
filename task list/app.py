"""
=====================================================================================
 BACKEND - REST API (Flask)
 Exposes the TaskList data structure (Singly Linked List) to the Frontend.
=====================================================================================
To run:
    1. pip install flask
    2. python app.py
    3. Open your browser at http://127.0.0.1:5000
=====================================================================================
"""

from flask import Flask, jsonify, request, render_template
from linked_list import (
    TaskList,
    TaskNotFoundError,
    EmptyListError,
    InvalidPriorityError,
)

app = Flask(__name__)

# The data structure lives in memory while the server is running.
# It is EXACTLY the singly linked list built in linked_list.py
task_list = TaskList()

# Sample data so the frontend doesn't start empty
task_list.add_task("Study linked lists", "Review the theory of nodes and pointers", "high")
task_list.add_task("Do the Python workshop", "Implement the TaskList class", "high")
task_list.add_task("Build the Frontend", "Connect HTML/JS with the Flask API", "medium")
task_list.mark_completed(1)


# -------------------------------------------------------------------------
# MAIN ROUTE -> serves the Frontend
# -------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------------------------------
# API: LIST TASKS (with optional filters)
#   GET /api/tasks
#   GET /api/tasks?status=pending|completed
#   GET /api/tasks?priority=high|medium|low
# -------------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    status = request.args.get("status")
    priority = request.args.get("priority")

    if status == "pending":
        data = task_list.get_pending()
    elif status == "completed":
        data = task_list.get_completed()
    elif priority:
        data = task_list.filter_by_priority(priority)
    else:
        data = task_list.get_all()

    return jsonify({"ok": True, "tasks": data, "total": len(data)})


# -------------------------------------------------------------------------
# API: STATISTICS
#   GET /api/tasks/statistics
# -------------------------------------------------------------------------
@app.route("/api/tasks/statistics", methods=["GET"])
def get_statistics():
    return jsonify({"ok": True, "statistics": task_list.get_statistics()})


# -------------------------------------------------------------------------
# API: CREATE TASK (inserts a new node at the end of the list)
#   POST /api/tasks   body: {title, description, priority, at_start}
# -------------------------------------------------------------------------
@app.route("/api/tasks", methods=["POST"])
def create_task():
    body = request.get_json(silent=True) or {}
    title = body.get("title", "")
    description = body.get("description", "")
    priority = body.get("priority", "medium")
    at_start = bool(body.get("at_start", False))

    try:
        if at_start:
            node = task_list.add_to_start(title, description, priority)
        else:
            node = task_list.add_task(title, description, priority)
        return jsonify({"ok": True, "task": node.to_dict()}), 201
    except (ValueError, InvalidPriorityError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# -------------------------------------------------------------------------
# API: UPDATE TASK (modifies the data of an existing node)
#   PUT /api/tasks/<id>   body: {title, description, priority}
# -------------------------------------------------------------------------
@app.route("/api/tasks/<int:id_>", methods=["PUT"])
def update_task(id_):
    body = request.get_json(silent=True) or {}
    try:
        node = task_list.update_task(
            id_,
            title=body.get("title"),
            description=body.get("description"),
            priority=body.get("priority"),
        )
        return jsonify({"ok": True, "task": node.to_dict()})
    except TaskNotFoundError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except (ValueError, InvalidPriorityError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# -------------------------------------------------------------------------
# API: TOGGLE COMPLETED/PENDING STATUS
#   PATCH /api/tasks/<id>/complete
# -------------------------------------------------------------------------
@app.route("/api/tasks/<int:id_>/complete", methods=["PATCH"])
def toggle_completed(id_):
    try:
        node = task_list.toggle_completed(id_)
        return jsonify({"ok": True, "task": node.to_dict()})
    except TaskNotFoundError as e:
        return jsonify({"ok": False, "error": str(e)}), 404


# -------------------------------------------------------------------------
# API: MOVE TASK TO THE START (reorders the list's pointers)
#   PATCH /api/tasks/<id>/move-to-start
# -------------------------------------------------------------------------
@app.route("/api/tasks/<int:id_>/move-to-start", methods=["PATCH"])
def move_to_start(id_):
    try:
        task_list.move_to_start(id_)
        return jsonify({"ok": True, "tasks": task_list.get_all()})
    except TaskNotFoundError as e:
        return jsonify({"ok": False, "error": str(e)}), 404


# -------------------------------------------------------------------------
# API: REVERSE THE LINKED LIST (redirects all 'next' pointers)
#   PATCH /api/tasks/reverse
# -------------------------------------------------------------------------
@app.route("/api/tasks/reverse", methods=["PATCH"])
def reverse_list():
    task_list.reverse()
    return jsonify({"ok": True, "tasks": task_list.get_all()})


# -------------------------------------------------------------------------
# API: DELETE TASK (unlinks the node from the list)
#   DELETE /api/tasks/<id>
# -------------------------------------------------------------------------
@app.route("/api/tasks/<int:id_>", methods=["DELETE"])
def delete_task(id_):
    try:
        task_list.remove_task(id_)
        return jsonify({"ok": True, "message": f"Task {id_} removed."})
    except (TaskNotFoundError, EmptyListError) as e:
        return jsonify({"ok": False, "error": str(e)}), 404


# -------------------------------------------------------------------------
# API: CLEAR THE WHOLE LIST
#   DELETE /api/tasks
# -------------------------------------------------------------------------
@app.route("/api/tasks", methods=["DELETE"])
def clear_list():
    task_list.clear()
    return jsonify({"ok": True, "message": "All tasks were removed."})


if __name__ == "__main__":
    app.run(debug=True)
