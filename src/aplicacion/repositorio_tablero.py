"""
Puerto abstracto RepositorioTablero.

Referencia: ARCHITECTURE.md §3 (reglas de dependencia) y §4 (contrato del puerto).
GLOSSARY.md: un Puerto es una interfaz definida por la capa de aplicacion para
comunicarse con el exterior sin depender de una tecnología concreta.

Este modulo SOLO depende de:
  - abc (stdlib)
  - src.dominio.tablero (capa interna)

No conoce JSON, archivos, Flask ni ningún detalle de infraestructura.
Cualquier import fuera de stdlib o src.dominio viola ARCHITECTURE.md §3.

La implementación concreta (basada en archivo JSON local) se introduce en el
PASO 11 como adaptador en src/infraestructura/persistencia/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.dominio.tablero import Tablero


class RepositorioTablero(ABC):
    """
    Contrato de persistencia del Tablero (ARCHITECTURE.md §4).

    Los casos de uso (CrearTarea, MoverTarea, ObtenerTablero) reciben una
    instancia de un subtipo concreto de este puerto por inyección de
    dependencia (constructor). De esta forma, la aplicación nunca conoce
    el mecanismo real de almacenamiento.
    """

    @abstractmethod
    def cargar(self) -> Tablero:
        """
        Devuelve el Tablero persistido.

        Si no existe almacenamiento previo, el adaptador debe devolver un
        Tablero vacío (FEATURE_SPEC_003 Bloque 4: 'Si el archivo JSON no
        existe, infraestructura puede inicializar un tablero vacio').
        """

    @abstractmethod
    def guardar(self, tablero: Tablero) -> None:
        """
        Persiste el estado actual del Tablero.

        Debe ser invocado únicamente por los casos de uso de escritura tras
        una operación de dominio exitosa (FEATURE_SPEC_001 AC-04, FEATURE_SPEC_002 AC-05).
        Las consultas (FEATURE_SPEC_003) NO deben invocar este metodo.
        """