"""
Pruebas de la entidad Tarea.

Referencia:
  - DOMAIN.md §1 (campos), §6 (nomenclatura).
  - INV-04 (titulo obligatorio).
  - FEATURE_SPEC_001 AC-01 (estado inicial TODO), AC-02, AC-03 (titulo invalido).
  - TECH_CONSTRAINTS.md §2 (no agregar campos).
"""

from dataclasses import fields
from uuid import UUID

import pytest

from src.dominio.errores import ErrorTituloTareaInvalido
from src.dominio.estado_tarea import EstadoTarea
from src.dominio.tarea import Tarea


# ---------- Estructura ----------

def test_tarea_expone_exactamente_id_titulo_y_estado():
    """
    DOMAIN.md §1 y TECH_CONSTRAINTS.md §2: Tarea solo tiene id_tarea, titulo, estado.
    Cualquier campo adicional (prioridad, fecha_limite, usuario...) amplia el alcance.
    """
    nombres_campos = {campo.name for campo in fields(Tarea)}
    assert nombres_campos == {"id_tarea", "titulo", "estado"}


# ---------- Creación válida (FEATURE_SPEC_001 AC-01) ----------

def test_crear_tarea_con_titulo_valido_genera_id_tarea_uuid():
    tarea = Tarea(titulo="Pagar facturas")
    assert isinstance(tarea.id_tarea, UUID)


def test_crear_tarea_con_titulo_valido_conserva_titulo():
    tarea = Tarea(titulo="Pagar facturas")
    assert tarea.titulo == "Pagar facturas"


def test_crear_tarea_con_titulo_valido_arranca_en_estado_todo():
    """FEATURE_SPEC_001 AC-01: una tarea nueva tiene estado TODO por defecto."""
    tarea = Tarea(titulo="Pagar facturas")
    assert tarea.estado is EstadoTarea.TODO


def test_dos_tareas_creadas_tienen_ids_distintos():
    """El id_tarea se genera por defecto y debe ser único."""
    t1 = Tarea(titulo="Tarea uno")
    t2 = Tarea(titulo="Tarea dos")
    assert t1.id_tarea != t2.id_tarea


# ---------- Validación de título (INV-04) ----------

@pytest.mark.parametrize("titulo_invalido", ["", " ", "   ", "\t", "\n", " \t \n "])
def test_crear_tarea_con_titulo_vacio_o_solo_espacios_lanza_error(titulo_invalido):
    """
    INV-04 y FEATURE_SPEC_001 AC-02, AC-03.
    Cubre cadena vacía, espacios simples, tabs y saltos de línea.
    """
    with pytest.raises(ErrorTituloTareaInvalido):
        Tarea(titulo=titulo_invalido)


def test_crear_tarea_con_titulo_no_string_lanza_error():
    """INV-04: el titulo debe ser un string válido."""
    with pytest.raises(ErrorTituloTareaInvalido):
        Tarea(titulo=None)  # type: ignore[arg-type]


# ---------- cambiar_estado ----------

def test_cambiar_estado_acepta_un_estadotarea_valido():
    """
    Cambio interno de estado. No valida transiciones: esa responsabilidad
    es de Tablero (PASO 5). Aquí solo se prueba la mutación.
    """
    tarea = Tarea(titulo="Pagar facturas")
    tarea.cambiar_estado(EstadoTarea.DOING)
    assert tarea.estado is EstadoTarea.DOING


def test_cambiar_estado_rechaza_valores_que_no_son_estadotarea():
    """No se aceptan strings, ints ni None como estado."""
    tarea = Tarea(titulo="Pagar facturas")
    with pytest.raises(TypeError):
        tarea.cambiar_estado("DOING")  # type: ignore[arg-type]