"""
EstadoTarea: enumerado de dominio.

Referencia: DOMAIN.md §1 (lenguaje ubicuo) y §6 (reglas de nomenclatura).
Solo depende de la biblioteca estándar (módulo `enum`).
No importa nada de aplicación ni de infraestructura.
"""

from enum import Enum


class EstadoTarea(Enum):
    """Estados válidos de una Tarea en el tablero Kanban."""

    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"