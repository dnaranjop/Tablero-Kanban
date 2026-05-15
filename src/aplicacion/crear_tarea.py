"""
Caso de uso: CrearTarea.

Referencia:
  - FEATURE_SPEC_001 (flujo principal y AC-01 a AC-05).
  - ARCHITECTURE.md §3: la aplicación importa de dominio, nunca de infraestructura.
  - DOMAIN.md §5: la creación de tareas pasa siempre por Tablero (aggregate root).

Contrato del caso de uso:
  - Recibe el título de la tarea.
  - Carga el Tablero, le pide crear la Tarea, persiste el resultado.
  - Devuelve la Tarea creada.
  - Si la validación de INV-04 falla, propaga ErrorTituloTareaInvalido y NO guarda.

Este módulo no conoce JSON, Flask ni archivos: solo conoce el puerto abstracto
RepositorioTablero (PASO 7) y el dominio.
"""

from __future__ import annotations

from src.aplicacion.repositorio_tablero import RepositorioTablero
from src.dominio.tarea import Tarea


class CrearTarea:
    """
    Application Service: caso de uso de creación de tarea.

    Recibe por inyección de dependencia una implementación del puerto
    RepositorioTablero. El caso de uso no instancia repositorios concretos.
    """

    def __init__(self, repositorio: RepositorioTablero) -> None:
        self._repositorio = repositorio

    def ejecutar(self, titulo: str) -> Tarea:
        """
        Flujo principal de FEATURE_SPEC_001:
          1. Cargar el tablero desde el repositorio.
          2. (la validación de título y la asignación de id ocurren dentro
             del aggregate root Tablero, paso a paso 4 del flujo).
          3. Crear la Tarea via Tablero.crear_tarea.
          4. Guardar el tablero actualizado (AC-04).
          5. Devolver la Tarea creada.

        Si Tablero.crear_tarea lanza ErrorTituloTareaInvalido, el error se
        propaga sin invocar guardar (AC-05, INV-05).
        """
        tablero = self._repositorio.cargar()
        tarea = tablero.crear_tarea(titulo)  # puede lanzar ErrorTituloTareaInvalido
        self._repositorio.guardar(tablero)
        return tarea