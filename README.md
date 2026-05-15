# Tablero Kanban Personal con Límite WIP

## 1. Descripción
Aplicación local para gestionar tareas personales en columnas TODO, DOING y DONE. La regla central es que DOING no puede contener más de tres tareas simultáneas.

## 2. Requisitos
- Python 3.11 o superior.
- Flask 3.x.
- pytest.

## 3. Instalación sugerida
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install flask pytest
```

## 4. Ejecución de pruebas
```bash
python -m pytest
```

## 5. Ejecución de la aplicación
Indicar aquí el comando definido cuando se implemente el adaptador HTTP Flask.

## 6. Validación arquitectónica
El dominio no debe importar Flask, HTTP, JSON, rutas de archivo ni dependencias de infraestructura.

## 7. Trazabilidad
Cada cambio debe estar asociado a un paso de PLAN_ATOMICO.md y a una entrada de BITACORA.md.
