"""
Pruebas del aggregate root Tablero.

Cobertura:
  - FEATURE_SPEC_001 (crear tarea): AC-01 a AC-05.
  - FEATURE_SPEC_002 (mover tarea): AC-01 a AC-06 (solo lo que es responsabilidad
    del dominio; AC-05/AC-06 sobre persistencia se cierran en los casos de uso).
  - FEATURE_SPEC_003 (obtener tablero): AC-01, AC-02.
  - INV-01 a INV-05.
"""

from uuid import uuid4

import pytest

from src.dominio.errores import (
    ErrorLimiteWipExcedido,
    ErrorTareaNoEncontrada,
    ErrorTituloTareaInvalido,
    ErrorTransicionInvalida,
)
from src.dominio.estado_tarea import EstadoTarea
from src.dominio.tablero import LIMITE_WIP, Tablero


# ---------- Helper de pruebas ----------

def _llenar_doing_con(tablero: Tablero, cantidad: int) -> None:
    """
    Coloca cantidad tareas en DOING partiendo de TODO.
    Asume que cantidad <= LIMITE_WIP.
    """
    for indice in range(cantidad):
        tarea = tablero.crear_tarea(f"Tarea {indice + 1}")
        tablero.mover_tarea(tarea.id_tarea, EstadoTarea.DOING)


# ---------- Constante de dominio ----------

def test_limite_wip_es_la_constante_3():
    """DOMAIN.md §1 y GLOSSARY.md: LimiteWip = 3 (TECH_CONSTRAINTS.md §2)."""
    assert LIMITE_WIP == 3


# ---------- Crear tarea: FEATURE_SPEC_001 ----------

def test_crear_tarea_con_titulo_valido_produce_tarea_en_todo():
    """FEATURE_SPEC_001 AC-01."""
    tablero = Tablero()
    tarea = tablero.crear_tarea("Pagar facturas")
    assert tarea.titulo == "Pagar facturas"
    assert tarea.estado is EstadoTarea.TODO


def test_crear_tarea_la_agrega_al_tablero():
    """FEATURE_SPEC_001 flujo principal paso 4."""
    tablero = Tablero()
    tarea = tablero.crear_tarea("Pagar facturas")
    assert tarea in tablero.listar_tareas()


def test_crear_tarea_con_titulo_vacio_lanza_error_y_no_modifica_tablero():
    """FEATURE_SPEC_001 AC-02, AC-05 + INV-04, INV-05."""
    tablero = Tablero()
    with pytest.raises(ErrorTituloTareaInvalido):
        tablero.crear_tarea("")
    assert tablero.listar_tareas() == []


def test_crear_tarea_con_solo_espacios_lanza_error_y_no_modifica_tablero():
    """FEATURE_SPEC_001 AC-03, AC-05 + INV-04, INV-05."""
    tablero = Tablero()
    with pytest.raises(ErrorTituloTareaInvalido):
        tablero.crear_tarea("   ")
    assert tablero.listar_tareas() == []


# ---------- Mover tarea: FEATURE_SPEC_002 ----------

def test_mover_de_todo_a_doing_funciona_con_doing_vacio():
    """FEATURE_SPEC_002 AC-01."""
    tablero = Tablero()
    tarea = tablero.crear_tarea("Tarea uno")
    tablero.mover_tarea(tarea.id_tarea, EstadoTarea.DOING)
    assert tarea.estado is EstadoTarea.DOING


def test_mover_de_todo_a_doing_funciona_con_dos_tareas_previas_en_doing():
    """FEATURE_SPEC_002 AC-01: límite aún no alcanzado (2 < 3)."""
    tablero = Tablero()
    _llenar_doing_con(tablero, 2)
    nueva = tablero.crear_tarea("Tercera tarea")
    tablero.mover_tarea(nueva.id_tarea, EstadoTarea.DOING)
    agrupado = tablero.obtener_tareas_por_estado()
    assert len(agrupado[EstadoTarea.DOING]) == 3


def test_mover_una_cuarta_tarea_a_doing_lanza_error_limite_wip():
    """FEATURE_SPEC_002 AC-02 + INV-01, INV-02."""
    tablero = Tablero()
    _llenar_doing_con(tablero, LIMITE_WIP)  # DOING = 3
    cuarta = tablero.crear_tarea("Cuarta tarea")
    with pytest.raises(ErrorLimiteWipExcedido):
        tablero.mover_tarea(cuarta.id_tarea, EstadoTarea.DOING)


def test_al_rechazar_la_cuarta_tarea_el_tablero_no_se_modifica():
    """INV-02, INV-05 + FEATURE_SPEC_002 AC-06."""
    tablero = Tablero()
    _llenar_doing_con(tablero, LIMITE_WIP)
    cuarta = tablero.crear_tarea("Cuarta tarea")

    agrupado_antes = tablero.obtener_tareas_por_estado()
    estados_antes = {t.id_tarea: t.estado for t in tablero.listar_tareas()}

    with pytest.raises(ErrorLimiteWipExcedido):
        tablero.mover_tarea(cuarta.id_tarea, EstadoTarea.DOING)

    # La cuarta sigue en TODO; las tres anteriores siguen en DOING.
    agrupado_despues = tablero.obtener_tareas_por_estado()
    estados_despues = {t.id_tarea: t.estado for t in tablero.listar_tareas()}
    assert estados_antes == estados_despues
    assert len(agrupado_despues[EstadoTarea.DOING]) == LIMITE_WIP
    assert cuarta.estado is EstadoTarea.TODO
    # Comprobación adicional sobre la agrupación TODO.
    assert cuarta in agrupado_despues[EstadoTarea.TODO]
    # El conteo total no cambia.
    assert len(tablero.listar_tareas()) == len(agrupado_antes[EstadoTarea.TODO]) + \
        len(agrupado_antes[EstadoTarea.DOING]) + len(agrupado_antes[EstadoTarea.DONE])


def test_mover_de_todo_a_done_lanza_transicion_invalida():
    """FEATURE_SPEC_002 AC-03 + INV-03."""
    tablero = Tablero()
    tarea = tablero.crear_tarea("Tarea uno")
    with pytest.raises(ErrorTransicionInvalida):
        tablero.mover_tarea(tarea.id_tarea, EstadoTarea.DONE)
    assert tarea.estado is EstadoTarea.TODO  # INV-05


def test_mover_de_doing_a_done_funciona():
    """FEATURE_SPEC_002 AC-04 + INV-03."""
    tablero = Tablero()
    tarea = tablero.crear_tarea("Tarea uno")
    tablero.mover_tarea(tarea.id_tarea, EstadoTarea.DOING)
    tablero.mover_tarea(tarea.id_tarea, EstadoTarea.DONE)
    assert tarea.estado is EstadoTarea.DONE


def test_mover_desde_done_no_es_transicion_valida():
    """INV-03: DONE es estado terminal (DOMAIN.md §3 enumera solo dos transiciones)."""
    tablero = Tablero()
    tarea = tablero.crear_tarea("Tarea uno")
    tablero.mover_tarea(tarea.id_tarea, EstadoTarea.DOING)
    tablero.mover_tarea(tarea.id_tarea, EstadoTarea.DONE)
    with pytest.raises(ErrorTransicionInvalida):
        tablero.mover_tarea(tarea.id_tarea, EstadoTarea.DOING)
    with pytest.raises(ErrorTransicionInvalida):
        tablero.mover_tarea(tarea.id_tarea, EstadoTarea.TODO)
    assert tarea.estado is EstadoTarea.DONE


def test_mover_una_tarea_inexistente_lanza_tarea_no_encontrada():
    """DOMAIN.md §4: ErrorTareaNoEncontrada."""
    tablero = Tablero()
    id_inventado = uuid4()
    with pytest.raises(ErrorTareaNoEncontrada):
        tablero.mover_tarea(id_inventado, EstadoTarea.DOING)


def test_mover_con_estado_destino_no_estadotarea_lanza_typeerror():
    """Solo se aceptan instancias de EstadoTarea como destino (defensa de tipo)."""
    tablero = Tablero()
    tarea = tablero.crear_tarea("Tarea uno")
    with pytest.raises(TypeError):
        tablero.mover_tarea(tarea.id_tarea, "DOING")  # type: ignore[arg-type]


# ---------- Obtener tablero: FEATURE_SPEC_003 ----------

def test_obtener_tareas_por_estado_devuelve_siempre_las_tres_claves():
    """FEATURE_SPEC_003 AC-01: incluso con tablero vacío."""
    tablero = Tablero()
    agrupado = tablero.obtener_tareas_por_estado()
    assert set(agrupado.keys()) == {EstadoTarea.TODO, EstadoTarea.DOING, EstadoTarea.DONE}
    assert agrupado[EstadoTarea.TODO] == []
    assert agrupado[EstadoTarea.DOING] == []
    assert agrupado[EstadoTarea.DONE] == []


def test_obtener_tareas_por_estado_no_modifica_el_tablero():
    """FEATURE_SPEC_003 AC-02: una consulta no muta estado."""
    tablero = Tablero()
    tablero.crear_tarea("Tarea uno")
    tablero.crear_tarea("Tarea dos")

    snapshot_antes = [(t.id_tarea, t.estado) for t in tablero.listar_tareas()]
    _ = tablero.obtener_tareas_por_estado()
    snapshot_despues = [(t.id_tarea, t.estado) for t in tablero.listar_tareas()]

    assert snapshot_antes == snapshot_despues


def test_obtener_tareas_por_estado_devuelve_listas_independientes():
    """
    Modificar la salida no debe afectar al tablero.
    Refuerza FEATURE_SPEC_003 AC-02.
    """
    tablero = Tablero()
    tablero.crear_tarea("Tarea uno")
    agrupado = tablero.obtener_tareas_por_estado()
    agrupado[EstadoTarea.TODO].clear()
    assert len(tablero.listar_tareas()) == 1


# ---------- Construcción inicial del Tablero ----------

def test_tablero_inicializa_vacio_por_defecto():
    """Caso típico de arranque del sistema."""
    tablero = Tablero()
    assert tablero.listar_tareas() == []


def test_tablero_inicializa_con_tareas_preexistentes_validas():
    """
    Soporta carga desde el repositorio (necesario para el PASO 11):
    si las tareas precargadas cumplen INV-01, el Tablero se construye sin error.
    """
    tablero_inicial = Tablero()
    t1 = tablero_inicial.crear_tarea("Tarea uno")
    t2 = tablero_inicial.crear_tarea("Tarea dos")
    tablero_inicial.mover_tarea(t1.id_tarea, EstadoTarea.DOING)

    reconstruido = Tablero(tareas=tablero_inicial.listar_tareas())
    ids = {t.id_tarea for t in reconstruido.listar_tareas()}
    assert ids == {t1.id_tarea, t2.id_tarea}


def test_tablero_inicializado_con_estado_invalido_rechaza_la_construccion():
    """
    INV-01: si la carga inicial declara más de LIMITE_WIP tareas en DOING,
    el Tablero no puede arrancar en un estado que ya viola sus invariantes.
    """
    # Construimos cuatro tareas en DOING manualmente para simular un JSON corrupto.
    from src.dominio.tarea import Tarea

    tareas_invalidas = [
        Tarea(titulo="A", estado=EstadoTarea.DOING),
        Tarea(titulo="B", estado=EstadoTarea.DOING),
        Tarea(titulo="C", estado=EstadoTarea.DOING),
        Tarea(titulo="D", estado=EstadoTarea.DOING),
    ]
    with pytest.raises(ErrorLimiteWipExcedido):
        Tablero(tareas=tareas_invalidas)