# Tablero Kanban Personal con Límite WIP

Aplicación local para gestionar tareas personales en columnas TODO, DOING y DONE.
La regla central es que *DOING no puede contener más de tres tareas simultáneas*
(invariante INV-01, definida en context/DOMAIN.md).

Implementado siguiendo la metodología del laboratorio:
*el paquete de contexto manda; la IA propone un plan; el estudiante autoriza paso a paso.*
La trazabilidad completa vive en plan/PLAN_ATOMICO.md y BITACORA.md.

---

## 1. Requisitos previos

- Python 3.11 o superior (probado con 3.13).
- Git.
- Sistema operativo: Windows con PowerShell (los comandos de esta guía).
  En Linux/macOS los equivalentes en bash son evidentes (source .venv/bin/activate
  en lugar de Activate.ps1).

## 2. Instalación

Desde la carpeta raíz del proyecto (tablero-kanban/):

powershell
# Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Si PowerShell rechaza la activación con un error de permisos:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Instalar dependencias (solo dos, conforme a TECH_CONSTRAINTS.md §1)
python -m pip install flask pytest


Tras la activación verás (.venv) al inicio del prompt.

## 3. Ejecutar las pruebas automatizadas

powershell
python -m pytest -v


Resultado esperado: aproximadamente 143 pruebas, todas en verde.

Para ejecutar solo un grupo:

powershell
# Solo el dominio (debe correr en milisegundos)
python -m pytest pruebas/dominio -v

# Solo la aplicación (casos de uso)
python -m pytest pruebas/aplicacion -v

# Solo la infraestructura (persistencia JSON, HTTP, frontend servido)
python -m pytest pruebas/infraestructura -v

# Solo la verificación arquitectónica (que el dominio no se contamina)
python -m pytest pruebas/arquitectura -v


## 4. Levantar la aplicación

powershell
$env:FLASK_APP = "src.infraestructura.http.app"
flask run


Abre el navegador en *http://127.0.0.1:5000/*.

Para detener el servidor: Ctrl + C en la terminal donde corre Flask.

### Variables de entorno opcionales

| Variable | Por defecto | Descripción |
|---|---|---|
| TABLERO_RUTA_JSON | ./tablero.json | Ruta del archivo donde se persiste el tablero. |

Ejemplo:

powershell
$env:TABLERO_RUTA_JSON = "C:\Temp\mi_tablero.json"
flask run


## 5. Cómo probar manualmente las invariantes

Una vez que la app esté corriendo en http://127.0.0.1:5000/:

1. *Crear tarea con título válido* → escribe "Comprar pan" → aparece en TODO.
2. *Crear con título vacío* → mensaje de error en rojo (HTTP 400 desde el backend; INV-04).
3. *Mover TODO → DOING* → clic en "Mover a DOING".
4. *Llenar DOING con tres tareas* → crear tres tareas y moverlas todas a DOING.
5. *Cuarta tarea en DOING (clave para evaluar INV-01)* → crear una cuarta y moverla a DOING.
   La operación se rechaza con un mensaje de error en rojo. Abre las DevTools del navegador (F12) → pestaña *Network* → la petición PATCH /api/tareas/... debe responder con *409*. Eso demuestra que la regla vive en el dominio y no en JavaScript.
6. *Mover DOING → DONE* → clic en "Mover a DONE".
7. *Persistencia* → detener Flask con Ctrl+C, volver a arrancarlo, refrescar la página. Las tareas siguen ahí (tablero.json en la raíz del proyecto).

## 6. Endpoints HTTP

| Método | Ruta | Descripción |
|---|---|---|
| GET   | /api/tablero         | Devuelve {TODO: [...], DOING: [...], DONE: [...]}. |
| POST  | /api/tareas          | Crea una tarea. Body: {"titulo": "..."}. 201 OK; 400 si título inválido. |
| PATCH | /api/tareas/<id>     | Mueve la tarea. Body: {"estado_destino": "DOING" | "DONE"}. 200 OK; 404 si no existe; 409 si WIP excedido o transición inválida. |

Probar desde la terminal:

powershell
# Crear
curl -X POST http://127.0.0.1:5000/api/tareas -H "Content-Type: application/json" -d '{\"titulo\": \"Probar API\"}'

# Consultar
curl http://127.0.0.1:5000/api/tablero


## 7. Verificación arquitectónica

ARCHITECTURE.md §6 exige que el dominio no importe Flask, HTTP, JSON ni dependencias de infraestructura.

Verificación manual con grep:

powershell
Get-ChildItem .\src\dominio -Recurse -Filter *.py | Select-String -Pattern "flask|json|requests|sqlalchemy|http"


Resultado esperado: sin coincidencias.

Verificación automatizada (parte de la suite de pruebas):

powershell
python -m pytest pruebas/arquitectura -v

## 8. Estructura del proyecto

tablero-kanban/
├── context/                        # Paquete de contexto (fuente de verdad)
│   ├── CONTEXT.md
│   ├── DOMAIN.md                   # Lenguaje ubicuo + invariantes INV-01..05
│   ├── ARCHITECTURE.md
│   ├── TECH_CONSTRAINTS.md
│   └── GLOSSARY.md
├── specs/                          # Una FEATURE_SPEC por caso de uso
│   ├── FEATURE_SPEC_001_crear_tarea.md
│   ├── FEATURE_SPEC_002_mover_tarea.md
│   └── FEATURE_SPEC_003_obtener_tablero.md
├── plan/
│   └── PLAN_ATOMICO.md             # Plan aprobado de 14 pasos
├── prompts/
│   ├── meta_prompt_planificacion.md
│   ├── plantilla_ejecucion_paso.md
│   └── respuestas/                 # Plan recibido de la IA
├── src/
│   ├── dominio/                    # Aggregate root, entidades, invariantes
│   │   ├── estado_tarea.py
│   │   ├── errores.py
│   │   ├── tarea.py
│   │   └── tablero.py              # INV-01 vive aquí (LIMITE_WIP = 3)
│   ├── aplicacion/                 # Casos de uso + puerto abstracto
│   │   ├── repositorio_tablero.py
│   │   ├── crear_tarea.py
│   │   ├── mover_tarea.py
│   │   └── obtener_tablero.py
│   └── infraestructura/            # Adaptadores: persistencia, HTTP, frontend
│       ├── persistencia/repositorio_tablero_json.py
│       ├── http/app.py
│       └── frontend/{index.html, estilos.css, app.js}
├── pruebas/
│   ├── dominio/                    # Pruebas puras del dominio
│   ├── aplicacion/                 # Casos de uso con doble en memoria
│   ├── infraestructura/            # Adaptadores reales (tmp_path, test_client)
│   └── arquitectura/               # Verificación automatizada de imports
├── BITACORA.md                     # Plan original, pasos, decisiones, bloqueos
└── README.md

## 9. Reglas de dependencia (ARCHITECTURE.md §3)
fraestructura  ────►  aplicacion  ────►  dominio
▲
│
(núcleo)
- src/dominio/ no importa de src/aplicacion/ ni de src/infraestructura/.
- src/aplicacion/ puede importar de src/dominio/.
- src/infraestructura/ puede importar de src/aplicacion/ y src/dominio/.
## 10. Trazabilidad del proceso

Cada commit del repositorio corresponde a un paso atómico del plan, identificado por
su número y su cambio normalizado (CAM-XX):

powershell
git log --oneline


Cada paso ejecutado tiene una entrada en BITACORA.md con:
- fecha,
- archivos modificados,
- comando de validación,
- resultado,
- hash del commit,
- observación técnica.

Decisiones técnicas relevantes registradas como DEC-01 a DEC-14.
Bloqueos resueltos registrados como BLOQ-XX.

## 11. Alcance del proyecto

*Incluido*:
- Crear tareas con título obligatorio.
- Mover tareas siguiendo transiciones TODO → DOING → DONE.
- Rechazar cuarta tarea en DOING (INV-01).
- Persistencia JSON local.
- Interfaz web mínima con JavaScript Vanilla.

*Excluido explícitamente* (CONTEXT.md §6):
- Autenticación, usuarios, roles.
- Base de datos relacional o NoSQL.
- Notificaciones, colaboración en tiempo real.
- Frameworks de frontend o librerías CSS.
- Estados adicionales (BLOCKED, CANCELLED, ARCHIVED).
- Cambiar LIMITE_WIP durante la ejecución.

## 12. Solución de problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| python no se reconoce | Python no instalado o no en PATH | Instalar Python 3.11+ y marcar "Add to PATH". |
| Activate.ps1 rechazado por permisos | Política de PowerShell | Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned. |
| ModuleNotFoundError: src al correr pytest | No estás en la raíz del proyecto | cd a la carpeta tablero-kanban. |
| Al ir a http://127.0.0.1:5000/ se ve un JSON o un 404 | Estás en /api/tablero o el frontend no existe | Ir a la raíz / y verificar src/infraestructura/frontend/. |
| La cuarta tarea en DOING se acepta | INV-01 violada | Ejecutar pytest pruebas/dominio/test_tablero.py -v y revisar tablero.py. |
| Falla pruebas/arquitectura/... | Algún archivo de dominio importa de fuera | Mover esa dependencia a src/infraestructura/. |