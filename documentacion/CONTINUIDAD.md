# Continuidad de TutorIA-Lucero

Actualizado: 7 de octubre de 2026. Estado vigente al cerrar generación API/UI. No se dispone de un porcentaje fiable de tokens restantes; no se inventa uno.

## Instrucciones vigentes

Seguir el plan por etapas. Las instrucciones directas del autor reemplazan autenticación local/Google y registro abierto por SSO/CAS UPS, modos mock/cas y cookie HttpOnly/SameSite. Angular no solicita contraseñas ni almacena tokens. CAS espera parámetros de TI. Conservar Angular, FastAPI, PostgreSQL/pgvector, Alembic y Docker; interfaz española, paleta UPS azul/amarillo/blanco y navegación superior accesible/responsiva.

Gemini elegido. Presupuesto autorizado USD 0: queda descartada la propuesta de USD 1. El autor mostró AI Studio con Nivel gratuito y autorizó usar la API; se acepta esa confirmación, no es verificación programática de facturación. No activar facturación, comprar créditos ni hacer fallback pagado. Clave configurada en .env: nunca imprimirla/copiarla a Git/pedirla por chat. Solo material sintético en pruebas externas; corpus institucional y perfiles reales requieren autorización/política de datos.

## Qué tenemos

- Hito 1: infraestructura modular, Docker, health, Alembic, Angular y pgvector comprobados.
- Hito 2 local: cuatro rutas auth, estado de navegador de un solo uso, sesión opaca persistida por hash, expiración/revocación, alta/actualización automática y conservación del rol. Usuario sin contraseña, CAS configurable pendiente de TI.
- Hito 3: biblioteca privada teacher/admin PDF/DOCX/TXT, validación, carga hasta 10 MiB, paginación, detalle y eliminación propios.
- Hito 4: extracción en worker, segmentos con página/párrafo, offsets Unicode y SHA-256, publicación atómica/reintentos/recuperación. E5 ONNX CPU local, 384 dimensiones, revisión 614241f622f53c4eeff9890bdc4f31cfecc418b3, e5-onnx-v1; pesos privados en volumen, inferencia sin red, sin truncar >512 tokens.
- Hito 5 técnico: búsqueda exacta propia con top-k/fuentes/filtros, pantalla /busqueda. HNSW contrastado contra referencia exacta en muestra sintética; no equivale a benchmark académico.
- Hito 6 parcial: interfaz LLMProvider, fábrica, adaptador Gemini REST, límites y metadata/errores seguros. gemini-3.1-flash-lite comprobado realmente; OpenAI/Claude pendientes, sin fallback.
- Hito 7 en curso: explicación/ejercicio/quiz/feedback, dificultad manual, quiz 1–5 y respuesta sintética requerida para feedback. Prompt educational-rag-v1, preparación propia top-3, snapshots y validación JSON/citas. Coordinador interno probado con cuatro recursos y fallos.
- Generación API/UI conectada: /recursos → preparar/revisar fuentes → botón explícito → POST /api/v1/content/{id}/generate → una llamada → validación → recurso/fallo. Componentes para cuatro contratos; una explicación real confirmada desde Angular. Roles/propiedad/CSRF, no-store, cuerpo vacío sin configuración cliente y máximo 16 KiB.
- Trazabilidad: prepared→generating→succeeded/failed, reserva persistida antes de red, cierre condicional, snapshots/modelo/consumo conocido o null. Migraciones 0001–0007 aplicadas, anteriores inmutables. Sin historial HTTP, métricas académicas/costo calculado ni adaptación todavía.

## Límites y estado local

.env privado: LLM_ENABLED=true, LLM_FREE_TIER_CONFIRMED=true, LLM_DAILY_REQUEST_LIMIT=5, gemini-3.1-flash-lite, una petición/minuto, entrada 12000 caracteres, salida 512 tokens, timeout 30 s. Plantilla con activación/confirmación false. Secretos excluidos de Git.

La ruta reserva cinco intentos globales por día UTC en PostgreSQL, incluidos fallos; una llamada simultánea y 60 s entre inicios. Reiniciar Docker no restaura el cupo. Preparación de un solo envío; terminal inmutable. Intentos abiertos >90 s se cierran como interrumpidos al reclamar otra preparación, sin reenvío. Documentos deben seguir disponibles para su propietario. Scripts manuales y otros clientes de la clave NO pasan por este cupo API. Limita solicitudes, no verifica facturación ni impone tope monetario en Google.

Docker backend/frontend/postgres saludable; datos/modelos conservados. Navegador /recursos con sesión docente ficticia y explicación real; selector de nuevos accesos sigue student. CAS no conectado. Sin contenido en localStorage; recargar pierde la vista, PostgreSQL conserva el resultado.

## Pruebas y evidencia

Última suite: 244 backend/PostgreSQL aprobadas en 17,41 s, dos advertencias conocidas Starlette/HTTPX y pypdf; 44 Angular en 12 archivos. Ruff check/format limpios, 130 archivos; build sin advertencias, 304,45 kB inicial y 19,14 kB módulo preparación. Tests automáticos sin Gemini.

Prueba Angular real sintética: e4fcd956-cdf4-43a1-8487-d82997e096b3, succeeded, gemini-3.1-flash-lite, S1, 1076 input/312 output/1388 total, 2355 ms. Reserva 2026-10-07 22:06:57 UTC y persistencia SQL confirmadas. Una llamada en este bloque; costo desconocido/null, no afirmar cargo medido cero. Evidencia pruebas/hito_07_generacion_ui.md y capturas hito_07_generacion_desktop.png / mobile.png. Móvil 390×844 solicitado, ancho DOM útil/scrollWidth 375 px sin desbordamiento, viewport restaurado.

Pruebas anteriores: conexión 55 tokens en pruebas/hito_06_gemini_real.md; coordinador RAG con timeout registrado y posterior éxito 1403 tokens en pruebas/hito_07_coordinador.md / hito_07_generacion_real.json. 2.5 Flash-Lite recibió 404; sin fallback/reintento automático ni causa inventada.

Evaluación RAG calculo-sintetico-v1: recall@3 base 0,875; alias explícitos mejoraron a 1 y MRR@3=0,9375 en la misma muestra que motivó el ajuste. No es validación independiente ni medición a escala. Reporte pruebas/hito_05_recuperacion.json. Conservar evidencia anterior de extracción, embeddings, permisos, CSRF, idempotencia y publicación tardía.

## Punto exacto siguiente

Flujo técnico de explicación real conectado; hito 7 NO cerrado. Próximo bloque: historial privado/API para recuperar resultados propios tras recargar, conservando snapshots sin nueva inferencia. Después verificar recorridos reales de ejercicio/quiz/feedback sintéticos dentro del cupo y mejorar presentación matemática según evidencia. Nunca llamadas externas en suites/healthchecks/arranque.

Pendientes: validación académica con corpus/rúbrica autorizados y consultas independientes; perfiles/adaptación hito 8; métricas/retención/purga e historial completo hito 10; CAS TI, administración global de roles/asignación de corpus estudiantil. PDF escaneados necesitan OCR, fórmulas/columnas requieren cotejo, OfficeMath se rechaza. Producción requiere cola/aislamiento/retención/limpieza de huérfanos. Snapshots conservan texto tras borrar documentos: definir purga antes de datos reales. Licencia y cuenta/visibilidad GitHub pendientes.

## Git y cómo retomar

Repositorio C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero, rama feature/resource-preparation, sin remoto/publicación. Bloque previo 7cd2600; este bloque en commit descriptivo (git log -1). Revisar git status y preservar cambios.

Leer AGENTS.md, README.md, PLAN_DE_TRABAJO.md, decisiones 0002/0004/0005/0006/0007/0008 y api/contenidos.md / limites_gemini.md. Levantar con docker compose up -d --build --wait sin imprimir secretos, sin docker compose config ni eliminar volúmenes. Si faltan pesos: docker compose --profile embeddings run --no-deps --rm prepare-embeddings. No repetir verificaciones cerradas sin cambios/fallos que lo justifiquen.
