# Continuidad de TutorIA-Lucero

Actualizado: 6 de octubre de 2026. Se conserva el estado al cerrar cada bloque y antes de una interrupción o reducción de contexto. No se dispone de un porcentaje fiable de tokens restantes; no se inventa uno.

## Instrucciones vigentes

El plan original continúa como base. La actualización directa del autor reemplaza autenticación local/Google y registro abierto por SSO/CAS UPS, modos mock/cas y cookie HttpOnly/SameSite. Angular no solicita contraseñas ni almacena tokens. CAS real no se conecta hasta recibir parámetros autorizados por TI. Se mantienen Angular, FastAPI, PostgreSQL/pgvector, Alembic y Docker. Paleta azul/amarillo/blanco relacionada con UPS y navegación superior interactiva/responsiva, con movimiento reducido. Consultar decisiones 0002/0003 y arquitectura/navegacion.md.

## Qué tenemos terminado

- Hito 1: estructura modular, FastAPI, health real, Angular, Docker, Alembic y pgvector; arranque conjunto comprobado.
- Hito 2 local: cuatro rutas auth, estado ligado al navegador de un solo uso, sesión opaca persistida por hash, expiración/revocación, alta/actualización automática y conservación del rol. Usuario institucional sin contraseña. Adaptador CAS preparado, URLs vacías hasta TI.
- Hito 3: carga PDF/DOCX/TXT hasta 10 MiB, validación estructural, biblioteca paginada, detalle y eliminación de documentos propios; teacher/admin y propietario comprobados. Bytes privados en document_data.
- Navegación: cabecera superior, pestañas con scroll, desplegable Explorar animado, foco/Escape, roles, responsive y movimiento reducido; estilo UPS.
- Hito 4: extracción/normalización/segmentación real en worker separado, referencias de página/párrafo, offsets Unicode y SHA-256 de unidad. Fragmentos paginados en Angular, estados/errores/reintentos persistidos, recuperación tras interrupción, publicación atómica e idempotencia.
- Hito 4, indexación: modelo local intfloat/multilingual-e5-small ONNX CPU, 384 dimensiones, revisión 614241f622f53c4eeff9890bdc4f31cfecc418b3, versión e5-onnx-v1. Pesos/tokenizer verificados por SHA-256 en embedding_data; inferencia sin red. Prefijos query:/passage:, pooling enmascarado y L2, hasta 512 tokens sin truncamiento. Vectores y token counts en pgvector, índice HNSW coseno. Preparar/reintentar/reconstruir desde Angular conservando texto y referencias. Modelo/revisión/versión/fecha persistidos.
- Hito 5 técnico: POST /api/v1/rag/search y pantalla /busqueda. Recuperación exacta con fuentes, top-k limitado y filtros de propiedad/estados/modelo; teacher/admin sobre corpus propio. Vocabulario matemático explícito versionado; cupo de worker compartido con indexación. HNSW contrastado con referencia exacta en muestra sintética. No hay LLM.
- Migraciones 0001–0005 aplicadas en PostgreSQL local. Las anteriores permanecen inmutables. Eliminación invalida intentos de extracción/indexación y retira fragmentos/vectores. No hay contraseñas ni llamadas institucionales reales.

## Pruebas y evidencia

Verificación final: 138 backend/PostgreSQL aprobadas sin omisiones, incluido modelo real y recuperación; Angular 38 aprobadas en 10 archivos. Compilación de producción aprobada sin advertencias de presupuesto. Ruff check/format check limpios (92 archivos), git diff --check limpio. Advertencias conocidas: Starlette TestClient/HTTPX y pypdf add_js en prueba de PDF activo.

Modelo real comprobado en worker con memoria/CPU/timeout limitados; sesión SQL sin transacción activa durante inferencia; persistencia/reproducción de vectores con tolerancia absoluta 1e-6; consulta coseno PostgreSQL e índice HNSW existente. Tres pasajes sintéticos y una consulta en español verifican una preferencia semántica mínima; no constituyen benchmark ni cierre del hito 5. Se cubren autorización/CSRF, errores, vectores inválidos, idempotencia, reconstrucción, recuperación, publicación tardía y eliminación. La primera muestra de exceso de tokens se corrigió porque no excedía realmente 512; ahora el tokenizer confirma el tamaño antes del rechazo.

Evaluación RAG calculo-sintetico-v1: ocho fuentes/consultas. Base E5 pura: top-1 y recall@3=0,875; la consulta de división no encontró cociente en top-3. Normalización explícita division/dividir→cociente y multiplicación/multiplicar→producto (calculo-alias-v1) recuperó ocho fuentes en top-3, siete primeras; MRR@3=0,9375, cociente en segundo lugar. Consultas/corpus no se cambiaron. Reporte antes/después: pruebas/hito_05_recuperacion.json. La misma muestra motivó el ajuste: no es validación independiente ni benchmark académico. HNSW ef_search=80, iterative_scan=strict_order, plan confirmado y coincidencia con top-3 exacto en ocho consultas. No se mide velocidad a escala.

Navegador: búsqueda real de tasa de cambio → fuente de derivadas con similitud 0,851, párrafo 1, texto y referencia verificable; filtro 1 → cero coincidencias, sin generar una respuesta. Vista móvil 390×844 verificada, pestaña activa visible tras su transición y texto legible; tamaño normal restaurado. Capturas hito_05_busqueda_desktop.png y hito_05_busqueda_mobile.png. Continúa evidencia previa de indexación/reconstrucción/persistencia. Al reanudar estaban detenidos los contenedores; se levantaron conservando volúmenes y se comprobó búsqueda con los mismos documentos/modelo. Docker deja tres servicios saludables. .env intacto; sin claves de IA ni credenciales reales. Evidencia en pruebas/hito_05.md y decisión 0006.

## Punto exacto de continuación

Hitos 1, 2 mock, 3, 4 y 5 técnicos cerrados con datos sintéticos. Próximo: hito 6, interfaz/fábrica de proveedores IA y sus límites. Todavía no hay adaptadores LLM, proveedor real configurado ni generación. RAG ya funciona sobre corpus propio docente; no se ha habilitado corpus para estudiantes. El indicador del inicio comprueba pgvector; cada documento conserva aparte su índice real. La evaluación académica sigue pendiente de corpus/rúbrica autorizados y consultas independientes.

PDF escaneados requieren OCR pendiente. PDF con fórmulas dibujadas/columnas requiere cotejo; DOCX OfficeMath y ciertos estilos verticales se rechazan para evitar alterar fórmulas. No se afirma validación académica ni autorización de corpus real. Si un fragmento supera tokens, la indexación falla sin truncamiento; reducir segmentación y volver a cargar. Workers síncronos con un cupo por proceso API son adecuados para la demostración local; producción requiere cola y coordinación compartida.

## Próximos pasos

1. Diseñar interfaz generate, esquemas de entrada/salida, fábrica y configuración de proveedores (plan: OpenAI/Gemini/Claude), con modelo explícito, timeout, errores y límites. No conectar a proveedores externos ni consumir presupuesto sin escoger proveedor/modelo y disponer de configuración local autorizada.
2. Preparar contratos y pruebas de adaptadores con respuestas de prueba identificadas como tales, fuera del producto. No presentar una respuesta simulada como contenido generado real. Mantener lógica fuera de routers y claves exclusivamente en .env/backend.
3. Concretar proveedor inicial, modelos, presupuesto y credenciales antes de una integración real. Nunca pedir que se peguen secretos en el chat ni guardarlos en Angular/Git. Guardar trazabilidad mínima antes de la primera generación real; ampliar en hito 10.
4. Validar recuperación con consultas independientes y corpus/rúbrica autorizados. El ajuste de vocabulario actual se evaluó en la misma muestra que lo motivó. Similaridad no implica certeza; corpus grande y HNSW requieren medición de recall/rendimiento y coordinación de workers.
5. Pendientes externos: TI (URLs CAS, callback, atributos, dominios y pruebas), corpus autorizado/rúbrica, administración global de roles y asignación curso/corpus para estudiantes, licencia y cuenta/visibilidad GitHub. Producción requiere cola, aislamiento, retención y limpieza de archivos huérfanos.

## Git y cómo retomar

Repositorio C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero. Rama feature/rag-search, basada en 21d4d3a (embeddings/indexación), precedido por e26dc06 (extracción), precedido por 019c56b (navegación), 31270c6 (corpus/UPS), 82fabe6 (autenticación) y c7db36d (base). El bloque se guarda en commit descriptivo; consultar git log -1 para su identificador. Sin remoto GitHub.

Leer AGENTS.md, este archivo, PLAN_DE_TRABAJO.md y decisiones 0002/0004/0005/0006 y api/rag.md. Revisar git status antes de editar y preservar cambios existentes. Ejecutar docker compose up -d --build --wait desde raíz sin imprimir secretos ni eliminar volúmenes. Los pesos actuales ya están preparados; si el volumen aún no existe, ejecutar docker compose --profile embeddings run --no-deps --rm prepare-embeddings. No repetir verificaciones ya cerradas sin cambios que lo justifiquen.

## Estado local al cerrar

Backend, frontend y postgres saludables; migración 0005 al día, sin nueva migración ni alteración de las aplicadas. Navegador abierto en /busqueda con resultado del docente ficticio y fuente de derivadas. .env permanece intacto (selector original student); la sesión docente previa sigue vigente hasta logout/expiración, y un acceso nuevo usa el selector del .env. No se borró la muestra ni se usaron credenciales UPS. Modelo y documentos permanecen en volúmenes privados, fuera de Git. Las consultas/resultados no se guardan en localStorage ni en historial. Capturas y reporte contienen únicamente datos sintéticos.
