# Modelo de datos y evolución

La migración 0001 habilita pgvector. La migración 0002 crea usuarios institucionales, sesiones y solicitudes de acceso. La 0003 crea documentos, la 0004 incorpora extracción trazable y fragmentos, la 0005 añade embeddings e índice HNSW, la 0006 prepara trazabilidad de contenidos, la 0007 reserva inicios de generación y la 0008 incorpora perfiles sintéticos. Las ocho están aplicadas en PostgreSQL local; se conservan inmutables las migraciones anteriores.

`usuarios`: id, institutional_email único, institutional_id opcional único, nombre, apellido, rol (student/teacher/admin), activo, created_at y last_login. No existe password ni password_hash.

`sesiones_autenticacion`: hash del token como identificador, usuario con FK, modo y expiración. `intentos_sso`: hash del estado, modo, URL service y expiración. El estado de acceso se consume una sola vez; la sesión se revoca al cerrar sesión. Los hashes no permiten reconstruir el token del navegador.

La gestión administrativa de roles y las entidades independientes de métricas/evaluación todavía no están implementadas. El rol local actual está en usuarios; una entidad de roles independiente se evaluará al implementar la gestión de permisos.

`perfiles_rendimiento` (0008): UUID, owner_id con FK a usuarios e índice, payload JSONB validado por ProfileRequest, schema_version restringida a performance-profile-v1 y created_at con zona horaria. SQL exige objeto JSON y versión; los rangos, tipos, texto y declaración synthetic se validan en aplicación. Instantáneas privadas inmutables por creador teacher/admin, sin FK a estudiante institucional ni vínculo con generaciones todavía. Observaciones sucesivas crean otro UUID; no hay deduplicación ni idempotencia. Campos y permisos en [api/perfiles.md](../api/perfiles.md), decisión 0009 y pruebas/hito_08_perfiles.md.

`generaciones_contenido` (0006, ampliada por 0007): UUID, propietario FK/índice, request_snapshot, sources_snapshot, retrieval_snapshot JSONB privados; instructions/prompt exactos, prompt_version/hash; status prepared/generating/succeeded/failed; generation_started_at; proveedor/modelo solicitado/versión/id de respuesta; usage/latencia/costo nullable; recurso validado o código de error; created_at/completed_at. Restricciones de coherencia terminal, costo/latencia no negativos. Reserva antes de red y cierre condicional por propietario/estado. Prepared no implica llamada LLM. Historial HTTP propio disponible; adaptación de perfiles, costo calculado y métricas académicas pendientes.

Las fuentes son snapshots, no FK con cascada que borre evidencia tras cambiar/eliminar documentos. La política de retención/purga debe concretarse antes de datos institucionales. La base mínima agrupa las entidades conceptuales generaciones/fuentes/métricas del plan; su normalización posterior dependerá del historial/benchmark, no se consideran tablas pendientes completadas por el JSONB. Ver decisión 0008 y api/contenidos.md. Los registros de suites se revierten; la demostración manual conserva generaciones Gemini sobre material sintético.

Cuatro recorridos mínimos Gemini con material sintético almacenados (pruebas/hito_07_cuatro_recursos.md). Reserva con cap global persistente; sin cálculo monetario, evaluación académica ni adaptación de perfiles.

Entidades exigidas por la sección 10: usuarios, roles, documentos, fragmentos_documento, perfiles_rendimiento, generaciones, fuentes_generacion, proveedores_llm, metricas_generacion y evaluaciones_contenido.

Relaciones conceptuales propuestas para validar: usuarios asociados a roles; documentos con fragmentos; perfiles asociados a generaciones; generaciones vinculadas a fragmentos mediante fuentes_generacion, a proveedor/modelo, a métricas y a evaluaciones. Cardinalidades, política de eliminación, propiedad de documentos y retención se decidirán al implementar sus casos de uso.

Antes de crear una tabla se documentarán los campos, restricciones, índices, permisos y pruebas. Las migraciones se guardan en `backend/alembic/versions` y se ejecutan con Alembic. No se permite crear tablas desde el arranque de FastAPI con `create_all`.

`documentos`: UUID, owner_id con FK a usuarios, filename, title, mime_type, size_bytes (1..10 MiB), sha256, status (uploaded/deleted), created_at y deleted_at. Índice por propietario; listas y detalles excluyen eliminados. Los bytes se guardan en almacenamiento privado identificado por el UUID, separado de PostgreSQL. La eliminación conserva metadatos mínimos y retira el archivo y los fragmentos.

Desde 0004: processing_status (pending/processing/processed/failed), processing_error (código seguro), processing_token (UUID interno de intento), processing_started_at, processed_at, processing_version, chunk_chars, chunk_overlap, chunk_count y text_chars. Restricciones de estados y contadores no negativos. No se guarda texto extraído completo adicional en documentos.

`fragmentos_documento`: UUID, document_id con FK y ON DELETE CASCADE, position, source_kind (page/paragraph), source_index, char_start, char_end, text y source_sha256. Único (document_id, position), índice por documento, fuentes/posiciones válidas y longitud igual a char_end-char_start. Los offsets se refieren a una unidad normalizada; su SHA-256 se calcula sobre UTF-8. La política de eliminación lógica retira explícitamente los fragmentos en la misma transacción.

Desde 0005: embedding nullable Vector(384), embedding_tokens nullable (1..512) e índice HNSW ix_fragmentos_embedding_cosine con vector_cosine_ops. Documentos conservan index_status (pending/indexing/indexed/failed), index_error, index_token interno, index_started_at, indexed_at, embedding_model, embedding_revision y embedding_version. La publicación de todos los vectores y metadatos es atómica y condicionada por intento/documento vigente. Reconstruir reemplaza vectores sin cambiar los fragmentos. Borrar invalida ambos intentos y elimina fragmentos/vectores. Una futura recuperación deberá filtrar propiedad, estado indexed y modelo/revisión/versiones compatibles.
