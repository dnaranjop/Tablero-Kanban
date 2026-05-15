"""
Adaptador HTTP Flask.

Referencia:
  - ARCHITECTURE.md §5 (adaptador HTTP en src/infraestructura/http/).
  - TECH_CONSTRAINTS.md §1 (Flask 3.x).
  - FEATURE_SPEC_001, FEATURE_SPEC_002, FEATURE_SPEC_003.
  - DEC-01 (ErrorDominio como raiz para mapeo uniforme de errores).
  - DEC-08 (MoverTarea acepta string canonico como estado destino).

Este modulo es un ADAPTADOR: traduce HTTP <-> casos de uso. No contiene logica
de negocio. Cada endpoint:
  1. Parsea el request (body JSON o parametros de ruta).
  2. Instancia el caso de uso con un RepositorioTablero concreto.
  3. Invoca caso_de_uso.ejecutar(...).
  4. Mapea la salida o el error a una respuesta HTTP.

La ruta del archivo JSON se determina al construir la app via crear_app,
no se hardcodea aqui (DEC-11).
"""

from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from flask import Flask, jsonify, request, send_from_directory

from src.aplicacion.crear_tarea import CrearTarea
from src.aplicacion.mover_tarea import MoverTarea
from src.aplicacion.obtener_tablero import ObtenerTablero
from src.dominio.errores import (
    ErrorDominio,
    ErrorLimiteWipExcedido,
    ErrorTareaNoEncontrada,
    ErrorTituloTareaInvalido,
    ErrorTransicionInvalida,
)
from src.infraestructura.persistencia.repositorio_tablero_json import (
    RepositorioTableroJson,
)


# Mapeo de errores de dominio -> codigos HTTP (DEC-01).
_MAPA_ERROR_HTTP: dict[type[ErrorDominio], int] = {
    ErrorTituloTareaInvalido: 400,
    ErrorTareaNoEncontrada: 404,
    ErrorTransicionInvalida: 409,
    ErrorLimiteWipExcedido: 409,
}


def crear_app(ruta_archivo_json: str | Path | None = None) -> Flask:
    """
    Factoria de la aplicacion Flask.

    Permite inyectar la ruta del archivo JSON, especialmente util en pruebas
    (donde se usa tmp_path) y en produccion (variable de entorno
    TABLERO_RUTA_JSON, con fallback a un archivo local 'tablero.json').

    Parametros:
        ruta_archivo_json: ruta del archivo JSON usado por el adaptador de
            persistencia. Si es None, se lee de la variable de entorno
            TABLERO_RUTA_JSON; si tampoco esta, se usa './tablero.json'.
    """
    app = Flask(__name__)

    ruta = _resolver_ruta(ruta_archivo_json)
    app.config["TABLERO_RUTA_JSON"] = str(ruta)

    @app.get("/api/tablero")
    def obtener_tablero():
        """FEATURE_SPEC_003: consulta del tablero agrupado."""
        repositorio = RepositorioTableroJson(app.config["TABLERO_RUTA_JSON"])
        dto = ObtenerTablero(repositorio).ejecutar()
        return jsonify(dto), 200

    @app.post("/api/tareas")
    def crear_tarea():
        """FEATURE_SPEC_001: crear una tarea nueva."""
        cuerpo = request.get_json(silent=True) or {}
        titulo = cuerpo.get("titulo")
        if titulo is None:
            return _respuesta_error("titulo es obligatorio", 400)

        repositorio = RepositorioTableroJson(app.config["TABLERO_RUTA_JSON"])
        caso_de_uso = CrearTarea(repositorio)
        tarea = caso_de_uso.ejecutar(titulo)

        return jsonify({
            "id_tarea": str(tarea.id_tarea),
            "titulo": tarea.titulo,
            "estado": tarea.estado.name,
        }), 201

    @app.patch("/api/tareas/<id_tarea>")
    def mover_tarea(id_tarea: str):
        """FEATURE_SPEC_002: mover una tarea a otro estado."""
        try:
            id_uuid = UUID(id_tarea)
        except ValueError:
            return _respuesta_error("id_tarea no es un UUID valido", 400)

        cuerpo = request.get_json(silent=True) or {}
        estado_destino = cuerpo.get("estado_destino")
        if not isinstance(estado_destino, str):
            return _respuesta_error("estado_destino es obligatorio (TODO|DOING|DONE)", 400)

        repositorio = RepositorioTableroJson(app.config["TABLERO_RUTA_JSON"])
        caso_de_uso = MoverTarea(repositorio)
        try:
            caso_de_uso.ejecutar(id_uuid, estado_destino)
        except ValueError:
            # Estado destino canónico desconocido (p.ej. 'BLOCKED'); ver DEC-08.
            return _respuesta_error(
                "estado_destino debe ser uno de TODO, DOING, DONE", 400
            )

        # Tras un movimiento exitoso devolvemos el tablero completo (UI lo necesita).
        dto = ObtenerTablero(repositorio).ejecutar()
        return jsonify(dto), 200

    # ---------- Frontend estatico (PASO 13) ----------
    # El frontend Vanilla se sirve desde src/infraestructura/frontend/.
    # Si los archivos aun no existen (situacion durante el PASO 12), las
    # rutas devuelven 404; el PASO 13 los crea sin tocar este archivo.

    _DIR_FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

    @app.get("/")
    def index():
        if not (_DIR_FRONTEND / "index.html").exists():
            return _respuesta_error("frontend no instalado todavia", 404)
        return send_from_directory(_DIR_FRONTEND, "index.html")

    @app.get("/<path:archivo>")
    def estatico(archivo: str):
        ruta_completa = _DIR_FRONTEND / archivo
        if not ruta_completa.exists():
            return _respuesta_error("recurso no encontrado", 404)
        return send_from_directory(_DIR_FRONTEND, archivo)

    # ---------- Manejadores uniformes de errores de dominio ----------

    @app.errorhandler(ErrorDominio)
    def manejar_error_de_dominio(exc: ErrorDominio):
        """
        DEC-01: cualquier ErrorDominio se mapea a un codigo HTTP segun
        _MAPA_ERROR_HTTP. Esto evita que un error de negocio se filtre como 500.
        """
        codigo = _MAPA_ERROR_HTTP.get(type(exc), 409)
        return _respuesta_error(str(exc) or type(exc).__name__, codigo)

    return app


# ---------- Helpers internos ----------

def _resolver_ruta(ruta_archivo_json: str | Path | None) -> Path:
    if ruta_archivo_json is not None:
        return Path(ruta_archivo_json)
    desde_env = os.environ.get("TABLERO_RUTA_JSON")
    if desde_env:
        return Path(desde_env)
    return Path("tablero.json")


def _respuesta_error(mensaje: str, codigo: int):
    return jsonify({"error": mensaje}), codigo


# Instancia por defecto para ejecucion directa (flask run).
app = crear_app()