"""
Verificación arquitectónica del dominio.

Referencia:
  - ARCHITECTURE.md §1 (el dominio no conoce Flask, HTTP, JSON, archivos, etc.).
  - ARCHITECTURE.md §3 (reglas de dependencia: el dominio no importa de aplicación
    ni de infraestructura).
  - ARCHITECTURE.md §6 (verificación arquitectónica mínima).
  - TECH_CONSTRAINTS.md §2 (prohibiciones).

Estas pruebas reemplazan el grep manual de ARCHITECTURE.md §6 por una verificación
automatizada que corre con el resto del suite. Si fallan, hay deriva arquitectónica.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


# ---------- Configuración ----------

# Raíz del proyecto: este archivo vive en pruebas/arquitectura/, así que dos
# parents nos llevan a la raíz del repositorio.
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent
_DIR_DOMINIO = RAIZ_PROYECTO / "src" / "dominio"

# Módulos PROHIBIDOS en el dominio (TECH_CONSTRAINTS.md §2 + ARCHITECTURE.md §1).
# El dominio solo debe depender de la biblioteca estándar de Python.
_MODULOS_PROHIBIDOS = frozenset({
    "flask",
    "json",
    "requests",
    "sqlalchemy",
    "http",
    "httpx",
    "urllib",      # E/S de red
    "urllib3",
    "aiohttp",
    "starlette",
    "fastapi",
    "django",
    "pydantic",    # validación externa; INV-04 se valida con código propio
    "sqlite3",     # cualquier acceso a DB en el dominio es una violación
})

# Paquetes propios prohibidos en el dominio (ARCHITECTURE.md §3:
# src/dominio/ no importa src/aplicacion/ ni src/infraestructura/).
_PAQUETES_INTERNOS_PROHIBIDOS = frozenset({
    "src.aplicacion",
    "src.infraestructura",
})


# ---------- Helpers ----------

def _archivos_python_del_dominio() -> list[Path]:
    """Devuelve todos los archivos .py bajo src/dominio/, excluyendo _pycache_."""
    return [
        p for p in _DIR_DOMINIO.rglob("*.py")
        if "_pycache_" not in p.parts
    ]


def _imports_de(archivo: Path) -> list[str]:
    """
    Extrae los nombres de módulo de todos los import X y from X import Y
    de un archivo Python usando AST (no ejecuta el código).
    """
    arbol = ast.parse(archivo.read_text(encoding="utf-8"), filename=str(archivo))
    nombres: list[str] = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                nombres.append(alias.name)
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.module is not None:
                nombres.append(nodo.module)
    return nombres


def _modulo_raiz(nombre_modulo: str) -> str:
    """Devuelve la primera parte del nombre puntuado: 'http.client' -> 'http'."""
    return nombre_modulo.split(".", 1)[0]


# ---------- Pruebas ----------

def test_existe_el_directorio_de_dominio():
    """Sanity check: el directorio src/dominio/ debe existir."""
    assert _DIR_DOMINIO.is_dir(), f"No se encuentra el directorio {_DIR_DOMINIO}"


def test_el_dominio_tiene_al_menos_un_archivo_python():
    """Si el dominio está vacío, las verificaciones siguientes carecen de sentido."""
    archivos = _archivos_python_del_dominio()
    # Excluimos _init_.py vacío del conteo significativo.
    archivos_con_contenido = [
        p for p in archivos if p.name != "_init_.py" or p.stat().st_size > 0
    ]
    assert archivos_con_contenido, (
        "Se esperaba al menos un módulo de dominio (estado_tarea, errores, tarea, tablero)."
    )


@pytest.mark.parametrize("archivo", _archivos_python_del_dominio(), ids=lambda p: p.name)
def test_archivo_de_dominio_no_importa_modulos_prohibidos(archivo: Path):
    """
    ARCHITECTURE.md §1, §6 / TECH_CONSTRAINTS.md §2.
    Ningún archivo del dominio puede importar Flask, json, requests, sqlalchemy,
    http ni equivalentes. El dominio solo usa stdlib pura (enum, dataclasses, uuid, typing).
    """
    nombres = _imports_de(archivo)
    encontrados = sorted({
        nombre for nombre in nombres
        if _modulo_raiz(nombre) in _MODULOS_PROHIBIDOS
    })
    assert not encontrados, (
        f"Violacion arquitectonica en {archivo.relative_to(_RAIZ_PROYECTO)}: "
        f"el dominio importa modulos prohibidos {encontrados}. "
        f"Mover esa dependencia a src/infraestructura/ (ARCHITECTURE.md §5)."
    )


@pytest.mark.parametrize("archivo", _archivos_python_del_dominio(), ids=lambda p: p.name)
def test_archivo_de_dominio_no_importa_aplicacion_ni_infraestructura(archivo: Path):
    """
    ARCHITECTURE.md §3: las dependencias apuntan hacia el núcleo, no hacia afuera.
    El dominio no puede importar de src.aplicacion ni de src.infraestructura.
    """
    nombres = _imports_de(archivo)
    encontrados = sorted({
        nombre for nombre in nombres
        if any(nombre == prohibido or nombre.startswith(prohibido + ".")
               for prohibido in _PAQUETES_INTERNOS_PROHIBIDOS)
    })
    assert not encontrados, (
        f"Violacion de la regla de dependencia en "
        f"{archivo.relative_to(_RAIZ_PROYECTO)}: importa {encontrados}. "
        f"El dominio solo puede importar de la stdlib o de otros modulos de src.dominio."
    )


def test_imports_relativos_del_dominio_solo_apuntan_a_dominio():
    """
    Refuerzo de ARCHITECTURE.md §3.
    Si un archivo de dominio usa from src...import, el origen debe ser src.dominio.
    """
    violaciones: list[tuple[Path, str]] = []
    for archivo in _archivos_python_del_dominio():
        for nombre in _imports_de(archivo):
            if nombre.startswith("src.") and not nombre.startswith("src.dominio"):
                violaciones.append((archivo.relative_to(_RAIZ_PROYECTO), nombre))
    assert not violaciones, (
        "Los siguientes imports de dominio salen del paquete src.dominio: "
        + ", ".join(f"{a} -> {m}" for a, m in violaciones)
    )