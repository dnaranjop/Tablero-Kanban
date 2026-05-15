# CONTEXT.md -- Tablero Kanban Personal con Límite WIP

## 1. Propósito
Construir una aplicación local para gestionar tareas personales en un tablero Kanban con tres columnas: TODO, DOING y DONE. El sistema debe impedir que existan más de tres tareas simultáneas en la columna DOING.

## 2. Problema de negocio
El usuario tiende a iniciar demasiadas tareas al mismo tiempo. El sistema debe ayudarle a concentrarse limitando el trabajo en progreso y obligándolo a terminar tareas antes de iniciar nuevas.

## 3. Usuario principal
Usuario individual que organiza tareas personales o académicas desde un navegador en su equipo local.

## 4. Métricas de éxito
- Crear una tarea en menos de 200 ms en entorno local.
- Mover una tarea válida en menos de 200 ms en entorno local.
- Rechazar siempre una cuarta tarea en DOING.
- Mantener el tablero persistido después de reiniciar el servidor.
- Permitir validar las reglas del dominio mediante pruebas automatizadas.

## 5. Alcance incluido
- Crear tareas con título obligatorio.
- Mostrar tareas agrupadas por estado: TODO, DOING y DONE.
- Mover tareas siguiendo transiciones permitidas.
- Rechazar transiciones inválidas mediante errores de dominio.
- Rechazar una cuarta tarea en DOING mediante ErrorLimiteWipExcedido.
- Persistir el estado del tablero en un archivo JSON local.
- Exponer una interfaz web mínima con HTML, CSS y JavaScript Vanilla.

## 6. Alcance excluido
- [FUERA] Autenticación, usuarios, roles o perfiles.
- [FUERA] Base de datos relacional, NoSQL o migraciones.
- [FUERA] Despliegue en la nube.
- [FUERA] Notificaciones, comentarios o archivos adjuntos.
- [FUERA] Colaboración en tiempo real.
- [FUERA] Frameworks de frontend o librerías CSS.
- [FUERA] Cambiar el límite WIP durante la ejecución.
- [FUERA] Estados adicionales como BLOCKED, CANCELLED o ARCHIVED.

## 7. Riesgos del alcance
- Riesgo: que la IA agregue autenticación, base de datos o frameworks no solicitados.
  Mitigación: TECH_CONSTRAINTS.md prohíbe esas decisiones.
- Riesgo: que la regla WIP quede solo en la interfaz.
  Mitigación: DOMAIN.md exige que Tablero proteja la invariante INV-01.
- Riesgo: que la IA agregue campos habituales como prioridad, fecha límite o usuario.
  Mitigación: GLOSSARY.md y las especificaciones limitan la entidad Tarea a id_tarea, titulo y estado.
