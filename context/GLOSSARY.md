# GLOSSARY.md -- Tablero Kanban Personal

## Tarea
Unidad de trabajo con id_tarea, titulo obligatorio y estado. No confundir con Item, Pendiente, Ticket o Card.

## Tablero
Aggregate root que contiene todas las tareas y verifica las invariantes antes de aceptar cambios. No confundir con Board, Panel o Dashboard.

## EstadoTarea
Enumerado con valores TODO, DOING y DONE.

## LimiteWip
Constante del dominio igual a 3. Representa el máximo de tareas permitidas simultáneamente en DOING.

## Work-In-Progress (WIP)
Trabajo iniciado pero no terminado. En este proyecto corresponde a las tareas en estado DOING.

## Invariante
Regla de negocio que debe cumplirse siempre. No es una recomendación de interfaz.

## Puerto
Interfaz definida por la capa de aplicación para comunicarse con el exterior sin depender de una tecnología concreta.

## Adaptador
Implementación concreta de un puerto o mecanismo de entrada/salida, por ejemplo Flask o persistencia JSON.
