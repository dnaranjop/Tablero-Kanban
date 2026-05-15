# init_kanban.ps1
# Crea la estructura inicial del proyecto Tablero Kanban segun la guia §7.2.
# Uso: ejecutar en PowerShell desde la carpeta donde quieras crear el proyecto.

mkdir tablero-kanban
cd tablero-kanban
git init

New-Item -ItemType Directory -Force -Path `
  context, specs, plan, prompts\respuestas, `
  src\dominio, src\aplicacion, `
  src\infraestructura\http, src\infraestructura\persistencia, `
  src\infraestructura\frontend, pruebas | Out-Null

New-Item -ItemType File -Force -Path `
  context\CONTEXT.md, context\DOMAIN.md, context\ARCHITECTURE.md, `
  context\TECH_CONSTRAINTS.md, context\GLOSSARY.md, `
  specs\FEATURE_SPEC_001_crear_tarea.md, `
  specs\FEATURE_SPEC_002_mover_tarea.md, `
  specs\FEATURE_SPEC_003_obtener_tablero.md, `
  plan\PLAN_ATOMICO.md, prompts\meta_prompt_planificacion.md, `
  prompts\plantilla_ejecucion_paso.md, BITACORA.md, README.md | Out-Null

Write-Host ""
Write-Host "Estructura creada. Ahora copia el contenido de los archivos .md de la entrega"
Write-Host "y ejecuta el commit inicial:"
Write-Host ""
Write-Host "  git add ."
Write-Host '  git commit -m "chore: esqueleto inicial - contexto antes que codigo"'
