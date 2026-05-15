# BITACORA.md -- Tablero Kanban Personal

## 1. Estado actual
- Pasos ejecutados: 0 de N.
- Paso en curso: ninguno.
- Última actualización: {YYYY-MM-DD HH:MM}.
- Rama de trabajo: main o rama indicada por el profesor.

## 2. Plan original
Copiar aquí el plan aprobado antes de ejecutar código. El plan original no se edita; las modificaciones posteriores se registran como decisiones.

## 3. Pasos ejecutados

### Paso N - {titulo}
- Fecha: {YYYY-MM-DD HH:MM}
- Archivos modificados: {lista}
- Validación ejecutada: {comando}
- Resultado: {OK | bloqueo}
- Commit: {hash o referencia}
- Observación técnica breve: {máximo tres líneas}


### Paso 1 - Crear estructura de paquetes Python
- Fecha: {YYYY-MM-DD HH:MM}
- Archivos modificados:
  - src/__init__.py
  - src/dominio/__init__.py
  - src/aplicacion/__init__.py
  - src/infraestructura/__init__.py
  - src/infraestructura/http/__init__.py
  - src/infraestructura/persistencia/__init__.py
  - pruebas/__init__.py
  - pruebas/conftest.py
- Validación ejecutada: python -c "import src.dominio, src.aplicacion, src.infraestructura, src.infraestructura.http, src.infraestructura.persistencia; print('OK paquetes importables')"
- Resultado: OK
- Commit: {hash corto, lo añades tras commit --amend}
- Observación técnica: Esqueleto de paquetes Python listo. Sin lógica de dominio aún; preparado para PASO 2 (EstadoTarea).

### Paso 2 - Implementar enumerado EstadoTarea
- Fecha: {YYYY-MM-DD HH:MM}
- Archivos modificados:
  - src/dominio/estado_tarea.py (nuevo)
  - pruebas/dominio/__init__.py (nuevo, vacío)
  - pruebas/dominio/test_estado_tarea.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/dominio/test_estado_tarea.py -v
- Resultado: OK (5 passed)
- Commit: {hash corto}
- Observación técnica: Enumerado de dominio puro, solo usa stdlib (enum). Sin dependencias externas. Verificación arquitectónica grep en src/dominio: sin coincidencias.

### Paso 3 - Implementar errores de dominio
- Fecha: {YYYY-MM-DD HH:MM}
- Archivos modificados:
  - src/dominio/errores.py (nuevo)
  - pruebas/dominio/test_errores.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/dominio/test_errores.py -v
- Resultado: OK (17 passed)
- Commit: {hash corto}
- Observación técnica: Cuatro errores de DOMAIN.md §4 implementados como subclases de ErrorDominio (raíz semántica). Sin imports externos. Test de cierre verifica que no se añaden errores extra.

### Paso 4 - Implementar entidad Tarea con validación de título
- Fecha: {YYYY-MM-DD HH:MM}
- Archivos modificados:
  - src/dominio/tarea.py (nuevo)
  - pruebas/dominio/test_tarea.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/dominio/test_tarea.py -v
- Resultado: OK (14 passed)
- Commit: {hash corto}
- Observación técnica: Tarea como @dataclass con tres campos exactos (id_tarea, titulo, estado). INV-04 validada en __post_init__. cambiar_estado solo muta; la validación de transiciones queda para el aggregate root en el PASO 5.

### Paso 5 - Implementar aggregate root Tablero con LIMITE_WIP
- Fecha: {YYYY-MM-DD HH:MM}
- Archivos modificados:
  - src/dominio/tablero.py (nuevo)
  - pruebas/dominio/test_tablero.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/dominio/test_tablero.py -v
- Resultado: OK (19 passed)
- Commit: {hash corto}
- Observación técnica: Tablero como aggregate root protege INV-01 a INV-05. LIMITE_WIP = 3 a nivel de módulo (no parametrizable). Orden de verificaciones: existencia -> transición -> WIP -> mutación, lo que garantiza INV-05. El constructor rechaza tableros precargados que ya violen INV-01.

### Paso 6 - Verificación arquitectónica del dominio
- Fecha: 2026-05-15 HH:MM
- Archivos modificados:
  - pruebas/arquitectura/_init_.py (nuevo, vacío)
  - pruebas/arquitectura/test_dominio_aislado.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/arquitectura/test_dominio_aislado.py -v
- Resultado: OK (12 passed)
- Commit: {hash corto}
- Observación técnica: Verificación arquitectónica automatizada con AST. Reemplaza el grep manual por un test que falla si cualquier archivo de src/dominio/ importa Flask, json, requests, sqlalchemy, http, urllib, fastapi, django, pydantic, sqlite3, ni nada de src.aplicacion o src.infraestructura. Funciona como red de seguridad para los pasos 7-13.

### Paso 7 - Definir puerto abstracto RepositorioTablero
- Fecha: 2026-05-15 HH:MM
- Archivos modificados:
  - src/aplicacion/repositorio_tablero.py (nuevo)
  - pruebas/aplicacion/_init_.py (nuevo, vacío)
  - pruebas/aplicacion/test_repositorio_tablero_contrato.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/aplicacion/test_repositorio_tablero_contrato.py -v
- Resultado: OK (7 passed)
- Commit: {hash corto}
- Observación técnica: Puerto abstracto con exactamente cargar() y guardar(tablero), tal como ARCHITECTURE.md §4. Implementado con abc.ABC. El módulo solo depende de stdlib y de src.dominio.tablero. La implementación concreta JSON queda para el PASO 11.

### Paso 8 - Implementar caso de uso CrearTarea
- Fecha: 2026-05-15 HH:MM
- Archivos modificados:
  - src/aplicacion/crear_tarea.py (nuevo)
  - pruebas/aplicacion/conftest.py (nuevo: fixture repositorio_en_memoria)
  - pruebas/aplicacion/test_crear_tarea.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/aplicacion/test_crear_tarea.py -v
- Resultado: OK (12 passed)
- Commit: {hash corto}
- Observación técnica: Caso de uso CrearTarea con inyección de dependencia del puerto. Doble RepositorioTableroEnMemoria como fixture compartida (DEC-06). La validación de INV-04 se delega al dominio; el caso de uso solo orquesta cargar -> crear -> guardar y propaga errores sin persistir cambios parciales.

### Paso 9 - Implementar caso de uso MoverTarea
- Fecha: 2026-05-15 HH:MM
- Archivos modificados:
  - src/aplicacion/mover_tarea.py (nuevo)
  - pruebas/aplicacion/test_mover_tarea.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/aplicacion/test_mover_tarea.py -v
- Resultado: OK (13 passed)
- Commit: {hash corto}
- Observación técnica: Caso de uso MoverTarea con la misma forma que CrearTarea (DEC-07). La regla WIP, las transiciones y la existencia de la tarea se delegan íntegramente al aggregate root Tablero. El caso de uso solo orquesta cargar -> mover -> guardar y propaga errores. Soporta estado destino como EstadoTarea o como string canónico (preparación para el PASO 12).

### Paso 10 - Implementar caso de uso ObtenerTablero
- Fecha: 2026-05-15 HH:MM
- Archivos modificados:
  - src/aplicacion/obtener_tablero.py (nuevo)
  - pruebas/aplicacion/test_obtener_tablero.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/aplicacion/test_obtener_tablero.py -v
- Resultado: OK (10 passed)
- Commit: {hash corto}
- Observación técnica: Consulta pura: no invoca guardar() bajo ningún flujo. Devuelve un TableroDTO con las tres claves TODO/DOING/DONE siempre presentes. Cada TareaDTO contiene exactamente id_tarea, titulo y estado, todos como strings serializables a JSON. Cierra la capa de aplicación.

### Paso 11 - Implementar adaptador RepositorioTableroJson
- Fecha: 2026-05-15 HH:MM
- Archivos modificados:
  - src/infraestructura/persistencia/repositorio_tablero_json.py (nuevo)
  - pruebas/infraestructura/_init_.py (nuevo, vacío)
  - pruebas/infraestructura/test_repositorio_tablero_json.py (nuevo)
- Validación ejecutada: python -m pytest pruebas/infraestructura/test_repositorio_tablero_json.py -v
- Resultado: OK (11 passed)
- Commit: {hash corto}
- Observación técnica: Primer adaptador de infraestructura. Implementa el puerto RepositorioTablero usando archivo JSON local con stdlib (json + pathlib). La ruta se inyecta por constructor, no se hardcodea. El round-trip conserva el estado y la prueba clave test_wip_se_respeta_a_traves_de_la_persistencia demuestra que INV-01 sobrevive a reinicios.

## 4. Pasos pendientes
- [x] Paso 1 - Crear estructura de paquetes Python
- [x] Paso 2 - Implementar enumerado EstadoTarea
- [x] Paso 3 - Implementar errores de dominio
- [x] Paso 4 - Implementar entidad Tarea
- [x] Paso 5 - Implementar aggregate root Tablero
- [x] Paso 6 - Verificación arquitectónica del dominio
- [x] Paso 7 - Definir puerto RepositorioTablero
- [x] Paso 8 - Implementar caso de uso CrearTarea
- [x] Paso 9 - Implementar caso de uso MoverTarea
- [x] Paso 10 - Implementar caso de uso ObtenerTablero
- [x] Paso 11 - Implementar adaptador RepositorioTableroJson
- [ ] Paso 12 - Implementar adaptador HTTP Flask
- [ ] Paso 13 - Implementar frontend Vanilla
- [ ] Paso 14 - Actualizar README

## 5. Decisiones tomadas

### DEC-01 (paso 3) - Raíz común ErrorDominio para los errores
- Decisión: definir ErrorDominio como clase base de los cuatro errores de DOMAIN.md §4.
- Justificación: permite a la infraestructura HTTP (paso 12) capturar errores de dominio de forma uniforme sin acoplarse a cada subclase. No introduce comportamiento ni nuevos errores funcionales. Las cuatro clases listadas en DOMAIN.md §4 siguen existiendo con sus nombres exactos.
- Impacto: el adaptador HTTP del paso 12 puede tener un único `except ErrorDominio` para mapeo de códigos de estado, en lugar de cuatro `except` separados. Sin impacto en dominio ni aplicación.

### DEC-02 (paso 4) - Tarea.cambiar_estado no valida transiciones
- Decisión: el método `cambiar_estado` de la entidad Tarea solo muta el campo `estado`, sin verificar INV-01, INV-02 ni INV-03.
- Justificación: DOMAIN.md §2 establece que Tablero es el aggregate root y "toda creación o movimiento de tarea debe pasar por Tablero". Si la entidad Tarea validara transiciones por su cuenta, duplicaríamos la regla y permitiríamos saltarse al aggregate root. La validación de INV-01/02/03 vive exclusivamente en Tablero (PASO 5).
- Impacto: el PASO 5 (Tablero.mover_tarea) debe invocar Tarea.cambiar_estado solo después de haber validado la transición y el WIP. Cualquier código externo que llame directamente a Tarea.cambiar_estado sin pasar por Tablero es una violación arquitectónica.

### DEC-03 (paso 5) - Orden de verificación en mover_tarea
- Decisión: en `Tablero.mover_tarea` el orden de checks es (1) existencia de la tarea, (2) transición permitida (INV-03), (3) límite WIP (INV-01). La mutación del estado ocurre solo si los tres pasan.
- Justificación: este orden asegura INV-05 (no persistir cambios parciales) y produce mensajes de error más útiles (un id inexistente nunca debería disparar un error de WIP). También evita que un intento inválido como TODO->DONE consuma "intentos" o disparé efectos colaterales.
- Impacto: la prueba `test_al_rechazar_la_cuarta_tarea_el_tablero_no_se_modifica` documenta este contrato.

### DEC-04 (paso 5) - Constructor del Tablero rechaza estado inicial inválido
- Decisión: `Tablero(tareas=...)` valida en el constructor que las tareas precargadas no excedan LIMITE_WIP. Si lo exceden, lanza ErrorLimiteWipExcedido.
- Justificación: en el PASO 11 (RepositorioTableroJson) cargaremos el tablero desde un archivo. Si el archivo está corrupto o fue editado a mano, el dominio NO debe arrancar en estado inválido y dejar que la regla se viole "porque ya estaba así". Mejor fallar al cargar y obligar a corregir.
- Impacto: el adaptador de persistencia debe capturar este error y reportarlo claramente al cargar; nunca debe silenciarlo.

### DEC-05 (paso 6) - Lista ampliada de módulos prohibidos en el dominio
- Decisión: la prueba arquitectónica prohíbe en el dominio no solo los módulos que aparecen literalmente en ARCHITECTURE.md §6 (flask, json, requests, sqlalchemy, http) sino también urllib, urllib3, aiohttp, httpx, starlette, fastapi, django, pydantic y sqlite3.
- Justificación: el principio rector de ARCHITECTURE.md §1 es general ("el dominio no conoce HTTP, archivos, JSON ni detalles de interfaz") y TECH_CONSTRAINTS.md §2 prohíbe explícitamente Django, FastAPI y SQLAlchemy. Listar solo los cinco patrones del grep dejaría puertas abiertas (por ejemplo, importar urllib.request cumpliría el grep pero violaría el principio). Ampliar la lista refuerza el espíritu de la regla.
- Impacto: si un paso futuro intenta meter cualquiera de esos módulos en el dominio, la prueba falla y el commit no se hace. Si el profesor cuestionara la lista, basta argumentar que es un superset estricto de la verificación oficial.

### DEC-06 (paso 7) - Subtipo en memoria _RepositorioEnMemoria vive en las pruebas, no en src/
- Decisión: la implementación en memoria del puerto se define dentro del archivo de pruebas (pruebas/aplicacion/test_repositorio_tablero_contrato.py) y, en los pasos 8-10, se replicará como fixture compartida en pruebas/aplicacion/.
- Justificación: src/ contiene únicamente código de producción (puerto abstracto + casos de uso + adaptador real). Un repositorio en memoria mezclado en src/aplicacion/ confundiría capas, y un compañero podría usarlo "por error" en producción. Las pruebas son el único lugar legítimo para dobles.
- Impacto: en los pasos 8-10 se extraerá el doble a una fixture pytest reutilizable. En src/ nunca habrá implementaciones de puerto distintas a la oficial (JSON, PASO 11).

### DEC-07 (paso 8) - Nombre del método de entrada: ejecutar()
- Decisión: cada caso de uso expone un único método público llamado ejecutar(...) con la firma propia del caso (CrearTarea.ejecutar(titulo) -> Tarea).
- Justificación: convención uniforme para los casos de uso de los pasos 9 y 10 (MoverTarea.ejecutar(...), ObtenerTablero.ejecutar(...)). Facilita el mapeo desde el adaptador HTTP del PASO 12: cada endpoint instancia el caso de uso correspondiente, llama a ejecutar(), traduce excepciones a códigos HTTP.
- Impacto: los pasos 9, 10 y 12 reutilizan esta convención. El adaptador HTTP del PASO 12 podra escribirse de forma muy regular.

### DEC-08 (paso 9) - Normalización del estado destino antes de cargar el tablero
- Decisión: MoverTarea.ejecutar normaliza el parámetro estado_destino (acepta EstadoTarea o un string canónico) ANTES de invocar repositorio.cargar(). Si la normalización falla (string desconocido, tipo incorrecto), se propaga ValueError o TypeError sin tocar el repositorio.
- Justificación: una entrada malformada (típicamente desde HTTP) no debe disparar IO innecesaria. Cargar el tablero solo para descubrir que el estado destino es 'BLOCKED' es desperdicio y dificulta diagnosticar errores. El orden "validar entrada -> tocar IO" es una buena práctica.
- Impacto: el adaptador HTTP del PASO 12 puede pasar directamente el string del body JSON sin convertirlo; la conversión y el error 400 viven en el caso de uso.

### DEC-09 (paso 10) - DTO con tres claves fijas TODO/DOING/DONE y TypedDict
- Decisión: ObtenerTablero devuelve un TableroDTO modelado con typing.TypedDict, con las tres claves fijas TODO, DOING y DONE (siempre presentes, incluso vacías). Cada TareaDTO tiene exactamente id_tarea, titulo y estado, todos como strings.
- Justificación:
  (a) FEATURE_SPEC_003 AC-01 exige que las tres columnas existan siempre, para que la UI del PASO 13 pueda iterar las tres sin condicionales.
  (b) UUID y Enum no son serializables nativamente por json.dumps; convertirlos a string en la frontera de aplicación evita que el adaptador HTTP del PASO 12 tenga que conocer estos detalles.
  (c) TypedDict documenta el contrato al lector y al IDE sin imponer una dependencia runtime nueva (es stdlib).
- Impacto: el adaptador HTTP del PASO 12 puede devolver el DTO directamente con jsonify(); el frontend del PASO 13 itera 'TODO', 'DOING', 'DONE' como columnas.

### DEC-10 (paso 11) - Esquema JSON versionado y escritura completa
- Decisión: el archivo JSON incluye un campo "version": 1 y se reescribe completo en cada guardar(). No usamos formato append ni JSON Lines.
- Justificación:
  (a) La versión permite cambios futuros del esquema sin romper archivos viejos: el adaptador podría leer v1 y migrar a v2.
  (b) La escritura completa simplifica enormemente la atomicidad lógica (no quedan estados "a medias" si se interrumpe el guardar mid-operación, en el peor caso el archivo queda con el contenido anterior intacto al usar write_text que es un solo syscall en la práctica).
  (c) El alcance del proyecto (uso personal local, pocas tareas) hace que el costo de reescribir todo sea despreciable.
- Impacto: en cada guardar se serializa todo el tablero. Aceptable para este alcance.

### DEC-11 (paso 11) - Ruta del archivo inyectada por constructor
- Decisión: RepositorioTableroJson(ruta_archivo) recibe la ruta como parámetro obligatorio. No hay valor por defecto hardcodeado.
- Justificación: TECH_CONSTRAINTS.md §2 prohíbe que el dominio conozca rutas de archivo, y por consistencia tampoco quiero que el adaptador hardcodee una ubicación. El PASO 12 (Flask) decidirá dónde vive el archivo leyendo una variable de entorno o usando un default visible en su propio módulo. Esto mantiene la decisión de ubicación en un solo lugar.
- Impacto: el PASO 12 declara la ruta del JSON al instanciar el adaptador. Las pruebas usan tmp_path de pytest, lo que aísla cada test.

## 6. Bloqueos y solución

### BLOQ-XX
- Síntoma:
- Causa probable:
- Solución aplicada:
- Evidencia:
## guardar comits
----------------------------------------------------
git add .
git commit -m "descripción del cambio"
git push

python -m pytest pruebas/arquitectura/test_dominio_aislado.py -v  (prueba arquitectonica del dominio)

python -m pytest -v  (comando para todas las pruebas )