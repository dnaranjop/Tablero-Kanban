"""
Pruebas del frontend servido por Flask.

Cobertura:
  - Los tres archivos estaticos (index.html, estilos.css, app.js) se sirven
    correctamente bajo las rutas raiz y subruta.
  - El contenido HTML expone las tres columnas TODO, DOING, DONE.
  - El JavaScript NO duplica la regla WIP (CONTEXT.md §7, mitigación clave).
  - El JavaScript NO importa frameworks externos (TECH_CONSTRAINTS.md §2).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.infraestructura.http.app import crear_app


# ---------- Fixtures ----------

@pytest.fixture
def cliente(tmp_path: Path):
    app = crear_app(ruta_archivo_json=tmp_path / "tablero.json")
    app.config["TESTING"] = True
    with app.test_client() as cliente:
        yield cliente


# ---------- Servicio de archivos estaticos ----------

def test_get_index_devuelve_200_y_html(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_data(as_text=True)
    assert "<!DOCTYPE html>" in cuerpo
    assert "Tablero Kanban Personal" in cuerpo


def test_get_index_expone_las_tres_columnas(cliente):
    """FEATURE_SPEC_003 AC-03 a nivel de UI."""
    cuerpo = cliente.get("/").get_data(as_text=True)
    for estado in ("TODO", "DOING", "DONE"):
        assert f'data-estado="{estado}"' in cuerpo, (
            f"La columna {estado} no aparece en index.html"
        )


def test_get_estilos_css_devuelve_200(cliente):
    respuesta = cliente.get("/estilos.css")
    assert respuesta.status_code == 200
    assert ".tablero" in respuesta.get_data(as_text=True)


def test_get_app_js_devuelve_200(cliente):
    respuesta = cliente.get("/app.js")
    assert respuesta.status_code == 200
    assert "fetch(" in respuesta.get_data(as_text=True)


def test_archivo_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/no-existe.html")
    assert respuesta.status_code == 404


# ---------- CONTEXT.md §7: WIP NO vive solo en interfaz ----------

def test_javascript_no_duplica_la_regla_wip():
    """
    Mitigación documentada en CONTEXT.md §7: la regla WIP debe vivir en el
    dominio. Si el frontend tuviera una condición como length >= 3 o
    >= LIMITE_WIP, estaría replicando la invariante y violando la guía.

    Esta prueba abre el archivo app.js como texto y busca patrones sospechosos.
    No es una prueba absoluta (alguien podría escribir la regla de otra forma),
    pero detecta los errores más comunes de copilotos / IA generadora.
    """
    raiz = Path(__file__).resolve().parent.parent.parent
    ruta_js = raiz / "src" / "infraestructura" / "frontend" / "app.js"
    contenido = ruta_js.read_text(encoding="utf-8")

    patrones_prohibidos = [
        ">= 3",
        "> 3",
        ">=3",
        ">3",
        "LIMITE_WIP",
        "limite_wip",
        "limiteWip",
        "WIP_LIMIT",
    ]
    encontrados = [p for p in patrones_prohibidos if p in contenido]
    assert not encontrados, (
        f"app.js contiene patrones que sugieren validacion WIP en cliente: "
        f"{encontrados}. CONTEXT.md §7 prohibe que la regla viva solo en interfaz."
    )


def test_javascript_no_importa_frameworks_externos():
    """
    TECH_CONSTRAINTS.md §2: no usar React, Vue, Angular, jQuery, etc.
    Verificamos que no aparecen referencias a esos paquetes.
    """
    raiz = Path(__file__).resolve().parent.parent.parent
    ruta_js = raiz / "src" / "infraestructura" / "frontend" / "app.js"
    contenido = ruta_js.read_text(encoding="utf-8").lower()

    prohibidos = ["react", "vue", "angular", "jquery", "$(", "tailwind", "bootstrap"]
    encontrados = [p for p in prohibidos if p in contenido]
    assert not encontrados, f"app.js menciona frameworks prohibidos: {encontrados}"


def test_html_no_carga_frameworks_externos_por_cdn():
    """
    Algunos errores comunes: cargar React, Vue o Bootstrap desde un CDN
    via <script src="https://cdn..."> o <link href="https://cdn...">.
    """
    raiz = Path(__file__).resolve().parent.parent.parent
    ruta_html = raiz / "src" / "infraestructura" / "frontend" / "index.html"
    contenido = ruta_html.read_text(encoding="utf-8").lower()

    prohibidos = ["react", "vue", "angular", "jquery", "tailwind", "bootstrap"]
    encontrados = [p for p in prohibidos if p in contenido]
    assert not encontrados, f"index.html referencia frameworks prohibidos: {encontrados}"