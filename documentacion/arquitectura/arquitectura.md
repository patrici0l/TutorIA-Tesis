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

El módulo documentos sigue router → DocumentService → DocumentRepository. FastAPI valida permisos por sesión y propietario, MIME, extensión, tamaño y estructura antes de guardar. PostgreSQL almacena metadatos y SHA-256; el volumen document_data conserva bytes identificados por UUID fuera del directorio de nginx. El frontend usa la misma cookie y cabecera de protección que autenticación. Las listas son paginadas y los registros eliminados quedan excluidos. Los documentos se mantienen uploaded hasta implementar la ingesta; no se invoca un proveedor IA. La política detallada está en decisión 0003.
