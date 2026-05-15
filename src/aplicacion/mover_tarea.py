"""
Caso de uso: MoverTarea.

Referencia:
  - FEATURE_SPEC_002 (flujo principal y AC-01 a AC-06).
  - DOMAIN.md §2 (Tablero es el aggregate root; toda mutación pasa por él).
  - DOMAIN.md §5 (Tablero.mover_tarea valida INV-01, INV-02, INV-03).
  - ARCHITECTURE.md §3 (la aplicación no importa de infraestructura).

Contrato del caso de uso:
  - Recibe el id de la tarea y el estado destino (como instancia de EstadoTarea
    o como string canónico 'TODO' | 'DOING' | 'DONE').
  - Carga el Tablero, le pide mover la tarea, persiste y devuelve la tarea actualizada.
  - Toda la lógica de invariantes (WIP, transición, existencia) la ejecuta el dominio.
  - Si el dominio lanza un error, se propaga y NO se invoca guardar (INV-05).

Este caso de uso NO conoce JSON, Flask ni archivos. Solo conoce el puerto
RepositorioTablero (PASO 7) y el dominio.
"""

from __future__ import annotations

from uuid import UUID

from src.aplicacion.repositorio_tablero import RepositorioTablero
from src.dominio.estado_tarea import EstadoTarea
from src.dominio.tarea import Tarea


class MoverTarea:
    """
    Application Service: caso de uso de movimiento de tarea.

    Recibe por inyección de dependencia una implementación del puerto
    RepositorioTablero. El caso de uso no instancia repositorios concretos.
    """

    def __init__(self, repositorio: RepositorioTablero) -> None:
        self._repositorio = repositorio

    def ejecutar(self, id_tarea: UUID, estado_destino: EstadoTarea | str) -> Tarea:
        """
        Flujo principal de FEATURE_SPEC_002:
          1. Cargar el tablero desde el repositorio.
          2. (Buscar la tarea y verificar transición/WIP ocurre en Tablero.)
          3. Tablero.mover_tarea aplica las invariantes y muta el estado.
          4. Guardar el tablero actualizado (AC-05).
          5. Devolver la tarea actualizada.

        Si Tablero.mover_tarea lanza cualquier error de dominio
        (ErrorTareaNoEncontrada, ErrorTransicionInvalida, ErrorLimiteWipExcedido),
        el error se propaga sin invocar guardar (AC-06, INV-05).

        El parámetro estado_destino admite también un string canónico
        ('TODO' | 'DOING' | 'DONE') por comodidad del adaptador HTTP del PASO 12,
        pero la conversión a EstadoTarea ocurre ANTES de cargar el repositorio
        para que un string inválido no provoque IO ni efectos colaterales.
        """
        destino = self._normalizar_estado_destino(estado_destino)

        tablero = self._repositorio.cargar()
        tarea = tablero.mover_tarea(id_tarea, destino)  # puede lanzar error de dominio
        self._repositorio.guardar(tablero)
        return tarea

    @staticmethod
    def _normalizar_estado_destino(valor: EstadoTarea | str) -> EstadoTarea:
        """
        Acepta una instancia de EstadoTarea (uso desde código) o un string
        canónico (uso desde HTTP). Cualquier otro tipo o string desconocido
        produce ValueError y NO se llega a tocar el repositorio.

        Nota: este método NO valida transiciones; eso es responsabilidad
        del dominio (INV-03). Solo convierte la representación.
        """
        if isinstance(valor, EstadoTarea):
            return valor
        if isinstance(valor, str):
            try:
                return EstadoTarea[valor]
            except KeyError as exc:
                raise ValueError(
                    f"estado_destino desconocido: {valor!r}. "
                    f"Valores aceptados: TODO, DOING, DONE."
                ) from exc
        raise TypeError(
            "estado_destino debe ser EstadoTarea o un string canónico "
            "('TODO' | 'DOING' | 'DONE')."
        )