# Modelo de datos por desarrollar

La migración actual habilita únicamente pgvector y la tabla de versión de Alembic. No existen todavía tablas funcionales ni se presume validado su diseño.

Entidades exigidas por la sección 10: usuarios, roles, documentos, fragmentos_documento, perfiles_rendimiento, generaciones, fuentes_generacion, proveedores_llm, metricas_generacion y evaluaciones_contenido.

Relaciones conceptuales propuestas para validar: usuarios asociados a roles; documentos con fragmentos; perfiles asociados a generaciones; generaciones vinculadas a fragmentos mediante fuentes_generacion, a proveedor/modelo, a métricas y a evaluaciones. Cardinalidades, política de eliminación, propiedad de documentos y retención se decidirán al implementar sus casos de uso.

Antes de crear una tabla se documentarán los campos, restricciones, índices, permisos y pruebas. Las migraciones se guardan en `backend/alembic/versions` y se ejecutan con Alembic. No se permite crear tablas desde el arranque de FastAPI con `create_all`.
