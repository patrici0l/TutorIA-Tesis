# Arquitectura de TutorIA-Lucero

Estado consolidado: 25 de octubre de 2026. El [plan actual](../PLAN_ACTUAL.md)
separa implementación técnica, evidencia histórica y validación pendiente.

El navegador carga Angular desde nginx y consulta `/api/v1/health` en el mismo origen. Nginx reenvía `/api/` a FastAPI. El router delega en HealthService, que usa HealthRepository para consultar PostgreSQL y comprobar la extensión `vector`. No se requieren claves LLM.

Docker Compose espera a PostgreSQL, ejecuta Alembic en un servicio de migración de una sola ejecución, espera su resultado y arranca FastAPI. La interfaz espera a que la API pase su healthcheck. PostgreSQL persiste en un volumen nombrado. El reinicio normal no destruye datos.

La API devuelve 503 si la BD o pgvector fallan. Angular diferencia este caso de una API inaccesible. El healthcheck comprueba infraestructura, no afirma que existan documentos, embeddings o generación.

Las capas siguen router → servicio → repositorio. RAG separa extracción, embeddings,
recuperación y prompts. Los servicios educativos dependen de una interfaz común de
proveedor. Autenticación, documentos, contenidos, perfiles, métricas y estudiantes
cuentan con implementación; evaluación dispone de herramientas offline.

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

La inferencia termina antes de abrir la transacción de publicación. La reclamación condicional, token de intento y timeout permiten recuperar indexaciones interrumpidas y rechazar publicaciones tardías. Texto/referencias permanecen intactos. Angular muestra progreso, errores persistidos, reintento y reconstrucción explícita. La decisión 0005 documenta recursos y reproducibilidad. Buscar fuentes no llama al LLM; la generación real se solicita expresamente desde Recursos.

## Recuperación de fuentes

Angular /busqueda → POST /api/v1/rag/search → SearchService → EmbeddingWorkerClient y SearchRepository. El modelo genera un vector query local sin transacción de lectura abierta durante inferencia; el cupo es compartido con indexación. El vocabulario de consulta explícito y versionado normaliza equivalencias matemáticas y conserva la consulta original. SQL materializa corpus propio/elegible/compatible, ordena por distancia coseno exacta y devuelve texto y referencias sin vectores. La API exige teacher/admin y protección CSRF; no admite owner_id del cliente. Estudiantes pendientes de asignación de curso/corpus.

HNSW se compara en pruebas con plan confirmado, nunca se activa por una opción del cliente. La muestra técnica es pequeña y el ajuste de vocabulario se hizo sobre ella; validación independiente y rendimiento a escala siguen pendientes. Contrato api/rag.md, decisión 0006 y evidencia pruebas/hito_05.md. No se genera una respuesta ni se ofrece similitud como certeza.

## Capa de proveedores IA y generación

`modulos/proveedores_ia` ofrece `LLMProvider`, fábrica y adaptadores Gemini,
OpenAI y Claude. Gemini tiene evidencia de uso real; los otros adaptadores se han
probado con transporte simulado. El envío API/UI solo habilita Gemini bajo la
configuración gratuita autorizada. No hay reintentos automáticos ni fallback.
Los adaptadores conocen HTTP; los secretos permanecen en backend.

`PreparationService → PrepareContentService → SearchService` prepara fuentes,
solicitud y prompt versionado; un perfil sintético propio puede adaptar el apoyo.
El docente revisa las fuentes antes de enviar el identificador a generación.
`GenerationClaimRepository` reserva en PostgreSQL antes de salir a red y confirma
límites globales compartidos. `GeneratePreparationService` llama al proveedor una
vez; `GenerationTraceService` valida y persiste resultado o fallo seguro.
Validar formato/citas no certifica exactitud matemática ni calidad pedagógica.

El historial conserva snapshots de fuentes, perfil, prompt, modelo, límites y
consumo reportado. La consulta privada y exportación local no regeneran recursos.
Métricas y cuota distinguen datos conocidos de valores no registrados; el costo
es una estimación condicionada, no una consulta de facturación. Contratos vigentes:
[contenidos](../api/contenidos.md), [personalización](../api/personalizacion.md) y
[auditoría](../api/auditoria_recursos.md).

## Estudiantes y actividades

`AssignmentService` valida docente, destinatario y recurso propio. La actividad
comparte un banco fijo corregible o un recurso generado como material con soluciones.
El destinatario accede mediante la asignación, sin recibir prompts ni perfiles privados.
`PracticeService` corrige los bancos fijos en servidor y conserva intentos idempotentes.
Cerrar/cancelar bloquea nuevas entregas y mantiene las anteriores. Los materiales
generados todavía no registran lectura ni respuestas de quizzes dinámicos.

## Interfaz y lectura del código

Angular mantiene el recorrido Documentos → Recursos → Actividades y el acceso opcional
a perfiles. El menú modal restaura el foco; KaTeX está empaquetado y procesa texto
sin interpretar HTML externo. TS, HTML, SCSS y pruebas permanecen separados.

Los comentarios directos describen responsabilidades y decisiones no evidentes:
propiedad, transacciones, estados, límites, reenvíos y datos desconocidos. Deben ser
breves, próximos a la regla y explicar su motivo; nombres y tipos expresivos no
necesitan repetir cada instrucción. Las pruebas documentan los casos de comportamiento.

## Evaluación y entrega

Las herramientas de `modulos/evaluacion` preparan manifiestos, registros y revisión
humana offline; la simulación no ejecuta un benchmark real. El protocolo, la revisión
pedagógica y los experimentos completos siguen pendientes. La demo remota es una
operación optativa con identidades ficticias compartidas, no un despliegue institucional.
