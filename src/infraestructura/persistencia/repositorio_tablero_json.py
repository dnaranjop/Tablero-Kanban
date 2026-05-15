"""
Adaptador de persistencia JSON: RepositorioTableroJson.

Referencia:
  - ARCHITECTURE.md §4 (contrato del puerto RepositorioTablero).
  - ARCHITECTURE.md §5 (adaptador en src/infraestructura/persistencia/).
  - TECH_CONSTRAINTS.md §1 (persistencia JSON usando biblioteca estándar).
  - FEATURE_SPEC_003 Bloque 4 (archivo inexistente -> tablero vacío).
  - DEC-04 (constructor del Tablero rechaza estado inicial invalido).

Este modulo es un ADAPTADOR: traduce entre el modelo de dominio (Tablero, Tarea,
EstadoTarea) y el formato persistente (JSON). No contiene logica de negocio.

Formato del archivo JSON:
{
    "version": 1,
    "tareas": [
        {"id_tarea": "<uuid>", "titulo": "...", "estado": "TODO|DOING|DONE"},
        ...
    ]
}
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from src.aplicacion.repositorio_tablero import RepositorioTablero
from src.dominio.estado_tarea import EstadoTarea
from src.dominio.tablero import Tablero
from src.dominio.tarea import Tarea


# Version del esquema persistente; permite evoluciones futuras sin romper archivos viejos.
_VERSION_ESQUEMA: int = 1


class RepositorioTableroJson(RepositorioTablero):
    """
    Adaptador concreto del puerto RepositorioTablero.

    Persiste el Tablero en un archivo JSON local cuya ruta se inyecta por
    constructor. NO hardcodea la ruta (TECH_CONSTRAINTS.md §2).
    """

    def __init__(self, ruta_archivo: str | Path) -> None:
        self._ruta = Path(ruta_archivo)

    @property
    def ruta(self) -> Path:
        """Ruta absoluta/relativa del archivo JSON usado por este adaptador."""
        return self._ruta

    # ---------- Contrato del puerto ----------

    def cargar(self) -> Tablero:
        """
        Devuelve el Tablero persistido. Si el archivo no existe, devuelve un
        Tablero vacío (FEATURE_SPEC_003 Bloque 4).

        Si el archivo existe pero su contenido produce un Tablero que viola
        INV-01 (más de LIMITE_WIP tareas en DOING), el constructor del
        Tablero (DEC-04) lanza ErrorLimiteWipExcedido. No lo silenciamos:
        un archivo corrupto debe fallar visible.
        """
        if not self._ruta.exists():
            return Tablero()

        contenido = self._ruta.read_text(encoding="utf-8")
        datos = json.loads(contenido)
        tareas = self._reconstruir_tareas(datos)
        return Tablero(tareas=tareas)

    def guardar(self, tablero: Tablero) -> None:
        """
        Persiste el estado completo del tablero como JSON.

        Estrategia: escritura completa (no append). Cada llamada reescribe el
        archivo. Apropiado para un sistema personal local de pocas tareas.
        """
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        datos = self._serializar(tablero)
        self._ruta.write_text(
            json.dumps(datos, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ---------- Serializacion / deserializacion ----------

    @staticmethod
    def _serializar(tablero: Tablero) -> dict:
        return {
            "version": _VERSION_ESQUEMA,
            "tareas": [
                {
                    "id_tarea": str(tarea.id_tarea),
                    "titulo": tarea.titulo,
                    "estado": tarea.estado.name,
                }
                for tarea in tablero.listar_tareas()
            ],
        }

    @staticmethod
    def _reconstruir_tareas(datos: dict) -> list[Tarea]:
        tareas_raw = datos.get("tareas", [])
        tareas: list[Tarea] = []
        for item in tareas_raw:
            tarea = Tarea(
                id_tarea=UUID(item["id_tarea"]),
                titulo=item["titulo"],
                estado=EstadoTarea[item["estado"]],
            )
            tareas.append(tarea)
        return tareas