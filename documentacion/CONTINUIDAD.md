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
- Migraciones 0001–0005 aplicadas en PostgreSQL local. Las anteriores permanecen inmutables. Eliminación invalida intentos de extracción/indexación y retira fragmentos/vectores. No hay contraseñas ni llamadas institucionales reales.

## Pruebas y evidencia

Verificación final: 119 backend/PostgreSQL aprobadas sin omisiones, incluido modelo real; Angular 35 aprobadas en 9 archivos. Producción 299,59 kB iniciales, sin advertencias de presupuesto. Ruff check/format check limpios (85 archivos), git diff --check limpio. Advertencias conocidas: Starlette TestClient/HTTPX y pypdf add_js en prueba de rechazo de PDF activo.

Modelo real comprobado en worker con memoria/CPU/timeout limitados; sesión SQL sin transacción activa durante inferencia; persistencia/reproducción de vectores con tolerancia absoluta 1e-6; consulta coseno PostgreSQL e índice HNSW existente. Tres pasajes sintéticos y una consulta en español verifican una preferencia semántica mínima; no constituyen benchmark ni cierre del hito 5. Se cubren autorización/CSRF, errores, vectores inválidos, idempotencia, reconstrucción, recuperación, publicación tardía y eliminación. La primera muestra de exceso de tokens se corrigió porque no excedía realmente 512; ahora el tokenizer confirma el tamaño antes del rechazo.

Navegador: fallo model_unavailable antes de preparar, reintento exitoso después, reconstrucción explícita, fragmento/referencia conservados y detalle persistido después de reiniciar backend. Capturas hito_04_indice_desktop.png y hito_04_indice_mobile.png; tamaño normal restaurado después de 390×844. Segunda preparación verificó/reutilizó ambos artefactos sin descargar. Docker deja tres servicios saludables. Evidencia en pruebas/hito_04_indice.md, pruebas/hito_04_extraccion.md y decisiones 0004/0005.

## Punto exacto de continuación

Hitos 1, 2 mock, 3 y 4 técnicos cerrados con datos sintéticos. Próximo: hito 5, búsqueda semántica/top-k sin LLM. Todavía no existe POST /api/v1/rag/search, proveedores IA ni generación. El indicador del inicio comprueba extensión pgvector; cada documento conserva aparte su estado real de índice.

PDF escaneados requieren OCR pendiente. PDF con fórmulas dibujadas/columnas requiere cotejo; DOCX OfficeMath y ciertos estilos verticales se rechazan para evitar alterar fórmulas. No se afirma validación académica ni autorización de corpus real. Si un fragmento supera tokens, la indexación falla sin truncamiento; reducir segmentación y volver a cargar. Workers síncronos con un cupo por proceso API son adecuados para la demostración local; producción requiere cola y coordinación compartida.

## Próximos pasos

1. Diseñar POST /api/v1/rag/search: consulta validada, top-k limitado, embeddings query compatibles con los vectores publicados y respuesta con fragmento, documento, fuente/offsets, puntuación y versión.
2. Implementar retriever/repositorio con filtros de propietario, documento no eliminado/indexed y modelo/revisión/versión compatibles. No permitir que el cliente elija permisos. Para estudiantes, concretar asignación de corpus/curso antes de abrirles materiales docentes; la propiedad actual no equivale a un catálogo institucional público.
3. Crear corpus y consultas sintéticas de Cálculo Diferencial, contrastar búsqueda exacta con HNSW, verificar permisos/eliminación/estados y documentar recuperación relevante y casos sin evidencia. Mantener validación separada del LLM.
4. Añadir pantalla de búsqueda coherente con estilo UPS y referencias revisables. Cerrar hito 5 con pruebas y evidencia antes de hito 6.
5. Pendientes externos: TI (URLs CAS, callback, atributos, dominios y pruebas), corpus autorizado/rúbrica, administración global de roles, licencia y cuenta/visibilidad GitHub. Proveedores/modelos/presupuesto/credenciales se eligen antes del hito 6. Producción requiere aislamiento, retención y limpieza de archivos huérfanos.

## Git y cómo retomar

Repositorio C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero. Rama feature/vector-index, basada en e26dc06 (extracción), precedido por 019c56b (navegación), 31270c6 (corpus/UPS), 82fabe6 (autenticación) y c7db36d (base). El bloque se guarda en commit descriptivo; consultar git log -1 para su identificador. Sin remoto GitHub.

Leer AGENTS.md, este archivo, PLAN_DE_TRABAJO.md y decisiones 0002/0004/0005. Revisar git status antes de editar y preservar cambios existentes. Ejecutar docker compose up -d --build --wait desde raíz sin imprimir secretos ni eliminar volúmenes. Los pesos actuales ya están preparados; si el volumen aún no existe, ejecutar docker compose --profile embeddings run --no-deps --rm prepare-embeddings. No repetir verificaciones ya cerradas sin cambios que lo justifiquen.

## Estado local al cerrar

Backend, frontend y postgres saludables; migración al día. Navegador abierto en /documentos con detalle del docente ficticio, un fragmento y «Índice vectorial listo». .env permanece intacto (selector original student); la sesión docente previa sigue vigente hasta logout/expiración, y un acceso nuevo usa el selector del .env. No se borró la muestra ni se usaron credenciales UPS. Modelo y documentos permanecen en volúmenes privados; no se incluyen en Git. La inferencia local no necesita claves de IA.
