# meta_prompt_planificacion.md -- Solicitud de plan a la IA

## ROL
Actúa como Ingeniero Senior especializado en DDD, Arquitectura Hexagonal, Clean Architecture, Python y Spec-Driven Development. Tu tarea es redactar un PLAN_ATOMICO de implementación a partir del paquete de contexto. No generes código.

## CONTEXTO OBLIGATORIO
Lee con atención estos archivos en este orden:
1. context/CONTEXT.md
2. context/DOMAIN.md
3. context/ARCHITECTURE.md
4. context/TECH_CONSTRAINTS.md
5. context/GLOSSARY.md
6. specs/FEATURE_SPEC_001_crear_tarea.md
7. specs/FEATURE_SPEC_002_mover_tarea.md
8. specs/FEATURE_SPEC_003_obtener_tablero.md
9. BITACORA.md, si ya existe

Si detectas contradicciones, DETENTE y reporta el bloqueo antes de planificar.

## TAREA
Produce un plan en Markdown con esta estructura:

### Parte 1 - Cambios normalizados
Identifica los cambios requeridos y numera CAM-01, CAM-02, CAM-03, etc. Para cada cambio indica capa primaria y referencia del contexto.

### Parte 2 - Diagrama de dependencias
Indica qué pasos dependen de pasos anteriores. Respeta orden topológico: dominio antes que aplicación, aplicación antes que infraestructura.

### Parte 3 - Plan paso a paso
Cada paso debe usar esta plantilla literal:

```
PASO {N} - {Título corto y accionable}
Fase: {Análisis | Dominio | Aplicación | Infraestructura | UI | Pruebas | Documentación}
Cambio normalizado: {CAM-XX}
Referencia de contexto: {INV-XX, AC-XX, ARCHITECTURE.md, TECH_CONSTRAINTS.md}
Capas afectadas: {Dominio | Aplicación | Infraestructura | Presentación}
Archivos a crear o modificar:
Validación:
Criterio de aceptación:
Riesgo arquitectónico:
```

## RESTRICCIONES DURAS
- Cada paso debe poder revertirse con un solo git revert.
- Cada paso debe referenciar al menos un identificador del paquete de contexto.
- Si un paso no puede justificarse, omítelo.
- No propongas tecnologías no autorizadas.
- No cambies el alcance del proyecto.
- No generes código.

## AUTORIZACIÓN
Termina con una sección llamada "Pendiente de revisión del estudiante". No avances a código hasta que el estudiante apruebe el plan.
