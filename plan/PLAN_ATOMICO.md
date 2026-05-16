# PLAN_ATOMICO.md -- Plan aprobado propuesto por la IA

*Estado:* aprobado por el estudiante el 2026-05-15.
*Origen:* plan propuesto por la IA a partir del paquete de contexto, revisado con el protocolo de tres preguntas (§5 de la guía) y aprobado en conjunto.

---

## Parte 1 — Cambios normalizados

| ID | Cambio | Capa primaria | Referencia |
|---|---|---|---|
| CAM-01 | Definir el enumerado EstadoTarea con valores TODO, DOING, DONE | Dominio | DOMAIN.md §1, §6 / GLOSSARY.md |
| CAM-02 | Definir las excepciones de dominio (ErrorTituloTareaInvalido, ErrorTareaNoEncontrada, ErrorTransicionInvalida, ErrorLimiteWipExcedido) | Dominio | DOMAIN.md §4 |
| CAM-03 | Definir la entidad Tarea (id_tarea, titulo, estado) con validación de título | Dominio | DOMAIN.md §1, INV-04 / FEATURE_SPEC_001 |
| CAM-04 | Definir el aggregate root Tablero con la constante LIMITE_WIP=3 y operaciones que protejan INV-01 a INV-05 | Dominio | DOMAIN.md §2, §3, §5 |
| CAM-05 | Definir el puerto abstracto RepositorioTablero en la capa de aplicación | Aplicación | ARCHITECTURE.md §4 |
| CAM-06 | Implementar el caso de uso CrearTarea | Aplicación | FEATURE_SPEC_001 / AC-01 a AC-05 |
| CAM-07 | Implementar el caso de uso MoverTarea | Aplicación | FEATURE_SPEC_002 / AC-01 a AC-06 |
| CAM-08 | Implementar el caso de uso ObtenerTablero (consulta sin efectos) | Aplicación | FEATURE_SPEC_003 / AC-01 a AC-03 |
| CAM-09 | Implementar el adaptador de persistencia JSON | Infraestructura | ARCHITECTURE.md §5 / TECH_CONSTRAINTS.md §1 |
| CAM-10 | Implementar el adaptador HTTP Flask | Infraestructura | ARCHITECTURE.md §5 / FEATURE_SPEC_001..003 |
| CAM-11 | Implementar el frontend Vanilla (HTML + CSS + JS) | Infraestructura/UI | ARCHITECTURE.md §5 / TECH_CONSTRAINTS.md §1 |
| CAM-12 | Verificación arquitectónica automatizada (ausencia de imports prohibidos en src/dominio) | Pruebas | ARCHITECTURE.md §6 |
| CAM-13 | Actualizar README con instrucciones de ejecución reales del adaptador Flask | Documentación | README.md §5 |

---

## Parte 2 — Diagrama de dependencias

El orden topológico respeta la regla de dependencia de ARCHITECTURE.md §3: el dominio se construye primero, después la aplicación, finalmente la infraestructura.


[PASO 1: estructura paquetes]
        │
        ▼
[PASO 2: CAM-01 EstadoTarea] ──────┐
        │                          │
        ▼                          │
[PASO 3: CAM-02 Errores dominio] ──┤
        │                          │
        ▼                          │
[PASO 4: CAM-03 Tarea] ────────────┤   (dominio puro,
        │                          │    sin imports
        ▼                          │    externos)
[PASO 5: CAM-04 Tablero (root)] ───┘
        │
        ▼
[PASO 6: CAM-12 Verificación arquitectónica del dominio]
        │
        ▼
[PASO 7: CAM-05 Puerto RepositorioTablero]
        │
        ├───────────────┬───────────────┐
        ▼               ▼               ▼
[PASO 8: CAM-06]  [PASO 9: CAM-07]  [PASO 10: CAM-08]
 CrearTarea        MoverTarea        ObtenerTablero
        │               │               │
        └───────────────┴───────┬───────┘
                                ▼
[PASO 11: CAM-09 RepositorioTableroJson]
        │
        ▼
[PASO 12: CAM-10 Adaptador Flask]
        │
        ▼
[PASO 13: CAM-11 Frontend Vanilla]
        │
        ▼
[PASO 14: CAM-13 README final]


Cualquier paso de infraestructura ejecutado antes de su dependencia de dominio o aplicación viola las reglas de dependencia.

## Parte 3 — Plan paso a paso


PASO 1 — Crear estructura de paquetes Python
Fase: Análisis
Cambio normalizado: prerrequisito (no toca dominio aún)
Referencia de contexto: ARCHITECTURE.md §2, §3 / TECH_CONSTRAINTS.md §3
Capas afectadas: ninguna (solo esqueleto)
Archivos autorizados:
  - src/__init__.py, src/dominio/__init__.py, src/aplicacion/__init__.py
  - src/infraestructura/__init__.py, src/infraestructura/http/__init__.py
  - src/infraestructura/persistencia/__init__.py
  - pruebas/__init__.py, pruebas/conftest.py
Validación: python -c "import src.dominio, src.aplicacion, src.infraestructura"
Criterio de aceptación: los paquetes son importables sin ImportError.
Riesgo arquitectónico: ninguno; solo crea archivos vacíos.
Autorización: aprobado por el estudiante



PASO 2 — Implementar enumerado EstadoTarea
Fase: Dominio
Cambio normalizado: CAM-01
Referencia de contexto: DOMAIN.md §1, §6 / GLOSSARY.md
Capas afectadas: Dominio
Archivos autorizados:
  - src/dominio/estado_tarea.py
  - pruebas/dominio/test_estado_tarea.py
Validación: python -m pytest pruebas/dominio/test_estado_tarea.py -v
Criterio de aceptación: EstadoTarea expone exactamente TODO, DOING, DONE.
Riesgo arquitectónico: que el archivo importe algo externo. Solo stdlib (enum).
Autorización: aprobado por el estudiante



PASO 3 — Implementar errores de dominio
Fase: Dominio
Cambio normalizado: CAM-02
Referencia de contexto: DOMAIN.md §4
Capas afectadas: Dominio
Archivos autorizados:
  - src/dominio/errores.py
  - pruebas/dominio/test_errores.py
Validación: python -m pytest pruebas/dominio/test_errores.py -v
Criterio de aceptación: existen las clases ErrorTituloTareaInvalido, ErrorTareaNoEncontrada, ErrorTransicionInvalida y ErrorLimiteWipExcedido.
Riesgo arquitectónico: errores adicionales no listados en DOMAIN.md §4. Si la IA propone otros, rechazar.
Autorización: aprobado por el estudiante



PASO 4 — Implementar entidad Tarea con validación de título
Fase: Dominio
Cambio normalizado: CAM-03
Referencia de contexto: DOMAIN.md §1 / INV-04 / FEATURE_SPEC_001 AC-02, AC-03
Capas afectadas: Dominio
Archivos autorizados:
  - src/dominio/tarea.py
  - pruebas/dominio/test_tarea.py
Validación: python -m pytest pruebas/dominio/test_tarea.py -v
Criterio de aceptación:
  - Tarea contiene exactamente id_tarea, titulo y estado.
  - Crear con título "" o "   " lanza ErrorTituloTareaInvalido.
Riesgo arquitectónico: agregar campos como prioridad o fecha_limite (rechazar).
Autorización: aprobado por el estudiante



PASO 5 — Implementar aggregate root Tablero con LIMITE_WIP
Fase: Dominio
Cambio normalizado: CAM-04
Referencia de contexto: DOMAIN.md §2, §3 (INV-01..05), §5 / TECH_CONSTRAINTS.md §2
Capas afectadas: Dominio
Archivos autorizados:
  - src/dominio/tablero.py
  - pruebas/dominio/test_tablero.py
Validación: python -m pytest pruebas/dominio/test_tablero.py -v
Criterio de aceptación (mínimos):
  - crear_tarea agrega tarea en TODO (AC-01).
  - cuarta en DOING lanza ErrorLimiteWipExcedido (AC-02, INV-01, INV-02).
  - TODO->DONE lanza ErrorTransicionInvalida (AC-03, INV-03).
  - DOING->DONE funciona (AC-04).
  - Tarea inexistente lanza ErrorTareaNoEncontrada.
  - Operación inválida no modifica el estado (INV-05).
  - obtener_tareas_por_estado devuelve TODO, DOING, DONE.
Riesgo arquitectónico: que Tablero importe Flask, json o rutas. Verificar con grep en PASO 6.
Autorización: aprobado por el estudiante



PASO 6 — Verificación arquitectónica del dominio
Fase: Pruebas
Cambio normalizado: CAM-12
Referencia de contexto: ARCHITECTURE.md §6 / TECH_CONSTRAINTS.md §2
Capas afectadas: Dominio (verificación)
Archivos autorizados:
  - pruebas/arquitectura/test_dominio_aislado.py
Validación: python -m pytest pruebas/arquitectura/test_dominio_aislado.py -v
Criterio de aceptación: el dominio no contiene ningún import prohibido (flask, requests, sqlalchemy, json, http, urllib, fastapi, django, pydantic, sqlite3) ni imports de src.aplicacion / src.infraestructura.
Riesgo arquitectónico: si falla, NO avanzar a la capa de aplicación.
Autorización: aprobado por el estudiante



PASO 7 — Definir puerto abstracto RepositorioTablero
Fase: Aplicación
Cambio normalizado: CAM-05
Referencia de contexto: ARCHITECTURE.md §3, §4
Capas afectadas: Aplicación
Archivos autorizados:
  - src/aplicacion/repositorio_tablero.py
  - pruebas/aplicacion/test_repositorio_tablero_contrato.py
Validación: python -m pytest pruebas/aplicacion/test_repositorio_tablero_contrato.py -v
Criterio de aceptación: el puerto es ABC con métodos abstractos cargar() y guardar(tablero), nada más.
Riesgo arquitectónico:
  - Métodos adicionales (rechazar).
  - Imports de infraestructura en el puerto (rechazar).
Autorización: aprobado por el estudiante

PASO 8 — Implementar caso de uso CrearTarea
Fase: Aplicación
Cambio normalizado: CAM-06
Referencia de contexto: FEATURE_SPEC_001 AC-01 a AC-05
Capas afectadas: Aplicación
Archivos autorizados:
  - src/aplicacion/crear_tarea.py
  - pruebas/aplicacion/conftest.py (fixture compartida del doble en memoria)
  - pruebas/aplicacion/test_crear_tarea.py
Validación: python -m pytest pruebas/aplicacion/test_crear_tarea.py -v
Criterio de aceptación:
  - AC-01: tarea creada con id, titulo y estado TODO.
  - AC-02, AC-03: titulo invalido propaga ErrorTituloTareaInvalido.
  - AC-04: tras exito guardar() se invoca exactamente una vez.
  - AC-05: ante error guardar() NO se invoca.
Riesgo arquitectónico:
  - Caso de uso que instancia un repositorio concreto (debe inyectarse).
  - Validación de título en el caso de uso (INV-04 vive en el dominio).
Autorización: aprobado por el estudiante



PASO 9 — Implementar caso de uso MoverTarea
Fase: Aplicación
Cambio normalizado: CAM-07
Referencia de contexto: FEATURE_SPEC_002 AC-01 a AC-06
Capas afectadas: Aplicación
Archivos autorizados:
  - src/aplicacion/mover_tarea.py
  - pruebas/aplicacion/test_mover_tarea.py
Validación: python -m pytest pruebas/aplicacion/test_mover_tarea.py -v
Criterio de aceptación:
  - AC-01: TODO->DOING con DOING<3 funciona.
  - AC-02: cuarta tarea a DOING lanza ErrorLimiteWipExcedido y no guarda.
  - AC-03: TODO->DONE lanza ErrorTransicionInvalida y no guarda.
  - AC-04: DOING->DONE funciona.
  - AC-05: tras exito, guardar() se invoca exactamente una vez.
  - AC-06: ante error de dominio, guardar() no se invoca.
Riesgo arquitectónico:
  - Que el caso de uso recalcule la regla WIP en lugar de delegarla a Tablero.
Autorización: aprobado por el estudiante



PASO 10 — Implementar caso de uso ObtenerTablero
Fase: Aplicación
Cambio normalizado: CAM-08
Referencia de contexto: FEATURE_SPEC_003 AC-01 a AC-03
Capas afectadas: Aplicación
Archivos autorizados:
  - src/aplicacion/obtener_tablero.py
  - pruebas/aplicacion/test_obtener_tablero.py
Validación: python -m pytest pruebas/aplicacion/test_obtener_tablero.py -v
Criterio de aceptación:
  - AC-01: la salida contiene SIEMPRE las claves TODO, DOING y DONE.
  - AC-02: la consulta NO invoca guardar() (cero llamadas).
  - AC-03: la estructura es serializable a JSON.
Riesgo arquitectónico:
  - Cualquier llamada a guardar en una consulta es bug y se rechaza.
Autorización: aprobado por el estudiante



PASO 11 — Implementar adaptador de persistencia JSON
Fase: Infraestructura
Cambio normalizado: CAM-09
Referencia de contexto: ARCHITECTURE.md §4, §5 / TECH_CONSTRAINTS.md §1 (stdlib json)
Capas afectadas: Infraestructura
Archivos autorizados:
  - src/infraestructura/persistencia/repositorio_tablero_json.py
  - pruebas/infraestructura/test_repositorio_tablero_json.py
Validación: python -m pytest pruebas/infraestructura/test_repositorio_tablero_json.py -v
Criterio de aceptación:
  - guardar() crea un archivo JSON con la representacion correcta.
  - cargar() de un archivo existente reconstruye el Tablero.
  - cargar() sobre archivo inexistente devuelve Tablero vacio (FEATURE_SPEC_003 Bloque 4).
  - Round-trip guardar->cargar conserva el estado.
Riesgo arquitectónico:
  - Que el adaptador modifique la entidad Tarea o el Tablero.
  - Ruta del archivo hardcodeada en el dominio (debe ser parametro del adaptador).
Autorización: aprobado por el estudiante



PASO 12 — Implementar adaptador HTTP Flask
Fase: Infraestructura
Cambio normalizado: CAM-10
Referencia de contexto: ARCHITECTURE.md §5 / TECH_CONSTRAINTS.md §1 / FEATURE_SPEC_001..003
Capas afectadas: Infraestructura
Archivos autorizados:
  - src/infraestructura/http/app.py
  - pruebas/infraestructura/test_app_http.py
Endpoints minimos:
  - POST   /api/tareas       (201 con la tarea; 400 con titulo invalido)
  - PATCH  /api/tareas/<id>  (200 tablero; 404 no encontrada; 409 WIP/transicion)
  - GET    /api/tablero      (200 tablero agrupado)
Validación: python -m pytest pruebas/infraestructura/test_app_http.py -v
Criterio de aceptación: los tres endpoints responden los códigos esperados; los errores de dominio se traducen a HTTP, no se filtran como 500.
Riesgo arquitectónico:
  - Lógica de negocio en el handler HTTP (debe limitarse a parsear/llamar/mapear).
  - Introducción de ORM o tecnologías no autorizadas.
Autorización: aprobado por el estudiante



PASO 13 — Implementar frontend Vanilla
Fase: UI
Cambio normalizado: CAM-11
Referencia de contexto: ARCHITECTURE.md §5 / TECH_CONSTRAINTS.md §1, §2 / CONTEXT.md §5, §7
Capas afectadas: Presentación
Archivos autorizados:
  - src/infraestructura/frontend/index.html
  - src/infraestructura/frontend/estilos.css
  - src/infraestructura/frontend/app.js
  - pruebas/infraestructura/test_frontend_servido.py
Validación:
  - python -m pytest pruebas/infraestructura/test_frontend_servido.py -v
  - Prueba manual con flask run en http://127.0.0.1:5000/.
Criterio de aceptación: el usuario opera las tres columnas y la cuarta tarea en DOING se rechaza por el backend con 409 (visible en F12 -> Network).
Riesgo arquitectónico:
  - Bloquear visualmente la cuarta tarea (viola CONTEXT.md §7).
  - Usar React, Vue, jQuery, Tailwind o Bootstrap.
Autorización: aprobado por el estudiante



PASO 14 — Actualizar README con instrucciones reales de ejecución
Fase: Documentación
Cambio normalizado: CAM-13
Referencia de contexto: README.md §5 / TECH_CONSTRAINTS.md §4 / Checklist §14 de la guía
Capas afectadas: Documentación
Archivos autorizados:
  - README.md
Validación: lectura del README simulando un compañero externo + python -m pytest -v (sigue verde).
Criterio de aceptación: alguien que clona el repo y sigue el README consigue instalar, correr pytest, levantar Flask y reproducir las pruebas manuales.
Riesgo arquitectónico: que el paso aproveche para alterar código (rechazar). Solo documentación.
Autorización: aprobado por el estudiante


---

## Cierre del plan

- *Total de pasos aprobados:* 14.
- *Trazabilidad CAM:* CAM-01 a CAM-13 (más PASO 1 como prerrequisito sin CAM).
- *Cobertura de FEATURE_SPECs:* las tres especificaciones se cubren con los pasos 8, 9 y 10 respectivamente.
- *Cobertura de invariantes:* INV-01 a INV-05 viven en el aggregate root del PASO 5 y se verifican en los pasos 5, 8, 9, 11 y 12.
- *Mitigaciones declaradas:* CONTEXT.md §7 ("regla WIP solo en interfaz") se mitiga con los pasos 5, 9 y 13 (DEC-14).
- *Verificación arquitectónica:* PASO 6 reemplaza el grep manual por una prueba AST automatizada.

Bloqueos encontrados durante la ejecución (registrados en BITACORA.md sección 6):
- *BLOQ-01:* los pasos 1-5 se ejecutaron sin commits intermedios; se consolidó con commits retroactivos al detectarlo.
- *BLOQ-02:* la prueba test_index_devuelve_404_si_frontend_no_existe quedó obsoleta tras el PASO 13 y se eliminó.

*Plan ejecutado completo el 2026-05-15.*
