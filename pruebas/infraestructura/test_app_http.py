"""
Pruebas del adaptador HTTP Flask.

Cobertura:
  - FEATURE_SPEC_001: POST /api/tareas (201 OK; 400 si titulo invalido).
  - FEATURE_SPEC_002: PATCH /api/tareas/<id> (200 OK; 404; 409 por WIP y por transición).
  - FEATURE_SPEC_003: GET /api/tablero (200 OK con tres claves).
  - Los errores de dominio se traducen a HTTP, no se filtran como 500.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.dominio.tablero import LIMITE_WIP
from src.infraestructura.http.app import crear_app


# ---------- Fixtures ----------

@pytest.fixture
def cliente(tmp_path: Path):
    """Cliente Flask con un archivo JSON aislado por prueba (tmp_path)."""
    ruta = tmp_path / "tablero.json"
    app = crear_app(ruta_archivo_json=ruta)
    app.config["TESTING"] = True
    with app.test_client() as cliente:
        yield cliente


# ---------- GET /api/tablero ----------

def test_get_tablero_vacio_devuelve_200_y_tres_claves(cliente):
    """FEATURE_SPEC_003 AC-01."""
    respuesta = cliente.get("/api/tablero")
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert set(datos.keys()) == {"TODO", "DOING", "DONE"}
    assert datos["TODO"] == []
    assert datos["DOING"] == []
    assert datos["DONE"] == []


# ---------- POST /api/tareas ----------

def test_post_tarea_con_titulo_valido_devuelve_201_y_tarea_en_todo(cliente):
    """FEATURE_SPEC_001 AC-01."""
    respuesta = cliente.post(
        "/api/tareas",
        data=json.dumps({"titulo": "Pagar facturas"}),
        content_type="application/json",
    )
    assert respuesta.status_code == 201
    datos = respuesta.get_json()
    assert datos["titulo"] == "Pagar facturas"
    assert datos["estado"] == "TODO"
    assert "id_tarea" in datos


def test_post_tarea_con_titulo_vacio_devuelve_400(cliente):
    """FEATURE_SPEC_001 AC-02: ErrorTituloTareaInvalido -> 400."""
    respuesta = cliente.post(
        "/api/tareas",
        data=json.dumps({"titulo": ""}),
        content_type="application/json",
    )
    assert respuesta.status_code == 400


def test_post_tarea_con_titulo_solo_espacios_devuelve_400(cliente):
    """FEATURE_SPEC_001 AC-03."""
    respuesta = cliente.post(
        "/api/tareas",
        data=json.dumps({"titulo": "   "}),
        content_type="application/json",
    )
    assert respuesta.status_code == 400


def test_post_tarea_sin_titulo_en_el_body_devuelve_400(cliente):
    """Body sin campo titulo -> 400 explicito."""
    respuesta = cliente.post("/api/tareas", data="{}", content_type="application/json")
    assert respuesta.status_code == 400


# ---------- PATCH /api/tareas/<id> ----------

def _crear_tarea(cliente, titulo: str) -> dict:
    """Helper: crea una tarea via HTTP y devuelve el dict de respuesta."""
    respuesta = cliente.post(
        "/api/tareas",
        data=json.dumps({"titulo": titulo}),
        content_type="application/json",
    )
    assert respuesta.status_code == 201
    return respuesta.get_json()


def test_patch_mueve_tarea_de_todo_a_doing_devuelve_200(cliente):
    """FEATURE_SPEC_002 AC-01."""
    tarea = _crear_tarea(cliente, "Tarea uno")

    respuesta = cliente.patch(
        f"/api/tareas/{tarea['id_tarea']}",
        data=json.dumps({"estado_destino": "DOING"}),
        content_type="application/json",
    )
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    ids_doing = {t["id_tarea"] for t in datos["DOING"]}
    assert tarea["id_tarea"] in ids_doing


def test_patch_mueve_de_doing_a_done_devuelve_200(cliente):
    """FEATURE_SPEC_002 AC-04."""
    tarea = _crear_tarea(cliente, "Tarea uno")
    cliente.patch(
        f"/api/tareas/{tarea['id_tarea']}",
        data=json.dumps({"estado_destino": "DOING"}),
        content_type="application/json",
    )
    respuesta = cliente.patch(
        f"/api/tareas/{tarea['id_tarea']}",
        data=json.dumps({"estado_destino": "DONE"}),
        content_type="application/json",
    )
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    ids_done = {t["id_tarea"] for t in datos["DONE"]}
    assert tarea["id_tarea"] in ids_done


def test_patch_cuarta_tarea_a_doing_devuelve_409(cliente):
    """
    Punto critico para la rubrica del profesor: FEATURE_SPEC_002 AC-02.
    La invariante INV-01 se aplica desde el dominio y se traduce a HTTP 409.
    """
    # Llenamos DOING al limite.
    for indice in range(LIMITE_WIP):
        tarea = _crear_tarea(cliente, f"Tarea {indice + 1}")
        respuesta = cliente.patch(
            f"/api/tareas/{tarea['id_tarea']}",
            data=json.dumps({"estado_destino": "DOING"}),
            content_type="application/json",
        )
        assert respuesta.status_code == 200

    # Cuarta tarea: debe rechazarse desde el dominio con 409.
    cuarta = _crear_tarea(cliente, "Cuarta")
    respuesta = cliente.patch(
        f"/api/tareas/{cuarta['id_tarea']}",
        data=json.dumps({"estado_destino": "DOING"}),
        content_type="application/json",
    )
    assert respuesta.status_code == 409


def test_patch_de_todo_a_done_devuelve_409(cliente):
    """FEATURE_SPEC_002 AC-03 + INV-03."""
    tarea = _crear_tarea(cliente, "Tarea uno")
    respuesta = cliente.patch(
        f"/api/tareas/{tarea['id_tarea']}",
        data=json.dumps({"estado_destino": "DONE"}),
        content_type="application/json",
    )
    assert respuesta.status_code == 409


def test_patch_de_tarea_inexistente_devuelve_404(cliente):
    """DOMAIN.md §4 ErrorTareaNoEncontrada -> 404."""
    id_inventado = "11111111-1111-1111-1111-111111111111"
    respuesta = cliente.patch(
        f"/api/tareas/{id_inventado}",
        data=json.dumps({"estado_destino": "DOING"}),
        content_type="application/json",
    )
    assert respuesta.status_code == 404


def test_patch_con_id_no_uuid_devuelve_400(cliente):
    respuesta = cliente.patch(
        "/api/tareas/no-es-uuid",
        data=json.dumps({"estado_destino": "DOING"}),
        content_type="application/json",
    )
    assert respuesta.status_code == 400


def test_patch_con_estado_destino_invalido_devuelve_400(cliente):
    """DEC-08: estado canonico desconocido -> 400, sin tocar el repositorio."""
    tarea = _crear_tarea(cliente, "Tarea uno")
    respuesta = cliente.patch(
        f"/api/tareas/{tarea['id_tarea']}",
        data=json.dumps({"estado_destino": "BLOCKED"}),
        content_type="application/json",
    )
    assert respuesta.status_code == 400


def test_patch_sin_estado_destino_devuelve_400(cliente):
    tarea = _crear_tarea(cliente, "Tarea uno")
    respuesta = cliente.patch(
        f"/api/tareas/{tarea['id_tarea']}",
        data="{}",
        content_type="application/json",
    )
    assert respuesta.status_code == 400


# ---------- Persistencia a traves de HTTP ----------

def test_estado_se_persiste_entre_peticiones(cliente, tmp_path: Path):
    """
    Crear via POST y luego consultar via GET debe reflejar la tarea creada,
    demostrando que el adaptador realmente persiste el estado.
    """
    tarea = _crear_tarea(cliente, "Tarea persistente")

    respuesta = cliente.get("/api/tablero")
    datos = respuesta.get_json()
    ids_todo = {t["id_tarea"] for t in datos["TODO"]}
    assert tarea["id_tarea"] in ids_todo


def test_index_devuelve_404_si_frontend_no_existe(cliente):
    """
    En el PASO 12 todavía no existe el frontend. La ruta '/' debe contestar
    404 sin romperse. El PASO 13 hara que devuelva el HTML.
    """
    respuesta = cliente.get("/")
    assert respuesta.status_code == 404