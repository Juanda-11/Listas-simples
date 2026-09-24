"""
=====================================================================================
 BACKEND - API REST (Flask)
 Expone la estructura de datos ListaTareas (Lista Enlazada Simple) al Frontend.
=====================================================================================
Para ejecutar:
    1. pip install flask
    2. python app.py
    3. Abrir el navegador en http://127.0.0.1:5000
=====================================================================================
"""

from flask import Flask, jsonify, request, render_template
from lista_enlazada import (
    ListaTareas,
    TareaNoEncontradaError,
    ListaVaciaError,
    PrioridadInvalidaError,
)

app = Flask(__name__)

# La estructura de datos vive en memoria mientras el servidor está corriendo.
# Es EXACTAMENTE la lista enlazada simple construida en lista_enlazada.py
lista_tareas = ListaTareas()

# Datos de ejemplo para que el frontend no arranque vacío
lista_tareas.agregar_tarea("Estudiar listas enlazadas", "Repasar teoría de nodos y punteros", "alta")
lista_tareas.agregar_tarea("Hacer el taller de Python", "Implementar la clase ListaTareas", "alta")
lista_tareas.agregar_tarea("Construir el Frontend", "Conectar HTML/JS con la API Flask", "media")
lista_tareas.marcar_completada(1)


# -------------------------------------------------------------------------
# RUTA PRINCIPAL -> sirve el Frontend
# -------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------------------------------
# API: LISTAR TAREAS (con filtros opcionales)
#   GET /api/tareas
#   GET /api/tareas?estado=pendientes|completadas
#   GET /api/tareas?prioridad=alta|media|baja
# -------------------------------------------------------------------------
@app.route("/api/tareas", methods=["GET"])
def obtener_tareas():
    estado = request.args.get("estado")
    prioridad = request.args.get("prioridad")

    if estado == "pendientes":
        datos = lista_tareas.obtener_pendientes()
    elif estado == "completadas":
        datos = lista_tareas.obtener_completadas()
    elif prioridad:
        datos = lista_tareas.filtrar_por_prioridad(prioridad)
    else:
        datos = lista_tareas.obtener_todas()

    return jsonify({"ok": True, "tareas": datos, "total": len(datos)})


# -------------------------------------------------------------------------
# API: ESTADÍSTICAS
#   GET /api/tareas/estadisticas
# -------------------------------------------------------------------------
@app.route("/api/tareas/estadisticas", methods=["GET"])
def obtener_estadisticas():
    return jsonify({"ok": True, "estadisticas": lista_tareas.estadisticas()})


# -------------------------------------------------------------------------
# API: CREAR TAREA (inserta un nuevo nodo al final de la lista)
#   POST /api/tareas   body: {titulo, descripcion, prioridad, al_inicio}
# -------------------------------------------------------------------------
@app.route("/api/tareas", methods=["POST"])
def crear_tarea():
    body = request.get_json(silent=True) or {}
    titulo = body.get("titulo", "")
    descripcion = body.get("descripcion", "")
    prioridad = body.get("prioridad", "media")
    al_inicio = bool(body.get("al_inicio", False))

    try:
        if al_inicio:
            nodo = lista_tareas.agregar_al_inicio(titulo, descripcion, prioridad)
        else:
            nodo = lista_tareas.agregar_tarea(titulo, descripcion, prioridad)
        return jsonify({"ok": True, "tarea": nodo.a_diccionario()}), 201
    except (ValueError, PrioridadInvalidaError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# -------------------------------------------------------------------------
# API: ACTUALIZAR TAREA (modifica los datos de un nodo existente)
#   PUT /api/tareas/<id>   body: {titulo, descripcion, prioridad}
# -------------------------------------------------------------------------
@app.route("/api/tareas/<int:id_>", methods=["PUT"])
def actualizar_tarea(id_):
    body = request.get_json(silent=True) or {}
    try:
        nodo = lista_tareas.actualizar_tarea(
            id_,
            titulo=body.get("titulo"),
            descripcion=body.get("descripcion"),
            prioridad=body.get("prioridad"),
        )
        return jsonify({"ok": True, "tarea": nodo.a_diccionario()})
    except TareaNoEncontradaError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except (ValueError, PrioridadInvalidaError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# -------------------------------------------------------------------------
# API: ALTERNAR ESTADO COMPLETADA/PENDIENTE
#   PATCH /api/tareas/<id>/completar
# -------------------------------------------------------------------------
@app.route("/api/tareas/<int:id_>/completar", methods=["PATCH"])
def alternar_completada(id_):
    try:
        nodo = lista_tareas.alternar_completada(id_)
        return jsonify({"ok": True, "tarea": nodo.a_diccionario()})
    except TareaNoEncontradaError as e:
        return jsonify({"ok": False, "error": str(e)}), 404


# -------------------------------------------------------------------------
# API: MOVER TAREA AL INICIO (reordenar punteros de la lista)
#   PATCH /api/tareas/<id>/mover-inicio
# -------------------------------------------------------------------------
@app.route("/api/tareas/<int:id_>/mover-inicio", methods=["PATCH"])
def mover_al_inicio(id_):
    try:
        lista_tareas.mover_al_inicio(id_)
        return jsonify({"ok": True, "tareas": lista_tareas.obtener_todas()})
    except TareaNoEncontradaError as e:
        return jsonify({"ok": False, "error": str(e)}), 404


# -------------------------------------------------------------------------
# API: INVERTIR LA LISTA ENLAZADA (redirige todos los punteros 'siguiente')
#   PATCH /api/tareas/invertir
# -------------------------------------------------------------------------
@app.route("/api/tareas/invertir", methods=["PATCH"])
def invertir_lista():
    lista_tareas.invertir()
    return jsonify({"ok": True, "tareas": lista_tareas.obtener_todas()})


# -------------------------------------------------------------------------
# API: ELIMINAR TAREA (desenlaza el nodo de la lista)
#   DELETE /api/tareas/<id>
# -------------------------------------------------------------------------
@app.route("/api/tareas/<int:id_>", methods=["DELETE"])
def eliminar_tarea(id_):
    try:
        lista_tareas.eliminar_tarea(id_)
        return jsonify({"ok": True, "mensaje": f"Tarea {id_} eliminada."})
    except (TareaNoEncontradaError, ListaVaciaError) as e:
        return jsonify({"ok": False, "error": str(e)}), 404


# -------------------------------------------------------------------------
# API: VACIAR TODA LA LISTA
#   DELETE /api/tareas
# -------------------------------------------------------------------------
@app.route("/api/tareas", methods=["DELETE"])
def vaciar_lista():
    lista_tareas.vaciar()
    return jsonify({"ok": True, "mensaje": "Todas las tareas fueron eliminadas."})


if __name__ == "__main__":
    app.run(debug=True)
