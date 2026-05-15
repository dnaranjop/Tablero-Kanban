# TECH_CONSTRAINTS.md -- Tablero Kanban Personal

## 1. Stack obligatorio
- Python 3.11 o superior.
- Flask 3.x solamente como adaptador HTTP.
- HTML5, CSS3 y JavaScript Vanilla ES6+.
- Persistencia JSON usando biblioteca estándar de Python.
- pytest para pruebas automatizadas.
- Git para versionamiento paso a paso.

## 2. Prohibiciones
- No usar Django, FastAPI, SQLAlchemy, React, Vue, Angular, jQuery, Tailwind ni Bootstrap.
- No conectar el dominio con archivos, HTTP, Flask, JSON o variables de entorno.
- No resolver invariantes solo con validaciones de interfaz.
- No cambiar LIMITE_WIP a configurable.
- No agregar autenticación ni multiusuario.
- No generar código fuera de las rutas autorizadas en el paso.
- No agregar campos que no estén en GLOSSARY.md o en las especificaciones.

## 3. Convenciones de código
- Identificadores en español sin tildes.
- Archivos Python con nombres en minúscula y guion bajo.
- Cada paso debe poder validarse con pytest o con un comando de verificación explícito.
- Cada respuesta de la IA debe indicar archivos afectados antes de mostrar código.
- Si falta contexto para implementar un paso, la IA debe detenerse y solicitar aclaración.

## 4. Criterio de aceptación global
El proyecto se considera funcional cuando se puede crear una tarea, obtener el tablero, mover una tarea de TODO a DOING, impedir una cuarta tarea en DOING, mover tareas de DOING a DONE y conservar el tablero en JSON.
