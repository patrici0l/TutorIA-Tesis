# Arquitectura inicial

El navegador carga Angular desde nginx y consulta `/api/v1/health` en el mismo origen. Nginx reenvía `/api/` a FastAPI. El router delega en HealthService, que usa HealthRepository para consultar PostgreSQL y comprobar la extensión `vector`. No se requieren claves LLM.

Docker Compose espera a PostgreSQL, ejecuta Alembic en un servicio de migración de una sola ejecución, espera su resultado y arranca FastAPI. La interfaz espera a que la API pase su healthcheck. PostgreSQL persiste en un volumen nombrado. El reinicio normal no destruye datos.

La API devuelve 503 si la BD o pgvector fallan. Angular diferencia este caso de una API inaccesible. El healthcheck comprueba infraestructura, no afirma que existan documentos, embeddings o generación.

Las futuras capas seguirán router → servicio → repositorio. RAG tendrá loaders, retrievers, prompts y servicios separados. Los servicios educativos dependerán de una interfaz de proveedor común. La evolución prevista está detallada en el plan, aún sin implementación de esos módulos.

El entorno actual es de desarrollo local, con autenticación mock y adaptador CAS preparado y con puertos publicados exclusivamente en loopback. No es un despliegue institucional de producción.

## Acceso institucional

Angular inicia GET /api/v1/auth/login. FastAPI crea un intento de acceso de cinco minutos ligado al navegador; CAS devuelve el ticket al callback y FastAPI lo valida con el servicio configurado usando el mismo service. Se crea o actualiza el usuario local y se emite una cookie opaca HttpOnly. Angular consulta /auth/me antes de acceder a /inicio. En desarrollo mock sustituye únicamente la identidad institucional por una ficticia del servidor. La sesión y el intento están ligados al modo de autenticación.

Los registros de acceso de autenticación se desactivan para evitar capturar tickets o cookies. PostgreSQL conserva hashes de tokens y caducidad; el usuario no tiene contraseña. Logout revoca la sesión de TutorIA, sin cerrar globalmente CAS. La decisión 0002 documenta HTTPS, dominios, atributos y requisitos pendientes de TI.

## Corpus docente privado

El módulo documentos sigue router → DocumentService → DocumentRepository. FastAPI valida permisos por sesión y propietario, MIME, extensión, tamaño y estructura antes de guardar. PostgreSQL almacena metadatos y SHA-256; el volumen document_data conserva bytes identificados por UUID fuera del directorio de nginx. El frontend usa la misma cookie y cabecera de protección que autenticación. Las listas son paginadas y los registros eliminados quedan excluidos. El estado uploaded corresponde a almacenamiento; processing_status describe la extracción. No se invoca un proveedor IA. La política detallada está en decisión 0003.

## Extracción y segmentación

El router de documentos delega el procesamiento en IngestDocumentService → ChunkRepository, bajo el módulo rag. La lectura/parsing/normalización/segmentación ocurre en un proceso Python separado con timeout y límites de memoria/CPU en Docker. DocumentTextService extrae páginas PDF o párrafos DOCX/TXT y genera fragmentos con offsets exactos en texto normalizado. La publicación SQL condicional impide que un intento tardío sobreescriba un reintento o restaure un documento eliminado.

Angular incorpora DocumentChunksComponent para revisar texto paginado y fuentes; usa interpolación segura. Los fallos se conservan por documento y admiten reintento; procesos interrumpidos pueden recuperarse tras dos minutos. La decisión 0004 documenta límites y reproducción.

## Embeddings e indexación local

POST /documents/{id}/index delega en IndexDocumentService → IndexRepository. Un worker separado verifica pesos/tokenizer locales fijados por SHA-256, genera embeddings E5 de 384 dimensiones en CPU y valida longitud de tokens sin truncamiento. La descarga de pesos públicos es una operación explícita del perfil Docker embeddings; ninguna petición API descarga modelos ni transmite corpus fuera del entorno. El volumen embedding_data se monta solo para lectura en backend.

La inferencia termina antes de abrir la transacción de publicación. La reclamación condicional, token de intento y timeout permiten recuperar indexaciones interrumpidas y rechazar publicaciones tardías. Texto/referencias permanecen intactos. Angular muestra progreso, errores persistidos, reintento y reconstrucción explícita. La decisión 0005 documenta recursos y reproducibilidad. La búsqueda top-k ya se implementó; la conexión LLM real permanece desactivada.

## Recuperación de fuentes

Angular /busqueda → POST /api/v1/rag/search → SearchService → EmbeddingWorkerClient y SearchRepository. El modelo genera un vector query local sin transacción de lectura abierta durante inferencia; el cupo es compartido con indexación. El vocabulario de consulta explícito y versionado normaliza equivalencias matemáticas y conserva la consulta original. SQL materializa corpus propio/elegible/compatible, ordena por distancia coseno exacta y devuelve texto y referencias sin vectores. La API exige teacher/admin y protección CSRF; no admite owner_id del cliente. Estudiantes pendientes de asignación de curso/corpus.

HNSW se compara en pruebas con plan confirmado, nunca se activa por una opción del cliente. La muestra técnica es pequeña y el ajuste de vocabulario se hizo sobre ella; validación independiente y rendimiento a escala siguen pendientes. Contrato api/rag.md, decisión 0006 y evidencia pruebas/hito_05.md. No se genera una respuesta ni se ofrece similitud como certeza.

## Capa de proveedores IA

`modulos/proveedores_ia` expone interfaz `generate`, esquemas internos, fábrica, limitador compartido por proceso y adaptador Gemini. La capa educativa futura dependerá de la interfaz; solamente el adaptador conoce REST y headers del proveedor. Devuelve texto completo y metadata normalizada para trazabilidad, sin realizar SQL ni consultar perfiles/documentos. Configuración y secretos viven en backend; Docker los suministra desde el entorno privado, nunca desde Angular.

Activación inicial deshabilitada por el autor. Pruebas con HTTPX MockTransport sin red; aún no hay rutas content ni coordinador de llamada IA. No se envía corpus ni se presenta una respuesta simulada en el producto. La decisión 0007 y api/proveedores_ia.md detallan límites, errores, ausencias de metadata y requisitos antes de conectar Gemini real. OpenAI/Claude siguen previstos por la misma interfaz; no están implementados ni se usan como fallback.

`PrepareContentService → SearchService → EducationalPromptBuilder` prepara fuente/solicitud/esquema de recurso y hash canónico; `GenerationRepository` guarda evidencia antes de una eventual llamada. `GenerationTraceService → ResourceValidationService` valida estructura y pertenencia de citas antes de finalizar como succeeded; fallos quedan con código seguro y consumo conocido. Estado terminal no se sobreescribe. Contratos separados de explicación/ejercicio/quiz/feedback, dificultad manual, sin perfiles ni exactitud matemática certificada. No habilita llamadas IA ni rutas públicas de contenido. Decisión 0008 y api/contenidos.md.
