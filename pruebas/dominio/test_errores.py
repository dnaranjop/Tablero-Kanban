"""
Pruebas de los errores de dominio.

Referencia: DOMAIN.md §4 / §6.
"""

import pytest

from src.dominio.errores import (
    ErrorDominio,
    ErrorLimiteWipExcedido,
    ErrorTareaNoEncontrada,
    ErrorTituloTareaInvalido,
    ErrorTransicionInvalida,
)


ERRORES_DOMAIN_MD = [
    ErrorTareaNoEncontrada,
    ErrorTransicionInvalida,
    ErrorLimiteWipExcedido,
    ErrorTituloTareaInvalido,
]


@pytest.mark.parametrize("clase_error", ERRORES_DOMAIN_MD)
def test_cada_error_de_dominio_extiende_exception(clase_error):
    """DOMAIN.md §4: los errores de dominio deben ser excepciones de Python."""
    assert issubclass(clase_error, Exception)


@pytest.mark.parametrize("clase_error", ERRORES_DOMAIN_MD)
def test_cada_error_extiende_la_raiz_error_dominio(clase_error):
    """
    Permite a la infraestructura capturar de forma uniforme cualquier error
    de dominio sin acoplarse a las subclases.
    """
    assert issubclass(clase_error, ErrorDominio)


@pytest.mark.parametrize("clase_error", ERRORES_DOMAIN_MD)
def test_cada_error_puede_instanciarse_con_mensaje(clase_error):
    """Cada error debe aceptar un mensaje opcional y propagar al ser lanzado."""
    with pytest.raises(clase_error) as info:
        raise clase_error("mensaje de prueba")
    assert "mensaje de prueba" in str(info.value)


@pytest.mark.parametrize("clase_error", ERRORES_DOMAIN_MD)
def test_cada_error_puede_instanciarse_sin_mensaje(clase_error):
    """Cada error debe poder lanzarse sin argumentos."""
    with pytest.raises(clase_error):
        raise clase_error()


def test_no_existen_errores_adicionales_en_el_modulo():
    """
    DOMAIN.md §4 define exactamente cuatro errores.
    Cualquier clase de error adicional amplía el alcance y debe rechazarse.
    """
    from src.dominio import errores as modulo_errores

    nombres_clases_error = {
        nombre
        for nombre in dir(modulo_errores)
        if not nombre.startswith("_")
        and isinstance(getattr(modulo_errores, nombre), type)
        and issubclass(getattr(modulo_errores, nombre), Exception)
    }

    esperados = {
        "ErrorDominio",  # raíz semántica permitida
        "ErrorTareaNoEncontrada",
        "ErrorTransicionInvalida",
        "ErrorLimiteWipExcedido",
        "ErrorTituloTareaInvalido",
    }

    assert nombres_clases_error == esperados