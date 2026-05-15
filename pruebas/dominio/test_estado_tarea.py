"""
Pruebas del enumerado EstadoTarea.

Referencia: DOMAIN.md §1, §6 / GLOSSARY.md (EstadoTarea).
"""

import pytest

from src.dominio.estado_tarea import EstadoTarea


def test_estado_tarea_expone_los_tres_valores_del_dominio():
    """DOMAIN.md §1: EstadoTarea debe ser un enumerado con TODO, DOING y DONE."""
    nombres = {miembro.name for miembro in EstadoTarea}
    assert nombres == {"TODO", "DOING", "DONE"}


def test_estado_tarea_no_acepta_valores_adicionales():
    """
    DOMAIN.md §1 y CONTEXT.md §6 ([FUERA] Estados adicionales).
    El enumerado debe tener exactamente tres miembros.
    """
    assert len(list(EstadoTarea)) == 3


def test_estado_tarea_acceso_por_nombre():
    """Permite obtener un miembro a partir de su nombre canónico."""
    assert EstadoTarea["TODO"] is EstadoTarea.TODO
    assert EstadoTarea["DOING"] is EstadoTarea.DOING
    assert EstadoTarea["DONE"] is EstadoTarea.DONE


def test_estado_tarea_nombre_inexistente_lanza_keyerror():
    """Acceder a un estado no definido debe fallar (refuerza el alcance cerrado)."""
    with pytest.raises(KeyError):
        EstadoTarea["BLOCKED"]


def test_estado_tarea_valores_son_strings_mayusculas():
    """DOMAIN.md §6: valores del enumerado en mayúsculas."""
    for miembro in EstadoTarea:
        assert isinstance(miembro.value, str)
        assert miembro.value == miembro.value.upper()
        assert miembro.value == miembro.name