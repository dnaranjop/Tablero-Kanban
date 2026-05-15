"""
Aggregate root Tablero.

Referencia:
  - DOMAIN.md §2 (aggregate root).
  - DOMAIN.md §3 (INV-01 a INV-05).
  - DOMAIN.md §5 (operaciones autorizadas).
  - DOMAIN.md §6 (nomenclatura).
  - GLOSSARY.md (Tablero, LimiteWip).
  - TECH_CONSTRAINTS.md §2 (LIMITE_WIP no configurable).

El Tablero es la única puerta de entrada para crear y mover tareas.
La constante LIMITE_WIP está fija a nivel de módulo y NO se expone
como parámetro de instancia ni de método (TECH_CONSTRAINTS.md §2).
"""

from __future__ import annotations 

from typing import Final
from uuid import UUID

from src.dominio.errores import (
    ErrorLimiteWipExcedido,
    ErrorTareaNoEncontrada,
    ErrorTransicionInvalida,
)
from src.dominio.estado_tarea import EstadoTarea
from src.dominio.tarea import Tarea


# Constante de dominio (DOMAIN.md §1, GLOSSARY.md, TECH_CONSTRAINTS.md §2).
LIMITE_WIP: Final[int] = 3


# Mapa de transiciones autorizadas (INV-03 — DOMAIN.md §3).
# Para cada estado origen, conjunto de estados destino permitidos.
_TRANSICIONES_VALIDAS: Final[dict[EstadoTarea, frozenset[EstadoTarea]]] = {
    EstadoTarea.TODO: frozenset({EstadoTarea.DOING}),
    EstadoTarea.DOING: frozenset({EstadoTarea.DONE}),
    EstadoTarea.DONE: frozenset(),  # estado terminal
}


class Tablero:
    """
    Aggregate root del Bounded Context.

    Mantiene la colección de Tareas y protege las invariantes:
      - INV-01: a lo sumo LIMITE_WIP (3) tareas en DOING.
      - INV-02: violar INV-01 lanza ErrorLimiteWipExcedido sin mutar estado.
      - INV-03: transiciones TODO -> DOING y DOING -> DONE.
      - INV-04: validada al crear Tarea (en la entidad).
      - INV-05: una operación que lanza error no persiste cambios parciales.
    """

    def __init__(self, tareas: list[Tarea] | None = None) -> None:
        """
        Inicializa el Tablero, opcionalmente con un conjunto preexistente
        de tareas (caso típico: carga desde el repositorio, PASO 11).

        Si la carga inicial ya viola INV-01, lanzamos error inmediatamente:
        un Tablero recién cargado no puede arrancar en estado inválido.
        """
        self._tareas: dict[UUID, Tarea] = {}
        for tarea in tareas or []:
            self._tareas[tarea.id_tarea] = tarea
        if self._contar_en_estado(EstadoTarea.DOING) > LIMITE_WIP:
            raise ErrorLimiteWipExcedido(
                "El estado inicial del tablero viola INV-01 (DOING > 3)."
            )

    # ---------- Operaciones autorizadas (DOMAIN.md §5) ----------

    def crear_tarea(self, titulo: str) -> Tarea:
        """
        Crea una nueva Tarea en estado TODO.

        Referencias:
          - FEATURE_SPEC_001 flujo principal, AC-01.
          - INV-04 (validada en el constructor de Tarea).
          - INV-05: si Tarea(...) lanza ErrorTituloTareaInvalido, el
            tablero no se modifica porque la asignación al diccionario
            ocurre solo si la construcción tuvo éxito.
        """
        tarea = Tarea(titulo=titulo)  # puede lanzar ErrorTituloTareaInvalido
        self._tareas[tarea.id_tarea] = tarea
        return tarea

    def mover_tarea(self, id_tarea: UUID, estado_destino: EstadoTarea) -> Tarea:
        """
        Mueve una Tarea existente a un nuevo estado.

        Orden de verificaciones (importante para INV-05):
          1. La tarea existe                     -> si no, ErrorTareaNoEncontrada.
          2. La transición es válida (INV-03)    -> si no, ErrorTransicionInvalida.
          3. Si destino es DOING, INV-01         -> si no, ErrorLimiteWipExcedido.
          4. Recién entonces se muta el estado.

        Cualquier excepción en los pasos 1-3 NO modifica el tablero (INV-02, INV-05).

        Referencias: FEATURE_SPEC_002 AC-01 a AC-06; INV-01, INV-02, INV-03.
        """
        if not isinstance(estado_destino, EstadoTarea):
            raise TypeError("estado_destino debe ser una instancia de EstadoTarea.")

        # (1) existencia
        tarea = self._tareas.get(id_tarea)
        if tarea is None:
            raise ErrorTareaNoEncontrada(
                f"No existe ninguna tarea con id_tarea={id_tarea}."
            )

        # (2) transición válida (INV-03)
        destinos_permitidos = _TRANSICIONES_VALIDAS[tarea.estado]
        if estado_destino not in destinos_permitidos:
            raise ErrorTransicionInvalida(
                f"La transicion {tarea.estado.name} -> {estado_destino.name} no esta permitida."
            )

        # (3) límite WIP (INV-01, INV-02)
        if estado_destino is EstadoTarea.DOING:
            if self._contar_en_estado(EstadoTarea.DOING) >= LIMITE_WIP:
                raise ErrorLimiteWipExcedido(
                    f"La columna DOING ya contiene {LIMITE_WIP} tareas (limite WIP)."
                )

        # (4) mutación: única vez que se modifica el estado interno
        tarea.cambiar_estado(estado_destino)
        return tarea

    def obtener_tareas_por_estado(self) -> dict[EstadoTarea, list[Tarea]]:
        """
        Devuelve las tareas agrupadas por estado, sin mutar el tablero.

        Garantías:
          - Siempre incluye las tres claves TODO, DOING, DONE
            (FEATURE_SPEC_003 AC-01), aunque alguna esté vacía.
          - Devuelve listas nuevas; modificar la salida no afecta al tablero
            (FEATURE_SPEC_003 AC-02).
        """
        agrupado: dict[EstadoTarea, list[Tarea]] = {
            EstadoTarea.TODO: [],
            EstadoTarea.DOING: [],
            EstadoTarea.DONE: [],
        }
        for tarea in self._tareas.values():
            agrupado[tarea.estado].append(tarea)
        return agrupado

    # ---------- Auxiliares de solo lectura ----------

    def listar_tareas(self) -> list[Tarea]:
        """
        Devuelve una copia plana de las tareas del tablero.

        Útil para la capa de aplicación (casos de uso) y para el adaptador
        de persistencia (PASO 11), sin exponer el diccionario interno.
        """
        return list(self._tareas.values())

    def _contar_en_estado(self, estado: EstadoTarea) -> int:
        """Cuenta cuántas tareas están en un estado dado."""
        return sum(1 for tarea in self._tareas.values() if tarea.estado is estado)