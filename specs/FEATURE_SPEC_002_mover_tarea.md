# FEATURE_SPEC_002_mover_tarea.md -- Mover tarea entre columnas

## Bloque 1. Objetivo y precondiciones
Actor: usuario individual.
Objetivo: mover una tarea existente respetando transiciones secuenciales y límite WIP.
Precondiciones:
- La tarea existe en el tablero.
- El estado destino pertenece al conjunto DOING o DONE.
- El movimiento solicitado debe respetar DOMAIN.md.

## Bloque 2. Entrada
Entrada esperada:
```json
{
  "id_tarea": "uuid",
  "estado_destino": "DOING | DONE"
}
```

## Bloque 3. Flujo principal
1. Cargar el tablero desde el repositorio.
2. Buscar la tarea por id_tarea.
3. Verificar que la transición es válida.
4. Si estado_destino es DOING, verificar INV-01.
5. Cambiar el estado de la tarea.
6. Guardar el tablero actualizado.
7. Devolver el tablero o la tarea actualizada.

## Bloque 4. Errores de dominio
- ErrorTareaNoEncontrada.
- ErrorTransicionInvalida.
- ErrorLimiteWipExcedido.

## Bloque 5. Criterios de aceptación
- AC-01: mover una tarea de TODO a DOING funciona si DOING tiene menos de 3 tareas.
- AC-02: mover una cuarta tarea a DOING lanza ErrorLimiteWipExcedido.
- AC-03: mover de TODO a DONE lanza ErrorTransicionInvalida.
- AC-04: mover de DOING a DONE funciona.
- AC-05: después de un movimiento válido, el tablero se guarda.
- AC-06: si ocurre un error de dominio, el tablero no se guarda con cambios parciales.
