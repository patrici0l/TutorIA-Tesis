# Hito 9: preparación personalizada y trazabilidad del perfil

8 de octubre de 2026, America/Guayaquil. Implementación técnica de política, preparación y recuperación; evaluación de diferencias en contenido generado pendiente. No se declara terminado el experimento académico.

## Verificaciones

- Backend Docker Python 3.12/PostgreSQL: 292 aprobadas en 35,36 s; dos advertencias conocidas Starlette/HTTPX y pypdf.
- Angular: 56 aprobadas en 14 archivos. Un primer fallo de test por estado asincrónico de ngModel se corrigió esperando estabilización; el estado disabled se confirmó también en navegador.
- Ruff check/format: 148 archivos limpios. Build producción: 305,75 kB inicial, 28,93 kB módulo preparación; sin advertencias. Docker saludable y migración 0009 aplicada sin borrar volúmenes.

Doce casos cruzan los cuatro recursos con low/medium/high sobre el mismo tema, incluso con porcentaje 100: dificultad y orientación derivan del nivel informado, conservan tipo seleccionado y aíslan identificadores del prompt. Otros casos prueban tema incompatible, perfil ausente, foco vacío, compatibilidad manual y rechazo de payload/reglas falsificados. Integración real PostgreSQL comprueba propiedad, snapshot, historial, ausencia de inicio LLM y conservación al crear otro perfil del mismo tema. Angular comprueba envío solo de UUID, dificultad bloqueada y render seguro de etiquetas/restauración sin inferencia.

## Recorrido local

Docente ficticio, perfil SYN-001 / Derivadas / low / regla_potencia, UUID 5bb5b546-d9bb-49b6-ada5-f26528952c01. Se solicitó explicación con dificultad advanced y objetivo “Aplicar la regla de la potencia en una derivada sencilla.”

Preparación: `07cc9201-5d1d-4ab5-8bd1-76bf1f3fb225`. Respuesta basic, política profile-adaptation-v1, motivo de dominio bajo, pasos/pistas y foco localizado, sugerencias Explicación/Ejercicio/Quiz. Fuente S1 del documento sintético existente. SQL confirma status prepared, prompt educational-rag-profile-v2, advanced→basic y generation_started_at null.

Tras recargar, se abrió el registro del historial privado y se recuperó idéntica decisión. Capturas [escritorio](hito_09_adaptacion_desktop.png) y [móvil](hito_09_adaptacion_mobile.png). Móvil solicitado 390×844, ancho DOM y scrollWidth 375 px; sin desbordamiento. Viewport restaurado. Sesión docente ficticia renovada; selector para nuevos accesos restaurado a student.

Sin llamadas Gemini en este bloque, sin cambios a secretos, facturación ni cuotas. Las pruebas verifican diferencias de política/prompt, no calidad de salidas reales ni mejora del aprendizaje. El siguiente recorrido comparará contenido bajo el cupo autorizado y luego completará métricas/experimentos.

Prueba adicional de generación persistida: con documento/perfil ficticios en un savepoint PostgreSQL, se reserva la preparación real, se verifica que las instrucciones/prompt enviados son exactamente los conservados y se publica una respuesta validada mediante un proveedor ficticio de una sola llamada. Estado succeeded y snapshot de adaptación permanecen coherentes. El savepoint se revierte: no consume cuota real ni agrega datos de ensayo al entorno.
