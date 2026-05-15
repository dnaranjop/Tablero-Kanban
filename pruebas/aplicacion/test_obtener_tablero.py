"""
Pruebas del caso de uso ObtenerTablero.

Cobertura:
  - FEATURE_SPEC_003 AC-01 (siempre las tres claves).
  - FEATURE_SPEC_003 AC-02 (consulta NO muta ni guarda).
  - FEATURE_SPEC_003 AC-03 (estructura serializable).
"""

from __future__ import annotations

import json

from src.aplicacion.crear_tarea import CrearTarea
from src.aplicacion.mover_tarea import MoverTarea
from src.aplicacion.obtener_tablero import ObtenerTablero
from src.dominio.estado_tarea import EstadoTarea


# ---------- Helpers ----------

def _crear(repo, titulo):
    return CrearTarea(repo).ejecutar(titulo)


# ---------- AC-01: las tres claves siempre presentes ----------

def test_tablero_vacio_devuelve_las_tres_claves_con_listas_vacias(repositorio_en_memoria):
    """FEATURE_SPEC_003 AC-01: incluso con tablero vacio."""
    caso_de_uso = ObtenerTablero(repositorio_en_memoria)
    resultado = caso_de_uso.ejecutar()

    assert set(resultado.keys()) == {"TODO", "DOING", "DONE"}
    assert resultado["TODO"] == []
    assert resultado["DOING"] == []
    assert resultado["DONE"] == []


def test_tablero_con_tareas_agrupa_por_estado(repositorio_en_memoria):
    """FEATURE_SPEC_003 AC-01."""
    t1 = _crear(repositorio_en_memoria, "Tarea uno")  # queda en TODO
    t2 = _crear(repositorio_en_memoria, "Tarea dos")
    t3 = _crear(repositorio_en_memoria, "Tarea tres")

    mover = MoverTarea(repositorio_en_memoria)
    mover.ejecutar(t2.id_tarea, EstadoTarea.DOING)
    mover.ejecutar(t3.id_tarea, EstadoTarea.DOING)
    mover.ejecutar(t3.id_tarea, EstadoTarea.DONE)

    resultado = ObtenerTablero(repositorio_en_memoria).ejecutar()

    ids_todo = {tarea["id_tarea"] for tarea in resultado["TODO"]}
    ids_doing = {tarea["id_tarea"] for tarea in resultado["DOING"]}
    ids_done = {tarea["id_tarea"] for tarea in resultado["DONE"]}

    assert ids_todo == {str(t1.id_tarea)}
    assert ids_doing == {str(t2.id_tarea)}
    assert ids_done == {str(t3.id_tarea)}


# ---------- AC-02: consulta no muta ni guarda ----------

def test_la_consulta_no_invoca_guardar(repositorio_en_memoria):
    """FEATURE_SPEC_003 AC-02."""
    _crear(repositorio_en_memoria, "Tarea uno")
    contador_guardar_antes = repositorio_en_memoria.llamadas_guardar

    ObtenerTablero(repositorio_en_memoria).ejecutar()

    assert repositorio_en_memoria.llamadas_guardar == contador_guardar_antes


def test_la_consulta_no_modifica_el_dominio(repositorio_en_memoria):
    """
    FEATURE_SPEC_003 AC-02.
    Antes y despues de la consulta, los estados de las tareas deben coincidir.
    """
    t1 = _crear(repositorio_en_memoria, "Tarea uno")
    t2 = _crear(repositorio_en_memoria, "Tarea dos")
    MoverTarea(repositorio_en_memoria).ejecutar(t2.id_tarea, EstadoTarea.DOING)

    snapshot_antes = {
        t.id_tarea: t.estado for t in repositorio_en_memoria.cargar().listar_tareas()
    }
    ObtenerTablero(repositorio_en_memoria).ejecutar()
    snapshot_despues = {
        t.id_tarea: t.estado for t in repositorio_en_memoria.cargar().listar_tareas()
    }

    assert snapshot_antes == snapshot_despues
    # Sanity: las dos tareas siguen ahí con sus estados.
    assert snapshot_despues[t1.id_tarea] is EstadoTarea.TODO
    assert snapshot_despues[t2.id_tarea] is EstadoTarea.DOING


def test_consultar_multiples_veces_no_invoca_guardar(repositorio_en_memoria):
    """Refuerzo de AC-02: ninguna iteración de consulta dispara guardar."""
    _crear(repositorio_en_memoria, "Tarea uno")
    contador_antes = repositorio_en_memoria.llamadas_guardar
    caso_de_uso = ObtenerTablero(repositorio_en_memoria)

    for _ in range(5):
        caso_de_uso.ejecutar()

    assert repositorio_en_memoria.llamadas_guardar == contador_antes


# ---------- AC-03: estructura serializable ----------

def test_la_salida_es_serializable_a_json(repositorio_en_memoria):
    """FEATURE_SPEC_003 AC-03."""
    _crear(repositorio_en_memoria, "Pagar facturas")

    resultado = ObtenerTablero(repositorio_en_memoria).ejecutar()
    # json.dumps lanza si hay tipos no serializables (UUID, Enum, etc.).
    cadena = json.dumps(resultado)
    parseado = json.loads(cadena)

    assert set(parseado.keys()) == {"TODO", "DOING", "DONE"}


def test_cada_tarea_dto_tiene_exactamente_id_titulo_y_estado(repositorio_en_memoria):
    """FEATURE_SPEC_003 AC-03: estructura minima para la UI del PASO 13."""
    _crear(repositorio_en_memoria, "Pagar facturas")

    resultado = ObtenerTablero(repositorio_en_memoria).ejecutar()
    for columna in ("TODO", "DOING", "DONE"):
        for tarea_dto in resultado[columna]:
            assert set(tarea_dto.keys()) == {"id_tarea", "titulo", "estado"}
            assert isinstance(tarea_dto["id_tarea"], str)
            assert isinstance(tarea_dto["titulo"], str)
            assert tarea_dto["estado"] in {"TODO", "DOING", "DONE"}


def test_estado_en_dto_coincide_con_la_columna(repositorio_en_memoria):
    """
    Si una tarea aparece en la columna 'DOING', su campo estado debe ser 'DOING'.
    Garantiza coherencia entre la agrupacion y el contenido.
    """
    t1 = _crear(repositorio_en_memoria, "Tarea uno")
    MoverTarea(repositorio_en_memoria).ejecutar(t1.id_tarea, EstadoTarea.DOING)

    resultado = ObtenerTablero(repositorio_en_memoria).ejecutar()
    for columna, lista in resultado.items():
        for tarea_dto in lista:
            assert tarea_dto["estado"] == columna


# ---------- Inyección y aislamiento ----------

def test_caso_de_uso_recibe_el_repositorio_por_constructor():
    from pruebas.aplicacion.conftest import RepositorioTableroEnMemoria

    repo = RepositorioTableroEnMemoria()
    caso_de_uso = ObtenerTablero(repo)
    assert caso_de_uso._repositorio is repo


def test_modulo_obtener_tablero_no_importa_infraestructura():
    """ARCHITECTURE.md §3."""
    import inspect
    from pathlib import Path

    from src.aplicacion import obtener_tablero as modulo

    contenido = Path(inspect.getfile(modulo)).read_text(encoding="utf-8")
    assert "import src.infraestructura" not in contenido
    assert "from src.infraestructura" not in contenido