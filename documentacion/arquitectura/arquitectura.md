# Arquitectura inicial

El navegador carga Angular desde nginx y consulta `/api/v1/health` en el mismo origen. Nginx reenvía `/api/` a FastAPI. El router delega en HealthService, que usa HealthRepository para consultar PostgreSQL y comprobar la extensión `vector`. No se requieren claves LLM.

Docker Compose espera a PostgreSQL, ejecuta Alembic en un servicio de migración de una sola ejecución, espera su resultado y arranca FastAPI. La interfaz espera a que la API pase su healthcheck. PostgreSQL persiste en un volumen nombrado. El reinicio normal no destruye datos.

La API devuelve 503 si la BD o pgvector fallan. Angular diferencia este caso de una API inaccesible. El healthcheck comprueba infraestructura, no afirma que existan documentos, embeddings o generación.

Las futuras capas seguirán router → servicio → repositorio. RAG tendrá loaders, retrievers, prompts y servicios separados. Los servicios educativos dependerán de una interfaz de proveedor común. La evolución prevista está detallada en el plan, aún sin implementación de esos módulos.

El entorno actual es de desarrollo local, sin autenticación todavía y con puertos publicados exclusivamente en loopback. No es un despliegue institucional de producción.
