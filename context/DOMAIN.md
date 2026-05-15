# DOMAIN.md -- Tablero Kanban Personal con Límite WIP

## 1. Lenguaje ubicuo
| Término | Definición |
|---|---|
| Tarea | Unidad de trabajo con id_tarea, titulo y estado. |
| Tablero | Aggregate root que contiene las tareas y protege las invariantes. |
| EstadoTarea | Enumerado con valores TODO, DOING y DONE. |
| LimiteWip | Constante de dominio con valor 3. |
| Transición | Cambio de estado de una tarea. |

## 2. Aggregate root
Tablero es el aggregate root. Toda creación o movimiento de tarea debe pasar por Tablero. Ningún adaptador de infraestructura puede modificar directamente una tarea evitando al aggregate root.

## 3. Invariantes
- INV-01: DOING no puede contener más de 3 tareas simultáneas.
- INV-02: exceder el límite WIP lanza ErrorLimiteWipExcedido y no modifica el estado del tablero.
- INV-03: las transiciones válidas son TODO -> DOING y DOING -> DONE.
- INV-04: una tarea debe tener título obligatorio, no vacío y sin solo espacios.
- INV-05: una operación inválida no debe persistir cambios parciales.

## 4. Errores de dominio
- ErrorTareaNoEncontrada: la tarea solicitada no existe en el tablero.
- ErrorTransicionInvalida: el cambio de estado no respeta el flujo permitido.
- ErrorLimiteWipExcedido: la columna DOING ya contiene tres tareas.
- ErrorTituloTareaInvalido: el titulo está vacío o contiene solo espacios.

## 5. Operaciones de dominio autorizadas
- Tablero.crear_tarea(titulo) crea una tarea en estado TODO después de validar INV-04.
- Tablero.mover_tarea(id_tarea, estado_destino) cambia el estado solo si se cumplen INV-01, INV-02 e INV-03.
- Tablero.obtener_tareas_por_estado() devuelve las tareas agrupadas sin modificar el estado interno.

## 6. Reglas de nomenclatura de código
- Identificadores en español sin tildes: Tarea, Tablero, EstadoTarea, id_tarea.
- Valores del enumerado en mayúsculas: TODO, DOING, DONE.
- Los errores de dominio son clases con nombres explícitos.
- No se implementan eventos de dominio en este ejercicio; agregarlos ampliaría el alcance.
