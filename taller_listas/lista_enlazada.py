"""
=====================================================================================
 TALLER: LISTAS SIMPLES (LISTAS ENLAZADAS) APLICADO A UN CASO DE ESTUDIO
 Caso de estudio: Gestor de Tareas Pendientes (To-Do List)
 Materia: Estructuras de Datos
 Docente: Jhonatan Andres Mideros Narvaez

 Descripción:
     Implementación de una LISTA ENLAZADA SIMPLE (Singly Linked List) usando
     Programación Orientada a Objetos, donde cada nodo representa una TAREA
     y contiene una referencia (puntero) al siguiente nodo de la lista.

     Estructura de un nodo:
         [ Datos de la Tarea | *siguiente ] --> [ Datos de la Tarea | *siguiente ] --> ... --> None

 Este módulo NO depende de ningún framework: puede usarse de forma independiente
 (por consola) o ser consumido por el backend Flask (app.py) que expone una API
 REST para el Frontend web.
=====================================================================================
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any, Iterator


# --------------------------------------------------------------------------------
# EXCEPCIONES PERSONALIZADAS
# --------------------------------------------------------------------------------
class ListaVaciaError(Exception):
    """Se lanza cuando se intenta operar sobre una lista enlazada vacía."""
    pass


class TareaNoEncontradaError(Exception):
    """Se lanza cuando no se encuentra una tarea con el id solicitado."""
    pass


class PrioridadInvalidaError(Exception):
    """Se lanza cuando la prioridad ingresada no es una de las permitidas."""
    pass


PRIORIDADES_VALIDAS = ("alta", "media", "baja")


# --------------------------------------------------------------------------------
# NODO: unidad básica de la lista enlazada
# --------------------------------------------------------------------------------
class Nodo:
    """
    Representa un nodo de la lista enlazada simple.

    Cada nodo almacena:
        - Los datos de una tarea (id, título, descripción, prioridad, estado)
        - Un puntero 'siguiente' que referencia al próximo nodo (o None si es el último)
    """

    __slots__ = (
        "id", "titulo", "descripcion", "prioridad",
        "completada", "fecha_creacion", "fecha_completada", "siguiente"
    )

    def __init__(self, id_: int, titulo: str, descripcion: str = "",
                 prioridad: str = "media") -> None:
        self.id: int = id_
        self.titulo: str = titulo
        self.descripcion: str = descripcion
        self.prioridad: str = prioridad
        self.completada: bool = False
        self.fecha_creacion: datetime = datetime.now()
        self.fecha_completada: Optional[datetime] = None
        self.siguiente: Optional["Nodo"] = None  # <-- puntero al siguiente nodo

    def a_diccionario(self) -> Dict[str, Any]:
        """Serializa el nodo a un diccionario (útil para exponerlo como JSON en la API)."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "prioridad": self.prioridad,
            "completada": self.completada,
            "fecha_creacion": self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_completada": (
                self.fecha_completada.strftime("%Y-%m-%d %H:%M:%S")
                if self.fecha_completada else None
            ),
        }

    def __repr__(self) -> str:
        estado = "✔" if self.completada else "✗"
        return f"Nodo(id={self.id}, titulo='{self.titulo}', completada={estado})"


# --------------------------------------------------------------------------------
# LISTA ENLAZADA SIMPLE: estructura principal (Clase contenedora)
# --------------------------------------------------------------------------------
class ListaTareas:
    """
    Lista Enlazada Simple que administra nodos de tipo Tarea.

    Mantiene referencias a:
        - self.cabeza  -> primer nodo de la lista (head)
        - self.cola    -> último nodo de la lista (tail), permite inserción O(1) al final
        - self.tamano  -> cantidad de nodos actuales

    Complejidad de las operaciones principales:
        agregar_tarea (al final)      -> O(1)   (gracias al puntero 'cola')
        agregar_al_inicio             -> O(1)
        buscar_tarea / actualizar     -> O(n)
        eliminar_tarea                -> O(n)
        recorrer / listar             -> O(n)
    """

    def __init__(self) -> None:
        self.cabeza: Optional[Nodo] = None
        self.cola: Optional[Nodo] = None
        self.tamano: int = 0
        self._contador_id: int = 1  # autoincremental, simula una PK

    # ------------------------------------------------------------------
    # Utilidades básicas
    # ------------------------------------------------------------------
    def esta_vacia(self) -> bool:
        return self.cabeza is None

    def __len__(self) -> int:
        return self.tamano

    def __iter__(self) -> Iterator[Nodo]:
        """Permite recorrer la lista con un 'for nodo in lista_tareas:'."""
        actual = self.cabeza
        while actual is not None:
            yield actual
            actual = actual.siguiente

    def __repr__(self) -> str:
        return f"ListaTareas(tamano={self.tamano})"

    # ------------------------------------------------------------------
    # INSERCIÓN
    # ------------------------------------------------------------------
    def agregar_tarea(self, titulo: str, descripcion: str = "",
                       prioridad: str = "media") -> Nodo:
        """
        Inserta un nuevo nodo AL FINAL de la lista enlazada. O(1)

        1. Se crea el nodo con los datos de la tarea.
        2. Si la lista está vacía, el nuevo nodo es cabeza y cola a la vez.
        3. Si no, el nodo 'cola' actual apunta (siguiente) al nuevo nodo,
           y el nuevo nodo pasa a ser la nueva cola.
        """
        titulo = (titulo or "").strip()
        if not titulo:
            raise ValueError("El título de la tarea no puede estar vacío.")
        prioridad = (prioridad or "media").lower().strip()
        if prioridad not in PRIORIDADES_VALIDAS:
            raise PrioridadInvalidaError(
                f"Prioridad '{prioridad}' inválida. Use: {PRIORIDADES_VALIDAS}"
            )

        nuevo_nodo = Nodo(self._contador_id, titulo, descripcion, prioridad)
        self._contador_id += 1

        if self.esta_vacia():
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            self.cola.siguiente = nuevo_nodo   # el último apunta al nuevo
            self.cola = nuevo_nodo             # el nuevo es ahora el último

        self.tamano += 1
        return nuevo_nodo

    def agregar_al_inicio(self, titulo: str, descripcion: str = "",
                           prioridad: str = "media") -> Nodo:
        """Inserta un nuevo nodo AL INICIO de la lista. O(1)"""
        titulo = (titulo or "").strip()
        if not titulo:
            raise ValueError("El título de la tarea no puede estar vacío.")
        prioridad = (prioridad or "media").lower().strip()
        if prioridad not in PRIORIDADES_VALIDAS:
            raise PrioridadInvalidaError(f"Prioridad '{prioridad}' inválida.")

        nuevo_nodo = Nodo(self._contador_id, titulo, descripcion, prioridad)
        self._contador_id += 1

        nuevo_nodo.siguiente = self.cabeza
        self.cabeza = nuevo_nodo
        if self.cola is None:  # lista estaba vacía
            self.cola = nuevo_nodo

        self.tamano += 1
        return nuevo_nodo

    # ------------------------------------------------------------------
    # BÚSQUEDA
    # ------------------------------------------------------------------
    def buscar_tarea(self, id_: int) -> Nodo:
        """Recorre la lista nodo por nodo hasta encontrar el id buscado. O(n)"""
        actual = self.cabeza
        while actual is not None:
            if actual.id == id_:
                return actual
            actual = actual.siguiente
        raise TareaNoEncontradaError(f"No existe una tarea con id={id_}.")

    def existe(self, id_: int) -> bool:
        try:
            self.buscar_tarea(id_)
            return True
        except TareaNoEncontradaError:
            return False

    # ------------------------------------------------------------------
    # ELIMINACIÓN
    # ------------------------------------------------------------------
    def eliminar_tarea(self, id_: int) -> bool:
        """
        Elimina el nodo cuyo id coincide, re-enlazando el nodo anterior
        directamente con el nodo siguiente al eliminado. O(n)
        """
        if self.esta_vacia():
            raise ListaVaciaError("No se puede eliminar: la lista está vacía.")

        anterior: Optional[Nodo] = None
        actual = self.cabeza

        while actual is not None:
            if actual.id == id_:
                if anterior is None:
                    # Se elimina la cabeza
                    self.cabeza = actual.siguiente
                else:
                    # Se "saltan" el nodo eliminado enlazando anterior -> siguiente
                    anterior.siguiente = actual.siguiente

                if actual is self.cola:
                    self.cola = anterior  # actualizar cola si se eliminó el último

                self.tamano -= 1
                return True

            anterior = actual
            actual = actual.siguiente

        raise TareaNoEncontradaError(f"No existe una tarea con id={id_}.")

    def vaciar(self) -> None:
        """Elimina todos los nodos de la lista. O(1) (se descartan las referencias)."""
        self.cabeza = None
        self.cola = None
        self.tamano = 0

    # ------------------------------------------------------------------
    # ACTUALIZACIÓN
    # ------------------------------------------------------------------
    def actualizar_tarea(self, id_: int, titulo: Optional[str] = None,
                          descripcion: Optional[str] = None,
                          prioridad: Optional[str] = None) -> Nodo:
        """Modifica los datos del nodo encontrado, sin alterar los punteros."""
        nodo = self.buscar_tarea(id_)
        if titulo is not None:
            titulo = titulo.strip()
            if not titulo:
                raise ValueError("El título no puede quedar vacío.")
            nodo.titulo = titulo
        if descripcion is not None:
            nodo.descripcion = descripcion
        if prioridad is not None:
            prioridad = prioridad.lower().strip()
            if prioridad not in PRIORIDADES_VALIDAS:
                raise PrioridadInvalidaError(f"Prioridad '{prioridad}' inválida.")
            nodo.prioridad = prioridad
        return nodo

    def marcar_completada(self, id_: int, completada: bool = True) -> Nodo:
        """Cambia el estado de completado de una tarea (toggle o explícito)."""
        nodo = self.buscar_tarea(id_)
        nodo.completada = completada
        nodo.fecha_completada = datetime.now() if completada else None
        return nodo

    def alternar_completada(self, id_: int) -> Nodo:
        nodo = self.buscar_tarea(id_)
        return self.marcar_completada(id_, not nodo.completada)

    # ------------------------------------------------------------------
    # REORDENAMIENTO (operación extra propia de listas enlazadas)
    # ------------------------------------------------------------------
    def mover_al_inicio(self, id_: int) -> None:
        """Desenlaza un nodo existente y lo vuelve a enlazar como cabeza. O(n)"""
        if self.cabeza is None or self.cabeza.id == id_:
            return
        anterior = self.cabeza
        actual = self.cabeza.siguiente
        while actual is not None:
            if actual.id == id_:
                anterior.siguiente = actual.siguiente
                if actual is self.cola:
                    self.cola = anterior
                actual.siguiente = self.cabeza
                self.cabeza = actual
                return
            anterior = actual
            actual = actual.siguiente
        raise TareaNoEncontradaError(f"No existe una tarea con id={id_}.")

    def invertir(self) -> None:
        """
        Invierte la lista enlazada in-place, redirigiendo los punteros
        'siguiente' de cada nodo en sentido contrario. Clásico ejercicio
        de listas simples. O(n) tiempo, O(1) espacio extra.
        """
        anterior: Optional[Nodo] = None
        actual = self.cabeza
        self.cola = self.cabeza
        while actual is not None:
            siguiente_temporal = actual.siguiente
            actual.siguiente = anterior
            anterior = actual
            actual = siguiente_temporal
        self.cabeza = anterior

    # ------------------------------------------------------------------
    # CONSULTAS / REPORTES
    # ------------------------------------------------------------------
    def obtener_todas(self) -> List[Dict[str, Any]]:
        return [nodo.a_diccionario() for nodo in self]

    def obtener_pendientes(self) -> List[Dict[str, Any]]:
        return [n.a_diccionario() for n in self if not n.completada]

    def obtener_completadas(self) -> List[Dict[str, Any]]:
        return [n.a_diccionario() for n in self if n.completada]

    def filtrar_por_prioridad(self, prioridad: str) -> List[Dict[str, Any]]:
        prioridad = prioridad.lower().strip()
        return [n.a_diccionario() for n in self if n.prioridad == prioridad]

    def estadisticas(self) -> Dict[str, Any]:
        total = self.tamano
        completadas = sum(1 for n in self if n.completada)
        pendientes = total - completadas
        por_prioridad = {p: 0 for p in PRIORIDADES_VALIDAS}
        for n in self:
            por_prioridad[n.prioridad] += 1
        return {
            "total": total,
            "completadas": completadas,
            "pendientes": pendientes,
            "porcentaje_completado": round((completadas / total * 100), 1) if total else 0.0,
            "por_prioridad": por_prioridad,
        }

    def imprimir_lista(self) -> None:
        """Recorre e imprime la lista por consola (traversal clásico de la teoría)."""
        if self.esta_vacia():
            print("La lista de tareas está vacía.")
            return
        actual = self.cabeza
        print("=" * 60)
        while actual is not None:
            estado = "Completada" if actual.completada else "Pendiente"
            print(f"[{actual.id}] {actual.titulo}  |  Prioridad: {actual.prioridad}  |  {estado}")
            print(f"     Descripción: {actual.descripcion or '(sin descripción)'}")
            print(f"     Siguiente -> {actual.siguiente.id if actual.siguiente else 'None'}")
            print("-" * 60)
            actual = actual.siguiente


# --------------------------------------------------------------------------------
# DEMO POR CONSOLA (ejecutar: python lista_enlazada.py)
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    lista = ListaTareas()

    lista.agregar_tarea("Estudiar listas enlazadas", "Repasar teoría de nodos y punteros", "alta")
    lista.agregar_tarea("Hacer el taller de Python", "Implementar la clase ListaTareas", "alta")
    lista.agregar_tarea("Construir el Frontend", "Conectar HTML/JS con la API Flask", "media")
    lista.agregar_tarea("Repasar para el parcial", "", "baja")

    print("\n>>> Lista completa de tareas:")
    lista.imprimir_lista()

    print("\n>>> Marcando como completada la tarea con id=1")
    lista.marcar_completada(1)

    print("\n>>> Eliminando la tarea con id=3")
    lista.eliminar_tarea(3)

    print("\n>>> Lista luego de las modificaciones:")
    lista.imprimir_lista()

    print("\n>>> Estadísticas:")
    print(lista.estadisticas())
