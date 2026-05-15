"""
Pruebas del caso de uso MoverTarea.

Cobertura:
  - FEATURE_SPEC_002 AC-01 a AC-06.
  - INV-01, INV-02, INV-03 (delegadas al dominio; aquí verificamos orquestación).
  - INV-05 (no persistir cambios parciales).
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from src.aplicacion.crear_tarea import CrearTarea
from src.aplicacion.mover_tarea import MoverTarea
from src.dominio.errores import (
    ErrorLimiteWipExcedido,
    ErrorTareaNoEncontrada,
    ErrorTransicionInvalida,
)
from src.dominio.estado_tarea import EstadoTarea
from src.dominio.tablero import LIMITE_WIP


# ---------- Helpers ----------

def _crear_tarea_via_caso_de_uso(repo, titulo: str):
    """Atajo: usar CrearTarea para tener tareas reales en el repositorio."""
    return CrearTarea(repo).ejecutar(titulo)


def _llenar_doing_con(repo, cantidad: int) -> None:
    """Coloca cantidad tareas en DOING usando los casos de uso reales."""
    mover = MoverTarea(repo)
    for indice in range(cantidad):
        tarea = _crear_tarea_via_caso_de_uso(repo, f"Tarea {indice + 1}")
        mover.ejecutar(tarea.id_tarea, EstadoTarea.DOING)


# ---------- AC-01: TODO -> DOING con DOING vacío ----------

def test_mover_de_todo_a_doing_funciona_con_doing_vacio(repositorio_en_memoria):
    """FEATURE_SPEC_002 AC-01 + INV-01 (vía dominio)."""
    tarea = _crear_tarea_via_caso_de_uso(repositorio_en_memoria, "Tarea uno")
    contador_guardar_antes = repositorio_en_memoria.llamadas_guardar

    mover = MoverTarea(repositorio_en_memoria)
    resultado = mover.ejecutar(tarea.id_tarea, EstadoTarea.DOING)

    assert resultado.estado is EstadoTarea.DOING
    assert repositorio_en_memoria.llamadas_guardar == contador_guardar_antes + 1


def test_mover_acepta_estado_destino_como_string_canonico(repositorio_en_memoria):
    """
    Comodidad para el adaptador HTTP del PASO 12.
    El caso de uso normaliza 'DOING' a EstadoTarea.DOING.
    """
    tarea = _crear_tarea_via_caso_de_uso(repositorio_en_memoria, "Tarea uno")
    mover = MoverTarea(repositorio_en_memoria)
    resultado = mover.ejecutar(tarea.id_tarea, "DOING")
    assert resultado.estado is EstadoTarea.DOING


# ---------- AC-02: cuarta tarea en DOING ----------

def test_mover_una_cuarta_tarea_a_doing_propaga_error_limite_wip(repositorio_en_memoria):
    """FEATURE_SPEC_002 AC-02 + INV-01, INV-02."""
    _llenar_doing_con(repositorio_en_memoria, LIMITE_WIP)
    cuarta = _crear_tarea_via_caso_de_uso(repositorio_en_memoria, "Cuarta")

    mover = MoverTarea(repositorio_en_memoria)
    with pytest.raises(ErrorLimiteWipExcedido):
        mover.ejecutar(cuarta.id_tarea, EstadoTarea.DOING)


def test_al_rechazar_la_cuarta_tarea_no_se_invoca_guardar(repositorio_en_memoria):
    """FEATURE_SPEC_002 AC-06 + INV-05."""
    _llenar_doing_con(repositorio_en_memoria, LIMITE_WIP)
    cuarta = _crear_tarea_via_caso_de_uso(repositorio_en_memoria, "Cuarta")

    contador_antes = repositorio_en_memoria.llamadas_guardar
    mover = MoverTarea(repositorio_en_memoria)
    with pytest.raises(ErrorLimiteWipExcedido):
        mover.ejecutar(cuarta.id_tarea, EstadoTarea.DOING)

    # Tras el intento fallido, guardar() NO se invoca.
    assert repositorio_en_memoria.llamadas_guardar == contador_antes


# ---------- AC-03: TODO -> DONE (transición inválida) ----------

def test_mover_de_todo_a_done_propaga_transicion_invalida(repositorio_en_memoria):
    """FEATURE_SPEC_002 AC-03 + INV-03."""
    tarea = _crear_tarea_via_caso_de_uso(repositorio_en_memoria, "Tarea uno")

    mover = MoverTarea(repositorio_en_memoria)
    with pytest.raises(ErrorTransicionInvalida):
        mover.ejecutar(tarea.id_tarea, EstadoTarea.DONE)


def test_tras_transicion_invalida_no_se_invoca_guardar(repositorio_en_memoria):
    """FEATURE_SPEC_002 AC-06 + INV-05."""
    tarea = _crear_tarea_via_caso_de_uso(repositorio_en_memoria, "Tarea uno")
    contador_antes = repositorio_en_memoria.llamadas_guardar

    mover = MoverTarea(repositorio_en_memoria)
    with pytest.raises(ErrorTransicionInvalida):
        mover.ejecutar(tarea.id_tarea, EstadoTarea.DONE)

    assert repositorio_en_memoria.llamadas_guardar == contador_antes


# ---------- AC-04: DOING -> DONE ----------

def test_mover_de_doing_a_done_funciona(repositorio_en_memoria):
    """FEATURE_SPEC_002 AC-04 + INV-03."""
    tarea = _crear_tarea_via_caso_de_uso(repositorio_en_memoria, "Tarea uno")
    mover = MoverTarea(repositorio_en_memoria)
    mover.ejecutar(tarea.id_tarea, EstadoTarea.DOING)
    resultado = mover.ejecutar(tarea.id_tarea, EstadoTarea.DONE)

    assert resultado.estado is EstadoTarea.DONE


# ---------- AC-05: tras éxito, guardar se invoca exactamente una vez ----------

def test_tras_movimiento_exitoso_guardar_se_invoca_exactamente_una_vez(
    repositorio_en_memoria,
):
    """FEATURE_SPEC_002 AC-05."""
    tarea = _crear_tarea_via_caso_de_uso(repositorio_en_memoria, "Tarea uno")
    contador_antes = repositorio_en_memoria.llamadas_guardar

    mover = MoverTarea(repositorio_en_memoria)
    mover.ejecutar(tarea.id_tarea, EstadoTarea.DOING)

    assert repositorio_en_memoria.llamadas_guardar == contador_antes + 1


# ---------- Tarea inexistente ----------

def test_mover_una_tarea_inexistente_propaga_error_tarea_no_encontrada(
    repositorio_en_memoria,
):
    """DOMAIN.md §4: ErrorTareaNoEncontrada se propaga sin guardar."""
    id_inventado = uuid4()
    contador_antes = repositorio_en_memoria.llamadas_guardar

    mover = MoverTarea(repositorio_en_memoria)
    with pytest.raises(ErrorTareaNoEncontrada):
        mover.ejecutar(id_inventado, EstadoTarea.DOING)

    assert repositorio_en_memoria.llamadas_guardar == contador_antes


# ---------- Normalización del estado destino ----------

def test_string_canonico_invalido_propaga_value_error_sin_tocar_el_repositorio(
    repositorio_en_memoria,
):
    """
    Un string no canónico debe rechazarse ANTES de cargar el tablero.
    Verifica que no se invoca ni cargar() ni guardar().
    """
    contador_cargar_antes = repositorio_en_memoria.llamadas_cargar
    contador_guardar_antes = repositorio_en_memoria.llamadas_guardar

    mover = MoverTarea(repositorio_en_memoria)
    with pytest.raises(ValueError):
        mover.ejecutar(uuid4(), "BLOCKED")  # estado fuera de DOMAIN.md §1

    assert repositorio_en_memoria.llamadas_cargar == contador_cargar_antes
    assert repositorio_en_memoria.llamadas_guardar == contador_guardar_antes


def test_tipo_no_soportado_de_estado_destino_propaga_type_error(repositorio_en_memoria):
    """
    Pasar un entero (o cualquier tipo distinto a EstadoTarea/str) debe fallar
    con TypeError sin invocar el repositorio.
    """
    contador_cargar_antes = repositorio_en_memoria.llamadas_cargar
    contador_guardar_antes = repositorio_en_memoria.llamadas_guardar

    mover = MoverTarea(repositorio_en_memoria)
    with pytest.raises(TypeError):
        mover.ejecutar(uuid4(), 42)  # type: ignore[arg-type]

    assert repositorio_en_memoria.llamadas_cargar == contador_cargar_antes
    assert repositorio_en_memoria.llamadas_guardar == contador_guardar_antes


# ---------- Inyección de dependencias y aislamiento ----------

def test_caso_de_uso_recibe_el_repositorio_por_constructor():
    from pruebas.aplicacion.conftest import RepositorioTableroEnMemoria

    repo = RepositorioTableroEnMemoria()
    caso_de_uso = MoverTarea(repo)
    assert caso_de_uso._repositorio is repo


def test_modulo_mover_tarea_no_importa_infraestructura():
    """ARCHITECTURE.md §3."""
    import inspect
    from pathlib import Path

    from src.aplicacion import mover_tarea as modulo

    contenido = Path(inspect.getfile(modulo)).read_text(encoding="utf-8")
    assert "import src.infraestructura" not in contenido
    assert "from src.infraestructura" not in contenido