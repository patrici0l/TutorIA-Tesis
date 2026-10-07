# Seguimiento del plan de implementación

Fuente rectora: Plan_Implementacion_TutorIA-Lucero.docx, entregado por el autor el 4 de octubre de 2026. Su extracción en orden, incluidas tablas, está en `investigacion/plan_implementacion_fuente.txt`. Los documentos previos se usan como contexto; no se modifican. No se interpretan ejemplos de código como funciones ya implementadas.

## Bloque actual

Hitos 1, 3 y 4 cerrados técnicamente con material sintético; estilo ajustado a colores UPS. Extracción, normalización, segmentación, revisión de fuentes y embeddings locales reproducibles en pgvector implementados; evidencia en `pruebas/hito_04_extraccion.md` y `pruebas/hito_04_indice.md`. Hito 5 técnico completado con búsqueda exacta, permisos, fuentes y comparación HNSW en corpus sintético; evidencia en pruebas/hito_05.md. Hito 6 parcialmente preparado: interfaz/fábrica/adaptador Gemini y pruebas sin red; conexión real desactivada por indicación del autor. Hito 2 implementado en modo mock y con adaptador CAS preparado; integración institucional pendiente de TI. Las verificaciones están en `pruebas/hito_01.md` y `pruebas/hito_02.md`. La instrucción directa del autor del 5 de octubre de 2026 reemplaza el login tradicional/JWT del documento por SSO/CAS y sesiones opacas HttpOnly; la fuente original se conserva íntegra. No dar por completados los siguientes hitos por haber creado sus carpetas.

| Paso | Entregable | Evidencia prevista |
|---|---|---|
| 1 | Repositorio TutorIA-Lucero | Git local, sin remoto aún |
| 2 | .gitignore y .env.example | Exclusión de secretos comprobada |
| 3 | Carpetas y README | Estructura raíz y guía de ejecución |
| 4 | FastAPI inicializado | app/main.py y dependencias fijadas |
| 5 | GET /api/v1/health | Contratos 200 y 503, OpenAPI |
| 6 | PostgreSQL y pgvector | Servicio Docker y consulta vectorial |
| 7 | Alembic | Migración 0001_enable_vector |
| 8 | Angular | Compilación de producción |
| 9 | Layout y rutas | /inicio y navegación accesible |
| 10 | SCSS y animaciones | Animación compartida y reduced-motion |
| 11 | Dockerfile backend | Imagen ejecutada sin root |
| 12 | Dockerfile frontend | Compilación multietapa y nginx |
| 13 | Compose | Volumen, healthchecks y orden de arranque |
| 14 | Angular consulta health | Pantalla con respuesta real y reintento |
| 15 | FastAPI consulta PostgreSQL | SELECT 1, extensión y prueba de integración |

## Secuencia obligatoria de hitos

| Hito | Alcance | Criterio de cierre | Estado |
|---|---|---|---|
| 1 Base | Preparación, backend, BD, frontend, Docker | Un comando levanta todo; interfaz confirma API y BD real | Completado |
| 2 Seguridad | SSO/CAS, usuarios institucionales, sesión HttpOnly, logout, roles, guards e interceptores | Acceso mock y rechazo de sesiones inválidas probados; integración UPS autorizada por TI | Mock completado; CAS pendiente de TI |
| 3 Corpus | PDF/DOCX/TXT, MIME/extensión/tamaño, permisos y gestión | Cargar, listar, consultar y eliminar documentos propios | Completado |
| 4 Ingesta | Extracción, normalización, segmentación, embeddings e índices | Corpus trazable y reproducible en pgvector | Completado técnicamente con material sintético |
| 5 RAG | Búsqueda semántica y top-k | Recuperación validada con corpus y consultas de referencia, sin LLM | Completado técnicamente con muestra sintética; validación independiente pendiente |
| 6 IA | Interfaz generate, fábrica y primer proveedor | Proveedor intercambiable, errores y límites controlados | Interfaz/fábrica/Gemini preparados y probados sin red; conexión real desactivada por el autor |
| 7 Recursos | Explicación, ejercicio, quiz y feedback | Flujo completo por recurso, fuentes y validación | Contratos/prompts/validación y preparación interna listos; API/UI y generación real pendientes |
| 8 Perfiles | Recepción por API de rendimiento externo | Validación y persistencia de perfiles sintéticos | Pendiente |
| 9 Personalización | Alto, medio, dificultades y dificultad localizada | Diferencias justificadas para mismo tema y distintos perfiles | Pendiente |
| 10 Trazabilidad | Fuentes, historial y métricas | Reconstrucción de cada generación y sus fallos | Base de snapshots y estados preparada por migración 0006; historial/métricas/perfiles/costo pendientes |
| 11 Benchmark | Directo/RAG, perfiles, OpenAI/Gemini/Claude | Experimentos controlados y resultados reales registrados | Pendiente |
| 12 Cierre | Endurecimiento, documentación, pruebas y MVP | Evidencia final, manuales e informe | Pendiente |

La tabla de etapas 0–15 de la sección 19 se conserva íntegra en la fuente. Los hitos anteriores agrupan esas etapas sin cambiar el orden. Ejemplos, pistas y retos se amplían después de los recursos iniciales. La segunda asignatura es condicional al tiempo disponible.

## Matriz de cobertura del documento

| Secciones del plan | Requisito | Implementación o destino |
|---|---|---|
| 1–2 | Stack, modularidad, API-first, seguridad y trazabilidad | Arquitectura inicial; continuidad en todos los hitos |
| 3 | Convenciones de idioma | Estructura y AGENTS.md |
| 4–6 | Raíz, backend, módulos, frontend y animaciones | Estructura inicial; cada módulo se implementa en su hito |
| 7 | Variables, secretos y exclusiones | Plantillas, script local y .gitignore |
| 8 | Interfaz LLM, OpenAI, Gemini y Claude | Hito 6: interfaz/fábrica y primer adaptador Gemini; OpenAI/Claude y comparación pendientes |
| 9 | REST/OpenAPI versionada | Health actual; catálogo restante pendiente |
| 10 | Diez entidades iniciales y Alembic | Modelo conceptual; columnas tras validar casos de uso |
| 11–12 | Flujo completo y RAG antes del LLM | Hitos 3–7, validación independiente de recuperación |
| 13 | Perfil externo y variables académicas | Hito 8; campos completos en la fuente |
| 14–15 | Recursos ampliables y personalización | Hito 7: cuatro contratos iniciales preparados, dificultad manual; personalización hito 9 pendiente |
| 16 | Evidencia de cada generación | Base mínima persistida en 0006; historial, perfiles y métricas por completar en hitos 8–10 |
| 17–18 | Docker, Git y GitHub | Docker y Git local; remoto pendiente de cuenta/visibilidad |
| 19–22 | Orden y criterio del primer bloque | Este seguimiento y evidencia de pruebas |
| 23–25 | Pruebas, seguridad y definición de terminado | Aplicar por hito; lista de cierre abajo |
| 26 | Experimentos A/B/C/D | Hito 11; D condicional |
| 27 | Documentación continua | README, arquitectura, BD, API, decisiones, pruebas; ampliar por hito |
| 28–30 | Evitar desorden y avanzar verticalmente | AGENTS.md y revisiones de cada entrega |

## Contratos aún pendientes

Autenticación implementada: GET `/auth/login`, GET `/auth/callback`, GET `/auth/me`, POST `/auth/logout`. Alta automática después de validar la identidad; sin registro por contraseña ni refresh JWT. El rol local se conserva al iniciar sesión. La gestión administrativa de permisos y las políticas institucionales quedan por concretar.

Documentos implementados: POST `/documents/upload`, GET `/documents`, GET y DELETE `/documents/{id}`, POST `/documents/{id}/process`, GET `/documents/{id}/chunks` y POST `/documents/{id}/index` (rebuild=true para reconstruir). Perfiles pendientes: POST `/profiles`, GET `/profiles/{id}`. Recuperación implementada: POST `/rag/search`, restringida al corpus propio teacher/admin.

Generación: POST `/content/generate`, `/content/quiz`, `/content/feedback`, `/content/explanation`, `/content/challenge`. Ejercicios se identificarán por `resource_type=EXERCISE` en el contrato genérico. Historial: GET `/generations` y `/generations/{id}`. Métricas: GET `/metrics`. Todas estas rutas llevarán el prefijo `/api/v1`.

## Campos de trazabilidad exigidos

`student_profile`, `topic`, `learning_objective`, `resource_type`, `difficulty`, `provider`, `model`, `prompt_version`, `retrieved_chunks`, `source_documents`, `latency`, `input_tokens`, `output_tokens`, `estimated_cost`, `created_at`, `status`, `error_detail` cuando corresponda. No registrar secretos. Conservar configuración de benchmark, versiones de prompts y procedimiento de perfiles sintéticos.

## Cierre de cada funcionalidad

- Caso de uso/endpoints implementados con entradas y salidas validadas.
- Lógica fuera del controlador, errores y persistencia cuando corresponda.
- Pruebas adecuadas y contrato OpenAPI actualizado.
- Interfaz con carga, éxito, error y archivos separados.
- Credenciales excluidas, revisión de cambios y commit descriptivo.
- Docker, API y pruebas sin regresiones.

Seguridad vigente: validación CAS en backend, hashes de tokens opacos, expiración y revocación de sesiones, autorización por rol, validación de documentos, no ejecutar cargas, saneamiento según contexto, límites de tamaño/frecuencia de solicitudes LLM y logs sin contenido sensible.

Actualización del hito 6: Gemini elegido directamente por el autor. Interfaz `generate`, fábrica, esquemas de texto/metadata, adaptador REST y límites implementados con pruebas de transporte ficticio. El autor pidió dejar la conexión real para después: LLM_ENABLED=false, sin llamadas/gasto y sin endpoint de generación todavía. El criterio de integración real del hito 6 permanece pendiente. No se salta a recursos generados de hito 7; puede prepararse su diseño y trazabilidad sin invocar el proveedor. Ver decisión 0007 y pruebas/hito_06_proveedores.md.

Preparación del hito 7 implementada: ContentRequest, cuatro esquemas discriminados, prompts educational-rag-v1, referencias S1…S10 y validación de JSON/citas. PrepareContentService usa recuperación propia top-3 sin llamada LLM. Migración 0006 y repositorio/servicio de trazabilidad guardan prompt/fuentes/solicitud y estados antes de una futura llamada; cierre condicional por propietario impide sobrescritura terminal. No hay perfil ni adaptación automática ni rutas content/historial todavía. 223 pruebas backend aprobadas; evidencia pruebas/hito_07_preparacion.md. No se declara hito 7/10 completo ni evaluación académica.

## Decisiones académicas y externas por concretar

Seleccionar corpus docente autorizado y rúbrica antes de RAG y evaluación. TI debe confirmar endpoints, atributos, callback, dominios y entorno CAS; el alta institucional automática ya está definida. Concretar administración de roles y corpus docente autorizado antes de usar datos reales. El hito 3 verifica propiedad con los roles locales existentes. Elegir licencia y cuenta/visibilidad de GitHub antes de publicación. Elegir modelos, presupuesto y credenciales de proveedores antes del hito 6. Estas decisiones no impiden construir y probar la base técnica. No se inventan aprobaciones del tutor, resultados experimentales ni fechas del cronograma.
