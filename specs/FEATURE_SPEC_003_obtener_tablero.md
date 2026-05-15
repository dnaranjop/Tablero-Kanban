# FEATURE_SPEC_003_obtener_tablero.md -- Obtener tablero

## Bloque 1. Objetivo y precondiciones
Actor: usuario individual.
Objetivo: consultar las tareas agrupadas por estado para mostrarlas en el tablero.
Precondiciones:
- El repositorio puede cargar un tablero existente o inicializar uno vacío.

## Bloque 2. Entrada
No requiere cuerpo de entrada.

## Bloque 3. Flujo principal
1. Cargar el tablero desde el repositorio.
2. Obtener las tareas agrupadas por TODO, DOING y DONE.
3. Devolver una representación serializable del tablero.
4. No modificar ni guardar el tablero durante la consulta.

## Bloque 4. Errores esperados
- No se esperan errores de dominio para una consulta válida.
- Si el archivo JSON no existe, infraestructura puede inicializar un tablero vacío.

## Bloque 5. Criterios de aceptación
- AC-01: obtener el tablero devuelve siempre las claves TODO, DOING y DONE.
- AC-02: una consulta no modifica el estado del dominio.
- AC-03: la interfaz puede pintar las tres columnas usando la respuesta.
