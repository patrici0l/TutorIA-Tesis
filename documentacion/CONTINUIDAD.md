# Continuidad de TutorIA-Lucero

## Estado vigente — 9 de octubre, auditoría por recurso

El 8 de octubre se implementó y probó el objeto audit del detalle del historial y un
desplegable Angular con fechas, proveedor/modelo, uso parcial, latencia, costo nullable,
código seguro, versión/hash de prompt y metadatos de recuperación. Lectura propia sin
inferencias ni errores crudos. 296 backend (32.44 s), 61 Angular/16 archivos (10.92 s),
Ruff limpio, build inicial 306.23 kB/preparación lazy 34.55 kB. Navegador verificó recurso
intermedio, fallo llm_timeout y alto aún preparado; móvil sin desbordamiento. Evidencia
pruebas/hito_10_auditoria.md y api/auditoria_recursos.md. El 9 se reanudó el cierre documental;
Docker estaba detenido y se inició conservando volúmenes. No repetir suites aprobadas si
solo se añade documentación. Cerrar este punto con commit y registrar en bitácora privada.

Próximo paso: comprobar cuota UTC actual/estado preparado y generar una vez el alto
32960f76-5d6d-43b7-9e9b-8d552c9970ed; actualizar la comparación con separación temporal.
Después retención/purga segura (el cupo depende de trazas: no borrarlas sin conservar
un registro independiente de reservas), estimación de costo versionada y benchmark.
CAS/corpus institucional/evaluación académica siguen pendientes de parámetros/autorización.
La sección de métricas del 8 es antecedente, cerrada en 31d3e6b.

## Estado vigente — continuación del 8 de octubre, métricas

Punto técnico cerrado: GET `/api/v1/metrics` y Angular `/metricas`, navegación docente,
resumen privado de todo el historial propio mediante una sola agregación SQL. Conteos de
estados, reservas y trazas separados; tokens y latencia con cobertura explícita/null;
solo cobertura de estimación de costo, sin tarifas ni verificación de facturación. No hubo
nuevas llamadas Gemini, cambios de cupo, migraciones ni modificación de credenciales.
Backend 295 pruebas aprobadas (29.51 s), Angular 59/15 archivos (54.04 s), Ruff limpio,
build Docker inicial 306.23 kB y métricas lazy 9.51 kB; Compose saludable. Navegador:
12 preparaciones, 4 prepared/0 generating/7 succeeded/1 failed, 8 trazas y 6 reservas,
9985 tokens totales conocidos en 7 trazas/1 sin dato, latencia promedio 4515.14 ms,
8 costos sin estimación. Actualización explícita y móvil sin desbordamiento verificados.
Evidencia `pruebas/hito_10_metricas.md`, contrato `api/metricas.md`, decisión 0011.

La bitácora personal se mantiene en seguimiento_privado/BITACORA.md, excluida y sin archivos
versionados. Cerrar este punto con commit feat descriptivo y registrar hash únicamente en
bitácora privada. Rama feature/resource-preparation, sin remoto.

Próximo paso: cuando se renueve el cupo UTC 9 (8 de octubre 19:00 Guayaquil), recuperar del
historial la preparación alta 32960f76-5d6d-43b7-9e9b-8d552c9970ed, verificar límites/modelo,
enviar una sola vez y completar evidencia de comparación. Sigue sin enviar al cerrar este
bloque anterior a las 19:00. No aumentar cuota ni repetir bajo/medio. Después completar
metadatos de trazabilidad consultables por recurso y política de retención/purga antes de
datos reales. Estimación monetaria necesita precio/moneda/versionado; benchmark/cierre/CAS
TI pendientes. Las secciones históricas siguientes se conservan como antecedentes; esta
sección reemplaza sus referencias a métricas aún no implementadas. No declarar hito 9
académico ni hito 10 completo.

Actualizado: 8 de octubre de 2026, America/Guayaquil. Estado vigente al registrar dos salidas adaptadas reales y bitácora privada. No se dispone de un porcentaje fiable de tokens restantes; no se inventa uno.

## Instrucciones vigentes

El autor pide itinerario personal por día/sesión en seguimiento_privado/BITACORA.md, excluido de Git/GitHub. Actualizar con trabajo, verificación, pendientes y commits; no copiar su contenido privado a documentación pública. Hacer commit al cerrar cada punto verificable, sin declarar hitos incompletos como terminados. Exclusión y regla persistente comprobadas en 05b7cec.

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
- Generación API/UI conectada: /recursos → preparar/revisar fuentes → botón explícito → POST /api/v1/content/{id}/generate → una llamada → validación → recurso/fallo. Los cuatro contratos mínimos confirmados realmente desde Angular con material sintético, citas y persistencia. Roles/propiedad/CSRF, no-store, cuerpo vacío sin configuración cliente y máximo 16 KiB.
- Trazabilidad: prepared→generating→succeeded/failed, reserva persistida antes de red, cierre condicional, snapshots/modelo/consumo conocido o null. Migraciones 0001–0009 aplicadas, anteriores inmutables. Historial privado HTTP con adaptación implementado; métricas académicas/costo calculado pendientes.
- Hito 8 técnico: POST /profiles, GET /profiles y GET /profiles/{id}; observaciones sintéticas inmutables privadas por creador teacher/admin, campos estrictos y versión performance-profile-v1. Angular /perfiles guarda, lista y abre detalle. Porcentaje/dominio/apoyo informados, sin calcular notas ni vincular usuarios reales; integración externa institucional pendiente. Ver api/perfiles.md y decisión 0009.
- Hito 9 preparación: profile_id propio opcional en /content/prepare, mismo tema requerido; dominio low→basic/pasos, medium→intermediate/práctica y high→advanced/complejidad. Foco en etiquetas de errores sin inferir gravedad. Tipo de recurso elegido por docente, alternativas sugeridas. Snapshot completo y política profile-adaptation-v1, prompt educational-rag-profile-v2; manual v1 compatible. Migración 0009 aplicada. Angular selecciona perfiles paginados, explica ajuste y restaura decisión histórica. No transmite perfil completo/identificadores a Gemini ni calcula notas. Diferencias de salidas reales y evaluación pedagógica pendientes.

## Límites y estado local

.env privado: LLM_ENABLED=true, LLM_FREE_TIER_CONFIRMED=true, LLM_DAILY_REQUEST_LIMIT=5, gemini-3.1-flash-lite, una petición/minuto, entrada 12000 caracteres, salida 512 tokens, timeout 30 s. Plantilla con activación/confirmación false. Secretos excluidos de Git.

La ruta reserva cinco intentos globales por día UTC en PostgreSQL, incluidos fallos; una llamada simultánea y 60 s entre inicios. Reiniciar Docker no restaura el cupo. Preparación de un solo envío; terminal inmutable. Intentos abiertos >90 s se cierran como interrumpidos al reclamar otra preparación, sin reenvío. Documentos deben seguir disponibles para su propietario. Scripts manuales y otros clientes de la clave NO pasan por este cupo API. Limita solicitudes, no verifica facturación ni impone tope monetario en Google.

Docker backend/frontend/postgres saludable; datos/modelos conservados. Navegador /recursos con sesión docente ficticia renovada y preparación adaptada recuperada; selector de nuevos accesos restaurado a student. CAS no conectado. Sin contenido en localStorage; tras recargar se consulta la lista para reabrir recursos o perfiles conservados en PostgreSQL.

## Pruebas y evidencia

Última suite: 292 backend/PostgreSQL aprobadas en 35,36 s, dos advertencias conocidas Starlette/HTTPX y pypdf; 56 Angular en 14 archivos. Ruff check/format limpios, 148 archivos; build sin advertencias, 305,75 kB inicial y 28,93 kB módulo preparación. Tests automáticos sin Gemini. Doce combinaciones recurso/nivel y generación sobre prompt adaptado conservado con proveedor ficticio comprobadas. Preparación 07cc9201-5d1d-4ab5-8bd1-76bf1f3fb225, perfil 5bb5b546-d9bb-49b6-ada5-f26528952c01: advanced→basic, política/motivo/foco restaurados tras recargar. Capturas y SQL en pruebas/hito_09_personalizacion.md; ninguna llamada Gemini en este bloque. Conservar evidencia previa pruebas/hito_08_perfiles.md.

Prueba Angular real sintética: e4fcd956-cdf4-43a1-8487-d82997e096b3, succeeded, gemini-3.1-flash-lite, S1, 1076 input/312 output/1388 total, 2355 ms. Reserva 2026-10-07 22:06:57 UTC y persistencia SQL confirmadas. Una llamada en este bloque; costo desconocido/null, no afirmar cargo medido cero. Evidencia pruebas/hito_07_generacion_ui.md y capturas hito_07_generacion_desktop.png / mobile.png. Móvil 390×844 solicitado, ancho DOM útil/scrollWidth 375 px sin desbordamiento, viewport restaurado.

Pruebas anteriores: conexión 55 tokens en pruebas/hito_06_gemini_real.md; coordinador RAG con timeout registrado y posterior éxito 1403 tokens en pruebas/hito_07_coordinador.md / hito_07_generacion_real.json. 2.5 Flash-Lite recibió 404; sin fallback/reintento automático ni causa inventada.

Evaluación RAG calculo-sintetico-v1: recall@3 base 0,875; alias explícitos mejoraron a 1 y MRR@3=0,9375 en la misma muestra que motivó el ajuste. No es validación independiente ni medición a escala. Reporte pruebas/hito_05_recuperacion.json. Conservar evidencia anterior de extracción, embeddings, permisos, CSRF, idempotencia y publicación tardía.

## Punto exacto siguiente

Hito 7: cuatro recorridos mínimos reales e historial privado comprobados; validación académica pendiente. Hito 8 sintético técnico terminado; hito 9 implementación disponible y comparación real parcial registrada. Próximo bloque: recuperar la preparación alta 32960f76-5d6d-43b7-9e9b-8d552c9970ed desde historial y completar esa comparación cuando el cupo lo permita, sin recrear preparaciones ni reintentar bajo/medio. UTC 8 termina en cinco inicios (tres anteriores + dos actuales). Renovación UTC 9: 8 de octubre a las 19:00 de Guayaquil; no hay ejecución programada. Verificar modelo/límites y documentar separación temporal. Después hito 10: métricas privadas de estados/latencia/tokens con null/desconocido explícito, sin inventar costo ni notas, y retención antes de datos reales. Nunca llamadas externas en suites/healthchecks/arranque.

Comparación actual: c00981b5-8f00-4e76-87fe-c4384ab11d47 (low, succeeded, 1161/381/1542 tokens, 1951 ms) y 39f18cd0-5529-4e25-a025-81f098d56033 (medium, succeeded, 1154/339/1493, 1999 ms), ambas 3.1 Flash-Lite/S1 con fuentes y datos fijos iguales. Dos salidas recuperadas tras recargar sin nuevas llamadas. Limitación: ambas añaden regla general de potencia no expresada en fuente; diferencias pequeñas, sin beneficio académico probado. Preservar protocolo/evidencia en pruebas/hito_09_comparacion_parcial.md y JSON. No cambiar esta muestra retrospectivamente; futuros corpus/rúbricas se documentarán por separado. Cambio UI únicamente informativo, build aprobado; las suites funcionales anteriores siguen siendo 292/56 y no se han repetido en este bloque.

Pendientes: validación académica con corpus/rúbrica autorizados y consultas independientes; integración externa de perfiles, vocabularios, idempotencia y política de datos; evaluación de salidas adaptadas hito 9; métricas/retención/purga e historial completo hito 10; benchmark comparativo/proveedores restantes hito 11; endurecimiento/manuales/informe hito 12; CAS TI, administración global de roles/asignación de corpus estudiantil. PDF escaneados necesitan OCR, fórmulas/columnas requieren cotejo, OfficeMath se rechaza. Producción requiere cola/aislamiento/retención/limpieza de huérfanos. Snapshots conservan texto tras borrar documentos: definir purga antes de datos reales. Licencia y cuenta/visibilidad GitHub pendientes.

## Git y cómo retomar

Repositorio C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero, rama feature/resource-preparation, sin remoto/publicación. Bloques previos 8f2e735 (historial), 33dc800 (documentación), 2f723ac (cuatro recursos reales) y 2cb6b21 (perfiles); adaptación en commit descriptivo (git log -1). Revisar git status y preservar cambios.

Leer AGENTS.md, README.md, PLAN_DE_TRABAJO.md, decisiones 0002/0004/0005/0006/0007/0008/0009/0010 y api/contenidos.md / perfiles.md / personalizacion.md / limites_gemini.md. Levantar con docker compose up -d --build --wait sin imprimir secretos, sin docker compose config ni eliminar volúmenes. Si faltan pesos: docker compose --profile embeddings run --no-deps --rm prepare-embeddings. No repetir verificaciones cerradas sin cambios/fallos que lo justifiquen.

## Evidencia conservada: contratos de recursos

7 de octubre, sesión nocturna: Docker Desktop se inició tras encontrar el motor detenido; datos/modelos conservados. Sesión docente ficticia renovada, selector de nuevos logins restaurado a student. 50 pruebas Angular aprobadas en 13 archivos, incluidas presentación de ejercicio/quiz/feedback; backend conserva 247 aprobadas (sin cambios backend posteriores).

Ejercicio real 34cbaee3-9dbe-40f6-a41b-65e3568d606b: succeeded, 1115 input/324 output/1439 total, 2088 ms, S1. Quiz real de una pregunta 42289db1-b80a-4290-b7bd-b26d1b03b845: succeeded, 1168 input/222 output/1390 total, 7516 ms, S1, cuatro opciones y respuesta desplegable comprobadas. Feedback 77754fbb-be92-4495-bdae-781db4a6b964 también succeeded: 1080 input/250 output/1330 total, 14146 ms, S1. Tres llamadas nuevas completadas, cupo UTC del 8 de octubre (fecha local 7), anterior llamada UI en día UTC previo. Los tres se recuperaron desde historial sin inferencia. Evidencia pruebas/hito_07_cuatro_recursos.md y recursos_reales.json. Pruebas externas de estos contratos cerradas: no repetirlas automáticamente. No reenvío ni gasto verificado.
