"""
Pruebas del adaptador RepositorioTableroJson.

Cobertura:
  - El adaptador cumple el puerto RepositorioTablero.
  - guardar() crea el archivo JSON con el esquema esperado.
  - cargar() de un archivo inexistente devuelve Tablero vacío
    (FEATURE_SPEC_003 Bloque 4).
  - Round-trip: guardar -> cargar conserva el estado.
  - Un archivo corrupto que viola INV-01 falla en cargar (DEC-04).
  - Compatibilidad con los casos de uso reales (CrearTarea, MoverTarea,
    ObtenerTablero) operando sobre archivos temporales.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.aplicacion.crear_tarea import CrearTarea
from src.aplicacion.mover_tarea import MoverTarea
from src.aplicacion.obtener_tablero import ObtenerTablero
from src.aplicacion.repositorio_tablero import RepositorioTablero
from src.dominio.errores import ErrorLimiteWipExcedido
from src.dominio.estado_tarea import EstadoTarea
from src.dominio.tablero import LIMITE_WIP, Tablero
from src.dominio.tarea import Tarea
from src.infraestructura.persistencia.repositorio_tablero_json import (
    RepositorioTableroJson,
)


# ---------- Fixture local ----------

@pytest.fixture
def ruta_json(tmp_path: Path) -> Path:
    """Ruta a un archivo JSON dentro de un directorio temporal de la prueba."""
    return tmp_path / "tablero.json"


# ---------- Contrato del puerto ----------

def test_es_subclase_y_cumple_el_puerto(ruta_json):
    repo = RepositorioTableroJson(ruta_json)
    assert isinstance(repo, RepositorioTablero)


# ---------- cargar() sobre archivo inexistente ----------

def test_cargar_archivo_inexistente_devuelve_tablero_vacio(ruta_json):
    """FEATURE_SPEC_003 Bloque 4."""
    assert not ruta_json.exists()
    repo = RepositorioTableroJson(ruta_json)
    tablero = repo.cargar()

    assert isinstance(tablero, Tablero)
    assert tablero.listar_tareas() == []


# ---------- guardar() ----------

def test_guardar_crea_archivo_json_con_esquema_esperado(ruta_json):
    repo = RepositorioTableroJson(ruta_json)
    tablero = Tablero()
    tablero.crear_tarea("Pagar facturas")

    repo.guardar(tablero)

    assert ruta_json.exists()
    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    assert datos["version"] == 1
    assert isinstance(datos["tareas"], list)
    assert len(datos["tareas"]) == 1
    tarea_serializada = datos["tareas"][0]
    assert set(tarea_serializada.keys()) == {"id_tarea", "titulo", "estado"}
    assert tarea_serializada["titulo"] == "Pagar facturas"
    assert tarea_serializada["estado"] == "TODO"


def test_guardar_crea_directorios_padre_si_no_existen(tmp_path):
    """
    Si la ruta apunta a un directorio que no existe todavía, el adaptador
    debe crearlo. Util para configuraciones por defecto del PASO 12.
    """
    ruta = tmp_path / "subdir" / "anidado" / "tablero.json"
    repo = RepositorioTableroJson(ruta)
    repo.guardar(Tablero())
    assert ruta.exists()


def test_guardar_sobrescribe_el_archivo_completo(ruta_json):
    """
    Estrategia de escritura: el archivo se reescribe en cada llamada.
    No queremos "fantasmas" de estados anteriores.
    """
    repo = RepositorioTableroJson(ruta_json)
    tablero = Tablero()
    tablero.crear_tarea("Primera")
    repo.guardar(tablero)

    nuevo_tablero = Tablero()
    nuevo_tablero.crear_tarea("Unica que debe quedar")
    repo.guardar(nuevo_tablero)

    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    titulos = [t["titulo"] for t in datos["tareas"]]
    assert titulos == ["Unica que debe quedar"]


# ---------- Round-trip: guardar -> cargar conserva el estado ----------

def test_round_trip_conserva_tareas_e_ids(ruta_json):
    """
    Propiedad clave: lo que se guarda es exactamente lo que se carga.
    Garantiza que la persistencia no pierde ni altera información.
    """
    original = Tablero()
    t1 = original.crear_tarea("Tarea uno")
    t2 = original.crear_tarea("Tarea dos")
    original.mover_tarea(t2.id_tarea, EstadoTarea.DOING)

    repo = RepositorioTableroJson(ruta_json)
    repo.guardar(original)
    cargado = repo.cargar()

    originales = {(t.id_tarea, t.titulo, t.estado) for t in original.listar_tareas()}
    recargados = {(t.id_tarea, t.titulo, t.estado) for t in cargado.listar_tareas()}
    assert originales == recargados
    # Tras un round-trip, t1 sigue en TODO y t2 sigue en DOING.
    estados = {t.id_tarea: t.estado for t in cargado.listar_tareas()}
    assert estados[t1.id_tarea] is EstadoTarea.TODO
    assert estados[t2.id_tarea] is EstadoTarea.DOING


def test_round_trip_de_tablero_vacio(ruta_json):
    """Caso límite: guardar y cargar un tablero vacio."""
    repo = RepositorioTableroJson(ruta_json)
    repo.guardar(Tablero())
    cargado = repo.cargar()
    assert cargado.listar_tareas() == []


# ---------- Archivo corrupto / invariante violada al cargar ----------

def test_cargar_archivo_con_doing_excedido_falla_visible(ruta_json):
    """
    DEC-04: si el JSON declara más de LIMITE_WIP tareas en DOING, el
    constructor del Tablero lanza ErrorLimiteWipExcedido y el adaptador
    NO debe silenciar el error: arrancar en estado inválido es peor que
    fallar al cargar.
    """
    contenido_corrupto = {
        "version": 1,
        "tareas": [
            {"id_tarea": "11111111-1111-1111-1111-111111111111", "titulo": "A", "estado": "DOING"},
            {"id_tarea": "22222222-2222-2222-2222-222222222222", "titulo": "B", "estado": "DOING"},
            {"id_tarea": "33333333-3333-3333-3333-333333333333", "titulo": "C", "estado": "DOING"},
            {"id_tarea": "44444444-4444-4444-4444-444444444444", "titulo": "D", "estado": "DOING"},
        ],
    }
    ruta_json.write_text(json.dumps(contenido_corrupto), encoding="utf-8")
    repo = RepositorioTableroJson(ruta_json)

    with pytest.raises(ErrorLimiteWipExcedido):
        repo.cargar()


# ---------- Integracion con los casos de uso reales ----------

def test_crear_tarea_persiste_en_archivo_json(ruta_json):
    """
    Verifica que la pila completa (caso de uso + adaptador real) funciona:
    una tarea creada queda persistida en disco.
    """
    repo = RepositorioTableroJson(ruta_json)
    caso = CrearTarea(repo)
    tarea = caso.ejecutar("Pagar facturas")

    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    ids = {t["id_tarea"] for t in datos["tareas"]}
    assert str(tarea.id_tarea) in ids


def test_obtener_tablero_sobre_archivo_persistido(ruta_json):
    """
    Tras crear y mover tareas con los casos de uso reales, ObtenerTablero
    devuelve la agrupacion esperada cargando desde disco.
    """
    repo = RepositorioTableroJson(ruta_json)
    crear = CrearTarea(repo)
    mover = MoverTarea(repo)

    t1 = crear.ejecutar("Tarea uno")  # TODO
    t2 = crear.ejecutar("Tarea dos")
    mover.ejecutar(t2.id_tarea, EstadoTarea.DOING)

    # Nuevo adaptador apuntando al mismo archivo: simula reinicio del proceso.
    repo_recargado = RepositorioTableroJson(ruta_json)
    dto = ObtenerTablero(repo_recargado).ejecutar()

    ids_todo = {t["id_tarea"] for t in dto["TODO"]}
    ids_doing = {t["id_tarea"] for t in dto["DOING"]}
    assert str(t1.id_tarea) in ids_todo
    assert str(t2.id_tarea) in ids_doing


def test_wip_se_respeta_a_traves_de_la_persistencia(ruta_json):
    """
    Refuerzo crítico para la rúbrica del profesor:
    la cuarta tarea en DOING se rechaza incluso después de simular un
    reinicio (creando un nuevo adaptador sobre el mismo archivo).
    """
    repo = RepositorioTableroJson(ruta_json)
    crear = CrearTarea(repo)
    mover = MoverTarea(repo)

    # Llenamos DOING al limite (3 tareas).
    for indice in range(LIMITE_WIP):
        tarea = crear.ejecutar(f"Tarea {indice + 1}")
        mover.ejecutar(tarea.id_tarea, EstadoTarea.DOING)

    # Simulamos reinicio.
    repo_recargado = RepositorioTableroJson(ruta_json)
    crear_recargado = CrearTarea(repo_recargado)
    mover_recargado = MoverTarea(repo_recargado)

    cuarta = crear_recargado.ejecutar("Cuarta")
    with pytest.raises(ErrorLimiteWipExcedido):
        mover_recargado.ejecutar(cuarta.id_tarea, EstadoTarea.DOING)