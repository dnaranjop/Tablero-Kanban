"""
Entidad Tarea.

Referencia: DOMAIN.md §1 (campos), §6 (nomenclatura) / INV-04 (título obligatorio).
GLOSSARY.md: Tarea = unidad de trabajo con id_tarea, titulo y estado.

Solo usa stdlib (uuid, dataclasses). No importa nada de aplicacion ni de
infraestructura. Cualquier campo adicional viola TECH_CONSTRAINTS.md §2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.dominio.errores import ErrorTituloTareaInvalido
from src.dominio.estado_tarea import EstadoTarea


@dataclass
class Tarea:
    """
    Unidad de trabajo del tablero Kanban.

    Atributos (DOMAIN.md §1, los únicos permitidos):
        id_tarea: identificador único, generado por la aplicación.
        titulo: texto no vacío, validado por INV-04.
        estado: instancia de EstadoTarea; por defecto TODO.
    """

    id_tarea: UUID = field(default_factory=uuid4)
    titulo: str = ""
    estado: EstadoTarea = EstadoTarea.TODO

    def __post_init__(self) -> None:
        """Refuerza INV-04 en el momento de construir la Tarea."""
        self._validar_titulo(self.titulo)

    @staticmethod
    def _validar_titulo(titulo: str) -> None:
        """
        INV-04: el título no puede ser vacío ni componerse solo de espacios.
        FEATURE_SPEC_001 AC-02, AC-03.
        """
        if not isinstance(titulo, str) or titulo.strip() == "":
            raise ErrorTituloTareaInvalido(
                "El titulo es obligatorio y no puede estar vacio ni contener solo espacios."
            )

    def cambiar_estado(self, nuevo_estado: EstadoTarea) -> None:
        """
        Cambia el estado interno de la Tarea.

        Nota arquitectónica importante:
        este método NO valida transiciones ni el límite WIP. Esas son
        responsabilidades del aggregate root Tablero (DOMAIN.md §2, §5;
        INV-01, INV-02, INV-03), que se implementará en el PASO 5.
        Esta operación debe invocarse únicamente desde Tablero.
        """
        if not isinstance(nuevo_estado, EstadoTarea):
            raise TypeError("nuevo_estado debe ser una instancia de EstadoTarea.")
        self.estado = nuevo_estado