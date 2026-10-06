# 0005 — Embeddings locales reproducibles

Fecha: 6 de octubre de 2026. Modelo elegido para el desarrollo local: intfloat/multilingual-e5-small. No requiere cuentas de IA ni envía documentos a un proveedor. La calidad académica se evaluará después con corpus y rúbrica autorizados.

## Modelo y ejecución

La [ficha oficial](https://huggingface.co/intfloat/multilingual-e5-small) indica 384 dimensiones, límite de 512 tokens y los prefijos query:/passage:, también para español. Se usa el ONNX publicado por el mismo repositorio, revisión 614241f622f53c4eeff9890bdc4f31cfecc418b3, con ONNX Runtime CPU. No se carga código remoto. Mean pooling sobre attention_mask y normalización L2 siguen la ficha. El tokenizer se carga desde archivo local, sin truncamiento automático.

model_spec.py fija revisión, versión e5-onnx-v1, dimensiones y SHA-256/tamaño de model.onnx y tokenizer.json, obtenidos de los objetos LFS del repositorio oficial en esa revisión. Los dos archivos ocupan aproximadamente 487 MB decimales y permanecen en embedding_data; no se versionan ni incorporan a la imagen. La preparación explícita descarga solo pesos públicos, verifica SHA-256 y publica cada archivo de forma atómica. La inferencia verifica ambos artefactos y no realiza conexiones externas. Repetir la preparación reutiliza archivos válidos.

## Persistencia e intentos

Migración 0005: Vector(384) y embedding_tokens en fragmentos_documento; índice HNSW para distancia coseno. Documentos conservan index_status, index_error, token interno, inicio/fecha, modelo, revisión y versión. El texto, offsets y SHA de extracción no cambian al indexar.

POST /documents/{id}/index exige propietario teacher/admin y cabecera CSRF. indexed es idempotente para la misma versión. rebuild=true permite reconstrucción explícita de vectores conservando IDs/texto de fragmentos. Durante reconstrucción index_status=indexing; un fallo no deja un índice marcado listo ni mezcla vectores parciales. Los vectores anteriores pueden conservarse hasta publicar el reemplazo, pero solo un documento indexed podrá participar en futura recuperación. La selección RAG deberá filtrar estado, propietario y revisión/modelo, nunca confiar en permisos del cliente.

La reclamación SQL condicional asigna token y admite reintento tras cinco minutos si quedó interrumpida. Una publicación tardía no modifica un intento nuevo o documento eliminado. Documento y vectores se actualizan en una transacción; DELETE invalida el intento y retira fragmentos/vectores. No se mantienen transacciones durante inferencia. Una versión incompatible exige reconstrucción explícita; no se cambia el índice en silencio.

## Límites y fallos

Hasta 1000 fragmentos por documento, 2000 caracteres por fragmento y 512 tokens incluyendo prefijo/especiales. Un fragmento que excede tokens detiene la indexación completa con token_limit; no se pierde el final del texto. El administrador puede ajustar segmentación y volver a cargar; segmentación automática por tokenizer se evaluará si el corpus autorizado la necesita.

Un subproceso de inferencia por proceso API, CPU de un hilo, timeout de pared EMBEDDING_TIMEOUT_SECONDS (30..180, defecto 180). En Docker Linux se limita memoria virtual a 3 GiB y CPU a 180 segundos; en Windows nativo aplica timeout sin RLIMIT. Nginx permite 210 segundos en API general. Más réplicas o grandes corpus requieren cola y coordinación compartida, pendientes de producción.

model_unavailable devuelve 503; token_limit, embedding_timeout, embedding_failed o invalid_embedding devuelven 422 seguro; fallo de persistencia 500 seguro. Vectores deben ser completos, finitos, de 384 dimensiones y normalizados; cuenta de tokens 1..512. No se registran texto, vectores ni diagnósticos sensibles.

## Fuentes y límites de esta decisión

[Modelo y pooling E5](https://huggingface.co/intfloat/multilingual-e5-small), [ONNX Runtime](https://onnxruntime.ai/docs/api/python/api_summary.html), [pgvector/HNSW](https://github.com/pgvector/pgvector). Dependencias de ejecución y transitivas fijadas en requirements/base.txt; dev reutiliza esa base. Se eligió ONNX directo para fijar artefactos sin una descarga implícita desde las peticiones.

La presencia de HNSW no acredita recall o velocidad. El siguiente hito comparará recuperación exacta/aproximada con consultas de referencia y filtros de autorización. No hay LLM ni resultados experimentales de tesis en este bloque.
