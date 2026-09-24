# Taller de Listas Simples aplicado a un caso de estudio
**Materia:** Estructuras de Datos
**Caso de estudio:** Gestor de Tareas Pendientes (To-Do List)
**Tecnologías:** Python (POO) + Flask (Backend/API) + HTML/CSS/JS (Frontend)

---

## 1. Descripción del problema

Se pide crear un script en Python que permita trabajar una **lista de tareas
pendientes**, donde **cada nodo representa una tarea** y contiene una
**referencia (puntero) al siguiente nodo** que contiene la siguiente tarea de
la lista. El taller debe incluir **Frontend**.

Esto es exactamente la definición de una **Lista Enlazada Simple**:

```
[Tarea A | *siguiente] --> [Tarea B | *siguiente] --> [Tarea C | NULL]
   cabeza (head)                                          cola (tail)
```

## 2. Arquitectura del proyecto

```
taller_listas/
├── lista_enlazada.py      # Núcleo del taller: Nodo + ListaTareas (POO puro, sin dependencias)
├── app.py                 # Backend Flask: expone la lista enlazada como API REST
├── templates/
│   └── index.html         # Frontend: estructura de la página
├── static/
│   ├── style.css           # Frontend: estilos
│   └── script.js            # Frontend: consumo de la API (fetch) y renderizado dinámico
├── requirements.txt
└── README.md
```

**¿Por qué esta arquitectura?**
- `lista_enlazada.py` es **100% autocontenido**: puedes ejecutarlo por consola
  (`python lista_enlazada.py`) sin necesidad de Flask, ideal para demostrar la
  estructura de datos en la sustentación.
- `app.py` NO reimplementa la lógica: solo la expone vía HTTP, cumpliendo con
  el requisito de tener un Frontend funcional que consuma la estructura de datos.

## 3. Clases y conceptos de POO aplicados

| Clase | Rol |
|---|---|
| `Nodo` | Representa un elemento de la lista: datos de la tarea + puntero `siguiente` |
| `ListaTareas` | Estructura contenedora: mantiene `cabeza`, `cola` y `tamano`, y expone los métodos de la lista enlazada |
| `TareaNoEncontradaError`, `ListaVaciaError`, `PrioridadInvalidaError` | Excepciones personalizadas para manejo robusto de errores |

Conceptos de POO usados: **encapsulamiento** (atributos gestionados por
métodos), **`__slots__`** para optimizar memoria del nodo, **manejo de
excepciones propias**, **iteradores** (`__iter__`, `__len__`) para poder
recorrer la lista con `for nodo in lista_tareas:`.

## 4. Operaciones implementadas sobre la lista enlazada

| Método | Operación | Complejidad |
|---|---|---|
| `agregar_tarea()` | Inserta un nodo al final | O(1) |
| `agregar_al_inicio()` | Inserta un nodo al inicio | O(1) |
| `buscar_tarea(id)` | Recorre la lista buscando un id | O(n) |
| `eliminar_tarea(id)` | Desenlaza un nodo, reconectando el anterior con el siguiente | O(n) |
| `actualizar_tarea(id, ...)` | Modifica los datos de un nodo sin tocar punteros | O(n) |
| `marcar_completada(id)` / `alternar_completada(id)` | Cambia el estado de una tarea | O(n) |
| `mover_al_inicio(id)` | Reordena la lista moviendo un nodo existente a la cabeza | O(n) |
| `invertir()` | Invierte el sentido de todos los punteros `siguiente` | O(n) |
| `vaciar()` | Elimina todos los nodos | O(1) |
| `estadisticas()` | Recorre la lista y genera un resumen (total, pendientes, completadas, %) | O(n) |

## 5. API REST expuesta por el Backend (`app.py`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/tareas` | Lista todas las tareas (o filtra por `?estado=` / `?prioridad=`) |
| GET | `/api/tareas/estadisticas` | Devuelve el resumen estadístico |
| POST | `/api/tareas` | Crea una tarea (nuevo nodo) |
| PUT | `/api/tareas/<id>` | Edita una tarea existente |
| PATCH | `/api/tareas/<id>/completar` | Alterna el estado completada/pendiente |
| PATCH | `/api/tareas/<id>/mover-inicio` | Mueve el nodo al inicio de la lista |
| PATCH | `/api/tareas/invertir` | Invierte la lista enlazada completa |
| DELETE | `/api/tareas/<id>` | Elimina un nodo específico |
| DELETE | `/api/tareas` | Vacía toda la lista |

## 6. Frontend

Interfaz web que consume la API mediante `fetch()` en JavaScript puro (sin
frameworks), y **visualiza la lista como una cadena de nodos conectados por
flechas (→ ... → NULL)**, para reforzar visualmente el concepto de lista
enlazada. Incluye:
- Formulario para agregar tareas (al inicio o al final).
- Tarjetas de nodo con prioridad, estado y descripción.
- Filtros (todas / pendientes / completadas).
- Botones para invertir la lista y vaciarla.
- Panel de estadísticas con barra de progreso.

## 7. Cómo ejecutar el proyecto

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar el servidor
python app.py

# 3. Abrir en el navegador
http://127.0.0.1:5000
```

### Ejecutar solo la estructura de datos por consola (sin Frontend)
```bash
python lista_enlazada.py
```

## 8. Posibles preguntas de sustentación (y respuesta rápida)

- **¿Por qué es O(1) agregar al final si es una lista simple?**
  Porque se mantiene un puntero adicional `cola` que siempre referencia al
  último nodo, evitando recorrer toda la lista.
- **¿Qué pasa si elimino la cabeza o la cola?**
  `eliminar_tarea()` maneja ambos casos: si es la cabeza, se actualiza
  `self.cabeza`; si es la cola, se actualiza `self.cola` usando el nodo
  `anterior` guardado durante el recorrido.
- **¿Cómo se invierte una lista enlazada simple?**
  Recorriendo la lista una sola vez y, en cada nodo, redirigiendo su puntero
  `siguiente` hacia el nodo anterior (método `invertir()`), en O(n) tiempo y
  O(1) espacio extra.
