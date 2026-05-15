# FEATURE_SPEC_001_crear_tarea.md -- Crear tarea

## Bloque 1. Objetivo y precondiciones
Actor: usuario individual.
Objetivo: crear una tarea nueva en estado TODO con título válido.
Precondiciones:
- El tablero existe o puede inicializarse vacío.
- El título proviene de una entrada de usuario o de una petición HTTP.

## Bloque 2. Entrada
Entrada esperada:
```json
{
  "titulo": "texto no vacío"
}
```

## Bloque 3. Flujo principal
1. Cargar el tablero desde el repositorio.
2. Validar que titulo no esté vacío ni compuesto solo por espacios.
3. Crear la tarea con id_tarea generado por la aplicación y estado TODO.
4. Agregar la tarea al tablero mediante Tablero.
5. Guardar el tablero actualizado.
6. Devolver la tarea creada.

## Bloque 4. Errores de dominio
- ErrorTituloTareaInvalido.

## Bloque 5. Criterios de aceptación
- AC-01: crear una tarea con título válido genera id_tarea, conserva titulo y asigna estado TODO.
- AC-02: crear una tarea con título vacío lanza ErrorTituloTareaInvalido.
- AC-03: crear una tarea con solo espacios lanza ErrorTituloTareaInvalido.
- AC-04: después de crear una tarea válida, el tablero se guarda.
- AC-05: si ocurre un error de dominio, el tablero no se guarda con cambios parciales.
