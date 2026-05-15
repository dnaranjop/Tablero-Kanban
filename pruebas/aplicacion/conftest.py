"""
Fixtures compartidas de la capa de aplicación.

Referencia: DEC-06 (la implementación en memoria del puerto vive en pruebas,
nunca en src/). Esta fixture se usará en los PASOS 8, 9 y 10.
"""

from __future__ import annotations

import pytest

from src.aplicacion.repositorio_tablero import RepositorioTablero
from src.dominio.tablero import Tablero


class RepositorioTableroEnMemoria(RepositorioTablero):
    """
    Doble en memoria del puerto RepositorioTablero.

    Contadores expuestos:
      - llamadas_cargar
      - llamadas_guardar
    Permiten a las pruebas verificar AC-04 (guardar invocado tras éxito)
    y AC-05 (guardar no invocado tras error).
    """

    def __init__(self, tablero_inicial: Tablero | None = None) -> None:
        self._tablero: Tablero = tablero_inicial if tablero_inicial else Tablero()
        self.llamadas_cargar: int = 0
        self.llamadas_guardar: int = 0

    def cargar(self) -> Tablero:
        self.llamadas_cargar += 1
        return self._tablero

    def guardar(self, tablero: Tablero) -> None:
        self.llamadas_guardar += 1
        self._tablero = tablero


@pytest.fixture
def repositorio_en_memoria() -> RepositorioTableroEnMemoria:
    """Fixture estándar: tablero vacío en memoria."""
    return RepositorioTableroEnMemoria()