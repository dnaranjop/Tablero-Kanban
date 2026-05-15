"""
Caso de uso: ObtenerTablero.

Referencia:
  - FEATURE_SPEC_003 (flujo principal y AC-01 a AC-03).
  - DOMAIN.md §5: Tablero.obtener_tareas_por_estado() es la única vía
    autorizada para leer la agrupación; no modifica estado.
  - ARCHITECTURE.md §3 (la aplicación no importa de infraestructura).

Contrato del caso de uso:
  - Es una CONSULTA pura: NO invoca repositorio.guardar() (FEATURE_SPEC_003 AC-02).
  - Devuelve una representación serializable del tablero, agrupada por estado,
    suficiente para que la UI del PASO 13 pinte tres columnas.

Forma del DTO de salida (FEATURE_SPEC_003 AC-01, AC-03):
    {
        "TODO":  [{"id_tarea": "<uuid>", "titulo": "...", "estado": "TODO"},  ...],
        "DOING": [{"id_tarea": "<uuid>", "titulo": "...", "estado": "DOING"}, ...],
        "DONE":  [{"id_tarea": "<uuid>", "titulo": "...", "estado": "DONE"},  ...]
    }

Las tres claves SIEMPRE están presentes, aunque alguna columna esté vacía
(garantiza AC-01 incluso con tablero recién creado).
"""

from __future__ import annotations

from typing import TypedDict

from src.aplicacion.repositorio_tablero import RepositorioTablero
from src.dominio.estado_tarea import EstadoTarea
from src.dominio.tarea import Tarea


class TareaDTO(TypedDict):
    """DTO plano de una tarea para la capa de presentación."""

    id_tarea: str
    titulo: str
    estado: str


class TableroDTO(TypedDict):
    """DTO del tablero agrupado por estado (FEATURE_SPEC_003 AC-01)."""

    TODO: list[TareaDTO]
    DOING: list[TareaDTO]
    DONE: list[TareaDTO]


class ObtenerTablero:
    """
    Application Service: consulta del tablero.

    Recibe por inyección de dependencia una implementación del puerto
    RepositorioTablero. El caso de uso NO instancia repositorios concretos
    y NO invoca repositorio.guardar() en ningún flujo.
    """

    def __init__(self, repositorio: RepositorioTablero) -> None:
        self._repositorio = repositorio

    def ejecutar(self) -> TableroDTO:
        """
        Flujo principal de FEATURE_SPEC_003:
          1. Cargar el tablero desde el repositorio.
          2. Obtener las tareas agrupadas por TODO, DOING y DONE.
          3. Devolver una representación serializable.
          4. NO modificar ni guardar el tablero (AC-02).
        """
        tablero = self._repositorio.cargar()
        agrupado = tablero.obtener_tareas_por_estado()

        return TableroDTO(
            TODO=[self._a_dto(t) for t in agrupado[EstadoTarea.TODO]],
            DOING=[self._a_dto(t) for t in agrupado[EstadoTarea.DOING]],
            DONE=[self._a_dto(t) for t in agrupado[EstadoTarea.DONE]],
        )

    @staticmethod
    def _a_dto(tarea: Tarea) -> TareaDTO:
        """Convierte una Tarea de dominio en un DTO plano serializable."""
        return TareaDTO(
            id_tarea=str(tarea.id_tarea),
            titulo=tarea.titulo,
            estado=tarea.estado.name,
        )