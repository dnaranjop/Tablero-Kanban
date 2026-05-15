"""
Pruebas del caso de uso CrearTarea.

Cobertura:
  - FEATURE_SPEC_001 AC-01 a AC-05.
  - INV-04 (titulo obligatorio, delegada al dominio).
  - INV-05 (no persistir cambios parciales en error).
"""

from __future__ import annotations

from uuid import UUID

import pytest

from src.aplicacion.crear_tarea import CrearTarea
from src.dominio.errores import ErrorTituloTareaInvalido
from src.dominio.estado_tarea import EstadoTarea


# ---------- AC-01: creación válida ----------

def test_crear_tarea_con_titulo_valido_devuelve_tarea_con_id_titulo_y_estado_todo(
    repositorio_en_memoria,
):
    """FEATURE_SPEC_001 AC-01."""
    caso_de_uso = CrearTarea(repositorio_en_memoria)
    tarea = caso_de_uso.ejecutar("Pagar facturas")

    assert isinstance(tarea.id_tarea, UUID)
    assert tarea.titulo == "Pagar facturas"
    assert tarea.estado is EstadoTarea.TODO


def test_crear_tarea_persistida_aparece_en_el_tablero(repositorio_en_memoria):
    """Refuerza AC-01: el tablero cargado tras crear contiene la tarea."""
    caso_de_uso = CrearTarea(repositorio_en_memoria)
    tarea = caso_de_uso.ejecutar("Pagar facturas")

    tablero = repositorio_en_memoria.cargar()
    ids = {t.id_tarea for t in tablero.listar_tareas()}
    assert tarea.id_tarea in ids


# ---------- AC-02 y AC-03: título inválido ----------

@pytest.mark.parametrize("titulo_invalido", ["", " ", "   ", "\t", "\n"])
def test_crear_tarea_con_titulo_invalido_propaga_error_de_dominio(
    repositorio_en_memoria, titulo_invalido
):
    """FEATURE_SPEC_001 AC-02 y AC-03 (INV-04)."""
    caso_de_uso = CrearTarea(repositorio_en_memoria)
    with pytest.raises(ErrorTituloTareaInvalido):
        caso_de_uso.ejecutar(titulo_invalido)


# ---------- AC-04: tras éxito, guardar() se invoca una vez ----------

def test_tras_creacion_exitosa_el_repositorio_recibe_guardar_exactamente_una_vez(
    repositorio_en_memoria,
):
    """FEATURE_SPEC_001 AC-04."""
    caso_de_uso = CrearTarea(repositorio_en_memoria)
    caso_de_uso.ejecutar("Pagar facturas")

    assert repositorio_en_memoria.llamadas_guardar == 1


def test_tras_creacion_exitosa_el_repositorio_recibe_cargar_exactamente_una_vez(
    repositorio_en_memoria,
):
    """
    El flujo principal (FEATURE_SPEC_001) carga el tablero una sola vez.
    Cargas adicionales sugerirían un caso de uso que no respeta el flujo.
    """
    caso_de_uso = CrearTarea(repositorio_en_memoria)
    caso_de_uso.ejecutar("Pagar facturas")

    assert repositorio_en_memoria.llamadas_cargar == 1


# ---------- AC-05: tras error, guardar() NO se invoca (INV-05) ----------

@pytest.mark.parametrize("titulo_invalido", ["", "   "])
def test_tras_error_de_dominio_el_repositorio_no_recibe_guardar(
    repositorio_en_memoria, titulo_invalido
):
    """FEATURE_SPEC_001 AC-05 + INV-05."""
    caso_de_uso = CrearTarea(repositorio_en_memoria)
    with pytest.raises(ErrorTituloTareaInvalido):
        caso_de_uso.ejecutar(titulo_invalido)

    assert repositorio_en_memoria.llamadas_guardar == 0


# ---------- Inyección de dependencias ----------

def test_caso_de_uso_recibe_el_repositorio_por_constructor():
    """
    El caso de uso NO instancia repositorios concretos por su cuenta.
    Verificamos que el atributo interno corresponde al objeto inyectado.
    """
    from pruebas.aplicacion.conftest import RepositorioTableroEnMemoria

    repo = RepositorioTableroEnMemoria()
    caso_de_uso = CrearTarea(repo)
    assert caso_de_uso._repositorio is repo


# ---------- Aislamiento de capa ----------

def test_modulo_crear_tarea_no_importa_infraestructura():
    """
    ARCHITECTURE.md §3: la capa de aplicación no importa de infraestructura.
    """
    import inspect
    from pathlib import Path

    from src.aplicacion import crear_tarea as modulo

    contenido = Path(inspect.getfile(modulo)).read_text(encoding="utf-8")
    assert "import src.infraestructura" not in contenido
    assert "from src.infraestructura" not in contenido