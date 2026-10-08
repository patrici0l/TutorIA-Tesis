# Contratos de contenidos — preparación

POST `/api/v1/content/prepare` y Angular `/recursos` permiten preparar solicitudes y revisar fuentes propias sin invocar IA. No se publican todavía /content/generate, /content/explanation, /content/quiz ni /content/feedback. Gemini permanece desactivado; la generación real requiere coordinador, modelo y límite de gasto definidos.

## POST /api/v1/content/prepare

Requiere sesión teacher/admin y protección CSRF mediante el header de cliente existente. ContentRequest es el cuerpo JSON; el propietario procede exclusivamente de la sesión. Máximo 16 KiB antes de parsear y cinco intentos por propietario/minuto/proceso antes de inferencia local o persistencia. En producción se requiere coordinación compartida del cupo.

201 devuelve `id`, `status=prepared`, `topic`, `learning_objective`, `resource_type`, `difficulty`, `question_count` (null salvo quiz) y `sources`. Cada fuente contiene texto, alias `citation_id`, UUID de documento/fragmento, título, nombre de archivo, posición, página/párrafo, offsets, hashes y similitud del contrato SearchHit. No devuelve prompt, instrucciones internas, respuesta a revisar, owner_id, claves ni vectores. Todas las respuestas del módulo llevan Cache-Control: no-store.

| Estado | Significado |
|---|---|
| 401 | Sesión inexistente o inválida |
| 403 | Rol o protección CSRF inválidos |
| 413 | Cuerpo excesivo |
| 422 | Solicitud inválida, ausencia de fuentes o contexto excesivo |
| 429 | Cupo agotado; Retry-After: 60 |
| 503 | Fuentes no verificables, recuperación o preparación no disponible |
| 500 | Error inesperado; el cliente no reintenta automáticamente |

Ruta → PreparationService → PrepareContentService/SearchService/EducationalPromptBuilder → GenerationRepository. Se confirma el snapshot en PostgreSQL antes de responder. Esta operación nunca llama al proveedor, incluso si se cambia LLM_ENABLED. Preparado no significa generado. Aún no hay historial HTTP para recuperar preparaciones tras recargar; el identificador permite verificar el registro guardado y queda preparado para el futuro flujo.

## ContentRequest

| Campo | Regla |
|---|---|
| topic | Texto no vacío, hasta 160 caracteres |
| learning_objective | Texto no vacío, hasta 400 caracteres |
| resource_type | EXPLANATION, EXERCISE, QUIZ o FEEDBACK |
| difficulty | basic por defecto; intermediate/advanced admitidos |
| question_count | Solo QUIZ, entero 1–5; tres por defecto |
| student_answer | Solo FEEDBACK, obligatoria, hasta 2000 caracteres |

Entrada normalizada a NFC, sin controles no textuales/surrogates ni campos extra. Dificultad manual; student_profile, owner_id, provider, model y claves no se admiten. El propietario proviene de sesión, no del JSON del navegador. Student_answer no implica identificar a un estudiante; perfiles reales quedan para hito 8. Angular avisa que la respuesta se guarda en el snapshot y pide usar datos de prueba sin identificadores personales.

## EducationalResource

Un objeto JSON discriminado por resource_type, con title (hasta 160 caracteres) y campos propios:

| Recurso | Campos |
|---|---|
| EXPLANATION | summary, steps (1–8), worked_example |
| EXERCISE | statement, hints (1–3), solution_steps (1–8), answer |
| QUIZ | questions (1–5), cada una con statement, options (cuatro), correct_option (0–3), explanation |
| FEEDBACK | diagnosis, correction, next_step |

Cada campo de texto educativo es CitedText: text (hasta 2000 caracteres) y citations (1–10 alias únicos S1…S10). Opciones quiz son textos distintos de hasta 400 caracteres; no son bloques de fundamentación y no llevan citas propias. El enunciado/explicación sí llevan citas. La cantidad de preguntas coincide con la solicitud. Salida máxima 65 536 caracteres y 262 144 bytes; solo JSON sin claves duplicadas ni envoltura markdown.

Las citas se verifican contra las fuentes recuperadas para esa preparación; no se aceptan UUID/alias inventados. Esto no certifica la exactitud ni respaldo semántico de cada afirmación. title/opciones/textos futuros deben renderizarse por interpolación, nunca como HTML activo. Solicitar ausencia de HTML en el prompt no equivale a un sanitizador.

## Preparación y persistencia internas

PrepareContentService.prepare → recuperación propia top-3 → EducationalPromptBuilder.build → PreparedContent. No llama IA. Se conservan instrucciones/prompt, versión educational-rag-v1, hash canónico, fuentes y metadata de recuperación; fallo por fuentes vacías o contexto excesivo, sin truncamiento silencioso.

GenerationRepository.prepare confirma la evidencia en PostgreSQL y retorna UUID; GenerationTarget opcional viene del backend. Cuando se conecte IA, debe requerirse target explícito y conservar la preparación antes del envío. GenerationTraceService.finish valida la salida y registra éxito o fallo conocido; fail registra un código de error permitido sin cuerpo remoto. Solo propietario+estado prepared permiten finalizar. Lecturas privadas terminan transacción antes de una futura inferencia. No publicar estas funciones como API sin roles/CSRF y límites HTTP.

Códigos internos: content_no_sources, content_invalid_sources, content_context_limit, content_invalid_output, content_wrong_resource, content_quiz_count, content_invalid_citations, content_insufficient_sources, content_target_mismatch, content_trace_unavailable, content_invalid_error_code. PreparationService mapea ausencia de fuentes/contexto a 422 y fuentes inválidas a 503; la generación futura necesitará su propio mapeo. generation_interrupted está reservado para cerrar una preparación interrumpida explícitamente.

No hay recursos reales, historial HTTP, cálculo de costo, perfiles ni adaptación por rendimiento en este bloque. Ver decisión 0008 para retención/purga y estado exacto de los hitos.

## Coordinador interno — 7 de octubre de 2026

GenerateContentService recibe proveedor/target configurados por backend, prepara fuentes del propietario y confirma el snapshot antes del único envío. GenerationTraceService valida y guarda el recurso o fallo conocido. Errores inesperados marcan generation_interrupted antes de propagarse internamente. No reintenta ni usa fallback; no abre red desde el router de preparación. Diez pruebas SQL nuevas cubren cuatro recursos y fallos. Se verificó una explicación real con la muestra sintética y proyecto Free Tier confirmado por el autor, presupuesto USD 0. Evidencia ../pruebas/hito_07_coordinador.md. API/UI de generación, control diario persistente y evaluación de recursos restantes aún pendientes; no presentar esta etapa como hito 7 completo.

## Generación desde una preparación revisada

POST /api/v1/content/{identifier}/generate, UUID y sesión teacher/admin del propietario. Cuerpo ausente o {}; campos extra (modelo/proveedor/prompt/propietario) rechazados 422, cuerpo >16 KiB rechazado 413. CSRF obligatorio y Cache-Control: no-store. El cliente nunca envía fuentes nuevas ni clave.

Respuesta 200: {id, status: succeeded|failed, resource: EducationalResource|null, message: string|null}. Fallos posteriores al envío se guardan y se informan sin cuerpo remoto/texto parcial. Otros rechazos: 401 sesión ausente, 403 rol/CSRF, 404 preparación ajena/inexistente, 409 ya enviada, 422 documentos fuente no disponibles, 429 cupo global/minuto o llamada en curso, 503 desactivada/configuración inválida. Angular no reintenta; después de pulsar mantiene la preparación como enviada incluso si la respuesta HTTP se pierde o rechaza, para evitar un reenvío incierto.

GenerationClaimRepository toma un bloqueo transaccional PostgreSQL, comprueba estado/propiedad/documentos y cupos, persiste generating/generation_started_at/target y confirma ANTES de red. Máximo LLM_DAILY_REQUEST_LIMIT (5 local) inicios globales por día UTC, incluidos fallos; 60 s entre inicios y una generación simultánea. Timeout local 30 s, una petición, sin fallback. Cada preparación admite un envío; finalización condicional por propietario y estado pending impide sobrescribir terminal. Intentos generating >90 s se cierran como generation_interrupted al reclamar otra preparación; no se reenvían ni se acepta publicación tardía. Migración nueva 0007; 0006 inmutable.

LLM_ENABLED y LLM_FREE_TIER_CONFIRMED deben estar habilitados en backend. La confirmación es una declaración del operador, no una consulta de facturación. Sin historial HTTP todavía: recargar pierde la vista pero conserva snapshot/recurso en BD. Componentes Angular renderizan los cuatro contratos por interpolación. Solo explicación sintética comprobada realmente desde UI; resto de pruebas reales/evaluación académica pendiente. Estado vigente reemplaza las menciones históricas de API/UI pendientes anteriores. Ver ../pruebas/hito_07_generacion_ui.md.

## Historial privado implementado — 7 de octubre de 2026

GET /api/v1/content/history?offset=0&limit=10 devuelve {items,total,offset,limit}; máximo 20 elementos, offset 0–100000 y orden created_at/id descendente estable. Cada resumen: id, topic, resource_type, difficulty, status, created_at, completed_at. GET /api/v1/content/history/{id} devuelve {preparation,status,created_at,completed_at,resource,message}; preparation representa la solicitud/fuentes originales, no el estado actual del envío, indicado por status externo.

Ambas rutas requieren teacher/admin y filtran por propietario, incluso admin. Detalle ajeno/inexistente: mismo 404; UUID/paginación inválidos 422; sesión ausente 401, rol incorrecto 403. Cache-Control: no-store, sin CSRF de escritura en GET. Sin SQL de mutación, búsqueda/embeddings/inferencia ni llamadas a proveedores. Lista no carga prompts/fuentes/recursos completos; respuestas no exponen instrucciones, prompt, owner_id, clave, respuesta de estudiante, vectores ni errores remotos. Detalle devuelve fuentes desde snapshot, aunque el documento original ya no exista; es evidencia histórica, no autorización para reenviar fuentes borradas.

Mis recursos en /recursos permite consultar/actualizar, paginar y abrir. Un recurso final o pendiente se restaura con envío bloqueado; uno prepared puede generarse explícitamente usando el control ya existente. Lectura no tiene polling/reintentos automáticos ni guarda contenido en localStorage. Formulario de nueva preparación permanece independiente. Lectura fallida se puede volver a consultar explícitamente. No hay purga, exportación, métricas académicas ni historial institucional compartido todavía.

Comprobación real de los cuatro contratos mínimos: explicación, ejercicio, quiz de una pregunta y feedback sintético, todos persistidos con citas S1 y recuperables sin inferencia. Ver ../pruebas/hito_07_cuatro_recursos.md. Queda pendiente evaluación académica independiente y escenarios extensos; el límite local 512 tokens no garantiza un quiz largo completo. Se rechaza salida truncada sin reintento automático.
