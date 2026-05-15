"""
Pruebas de contrato del puerto RepositorioTablero.

Referencia: ARCHITECTURE.md §3, §4.

Estas pruebas garantizan que:
  - El puerto es abstracto (no instanciable directamente).
  - Expone exactamente los dos metodos del contrato.
  - Un subtipo que NO implementa ambos metodos sigue siendo inutilizable.
  - El modulo no introduce dependencias hacia infraestructura.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from src.aplicacion.repositorio_tablero import RepositorioTablero
from src.dominio.tablero import Tablero


# ---------- Contrato abstracto ----------

def test_repositorio_tablero_es_abstracto():
    """
    ARCHITECTURE.md §4: RepositorioTablero es un puerto abstracto.
    Intentar instanciarlo directamente debe fallar con TypeError.
    """
    with pytest.raises(TypeError):
        RepositorioTablero()  # type: ignore[abstract]


def test_repositorio_tablero_expone_exactamente_cargar_y_guardar():
    """
    ARCHITECTURE.md §4 lista exactamente dos operaciones del puerto:
      - cargar() -> Tablero
      - guardar(tablero: Tablero) -> None
    Cualquier metodo abstracto adicional ampliaria el contrato.
    """
    metodos_abstractos = set(RepositorioTablero.__abstractmethods__)  
    assert metodos_abstractos == {"cargar", "guardar"}


def test_metodos_abstractos_tienen_la_firma_documentada():
    """
    cargar() no recibe parametros (salvo self).
    guardar(tablero) recibe exactamente un parametro de dominio.
    """
    firma_cargar = inspect.signature(RepositorioTablero.cargar)
    parametros_cargar = [
        nombre for nombre in firma_cargar.parameters if nombre != "self"
    ]
    assert parametros_cargar == []

    firma_guardar = inspect.signature(RepositorioTablero.guardar)
    parametros_guardar = [
        nombre for nombre in firma_guardar.parameters if nombre != "self"
    ]
    assert parametros_guardar == ["tablero"]


# ---------- Subtipos: comportamiento esperado ----------

class _RepositorioIncompleto(RepositorioTablero):
    """Solo implementa cargar(); debe seguir siendo no instanciable."""

    def cargar(self) -> Tablero:
        return Tablero()


def test_subtipo_que_no_implementa_todo_el_contrato_no_es_instanciable():
    """
    Un subtipo que no implementa AMBOS metodos abstractos sigue siendo abstracto.
    Garantiza que el contrato es completo y obligatorio.
    """
    with pytest.raises(TypeError):
        _RepositorioIncompleto()  # type: ignore[abstract]


class _RepositorioEnMemoria(RepositorioTablero):
    """Implementación mínima en memoria, util para pruebas de los casos de uso."""

    def __init__(self) -> None:
        self._tablero: Tablero = Tablero()
        self.contador_guardar: int = 0

    def cargar(self) -> Tablero:
        return self._tablero

    def guardar(self, tablero: Tablero) -> None:
        self._tablero = tablero
        self.contador_guardar += 1


def test_subtipo_completo_si_es_instanciable_y_cumple_el_contrato():
    """
    Un subtipo que implementa ambos metodos debe instanciarse sin error
    y debe ser reconocido como instancia del puerto.
    """
    repositorio = _RepositorioEnMemoria()
    assert isinstance(repositorio, RepositorioTablero)
    assert isinstance(repositorio.cargar(), Tablero)
    repositorio.guardar(Tablero())
    assert repositorio.contador_guardar == 1


# ---------- Aislamiento de capa: ARCHITECTURE.md §3 ----------

def test_modulo_puerto_no_importa_infraestructura():
    """
    ARCHITECTURE.md §3: src/aplicacion/ no puede importar src/infraestructura/.
    Verificamos via inspección del fichero (no por ejecución).
    """
    archivo = Path(inspect.getfile(RepositorioTablero))
    contenido = archivo.read_text(encoding="utf-8")
    # Patrones de import prohibidos
    assert "import src.infraestructura" not in contenido
    assert "from src.infraestructura" not in contenido


def test_modulo_puerto_no_importa_modulos_externos_de_io():
    """
    ARCHITECTURE.md §1, §4: el puerto es agnóstico de la tecnología.
    No debe acoplar la aplicacion a Flask, JSON, requests, etc.
    """
    archivo = Path(inspect.getfile(RepositorioTablero))
    contenido = archivo.read_text(encoding="utf-8")
    for prohibido in ("flask", "json", "requests", "sqlalchemy", "httpx"):
        assert f"import {prohibido}" not in contenido, (
            f"El puerto importa {prohibido}; deberia ser agnostico de IO."
        )
        assert f"from {prohibido}" not in contenido, (
            f"El puerto importa de {prohibido}; deberia ser agnostico de IO."
        )