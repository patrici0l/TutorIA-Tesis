# Contratos internos de contenidos — preparación

No se publican todavía /content/generate, /content/explanation, /content/quiz ni /content/feedback. La interfaz pública y respuestas HTTP se implementarán con el coordinador de generación; Gemini permanece desactivado por decisión del autor. No hay contenido ficticio en el producto.

## ContentRequest

| Campo | Regla |
|---|---|
| topic | Texto no vacío, hasta 160 caracteres |
| learning_objective | Texto no vacío, hasta 400 caracteres |
| resource_type | EXPLANATION, EXERCISE, QUIZ o FEEDBACK |
| difficulty | basic por defecto; intermediate/advanced admitidos |
| question_count | Solo QUIZ, entero 1–5; tres por defecto |
| student_answer | Solo FEEDBACK, obligatoria, hasta 2000 caracteres |

Entrada normalizada a NFC, sin controles no textuales/surrogates ni campos extra. Dificultad manual; student_profile, owner_id, provider, model y claves no se admiten. El propietario proviene de sesión en el futuro router, no del JSON del navegador. Student_answer no implica identificar a un estudiante; perfiles reales quedan para hito 8.

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

Códigos internos: content_no_sources, content_invalid_sources, content_context_limit, content_invalid_output, content_wrong_resource, content_quiz_count, content_invalid_citations, content_insufficient_sources, content_target_mismatch, content_trace_unavailable, content_invalid_error_code. El mapeo HTTP queda pendiente; generation_interrupted está reservado para cerrar una preparación interrumpida explícitamente.

No hay recursos reales, historial HTTP, cálculo de costo, perfiles ni adaptación por rendimiento en este bloque. Ver decisión 0008 para retención/purga y estado exacto de los hitos.
