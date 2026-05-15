"""
Errores de dominio del Tablero Kanban Personal.

Referencia: DOMAIN.md §4 (Errores de dominio) y §6 (nombres explícitos).
Solo depende de la biblioteca estándar.
No importa nada de aplicacion ni de infraestructura.

Estos errores son los únicos definidos en DOMAIN.md §4. Cualquier error
adicional ampliaría el alcance y debe rechazarse en revisión.
"""


class ErrorDominio(Exception):
    """
    Clase base de los errores de dominio.

    Permite a la capa de infraestructura (por ejemplo, el adaptador HTTP)
    capturar de forma uniforme cualquier error originado en el dominio
    sin acoplarse a cada subclase individual. No agrega comportamiento
    propio; solo sirve como raíz semántica.
    """


class ErrorTareaNoEncontrada(ErrorDominio):
    """DOMAIN.md §4: la tarea solicitada no existe en el tablero."""


class ErrorTransicionInvalida(ErrorDominio):
    """DOMAIN.md §4: el cambio de estado no respeta el flujo permitido."""


class ErrorLimiteWipExcedido(ErrorDominio):
    """DOMAIN.md §4: la columna DOING ya contiene tres tareas (INV-01)."""


class ErrorTituloTareaInvalido(ErrorDominio):
    """DOMAIN.md §4: el titulo está vacío o contiene solo espacios (INV-04)."""