# Modelo de datos y evolución

La migración 0001 habilita pgvector. La migración 0002 crea usuarios institucionales, sesiones y solicitudes de acceso. Las migraciones 0001, 0002 y 0003 están aplicadas en PostgreSQL local. La 0003 crea documentos.

`usuarios`: id, institutional_email único, institutional_id opcional único, nombre, apellido, rol (student/teacher/admin), activo, created_at y last_login. No existe password ni password_hash.

`sesiones_autenticacion`: hash del token como identificador, usuario con FK, modo y expiración. `intentos_sso`: hash del estado, modo, URL service y expiración. El estado de acceso se consume una sola vez; la sesión se revoca al cerrar sesión. Los hashes no permiten reconstruir el token del navegador.

La gestión administrativa de roles y las entidades posteriores todavía no están implementadas. El rol local actual está en usuarios; una entidad de roles independiente se evaluará al implementar la gestión de permisos.

Entidades exigidas por la sección 10: usuarios, roles, documentos, fragmentos_documento, perfiles_rendimiento, generaciones, fuentes_generacion, proveedores_llm, metricas_generacion y evaluaciones_contenido.

Relaciones conceptuales propuestas para validar: usuarios asociados a roles; documentos con fragmentos; perfiles asociados a generaciones; generaciones vinculadas a fragmentos mediante fuentes_generacion, a proveedor/modelo, a métricas y a evaluaciones. Cardinalidades, política de eliminación, propiedad de documentos y retención se decidirán al implementar sus casos de uso.

Antes de crear una tabla se documentarán los campos, restricciones, índices, permisos y pruebas. Las migraciones se guardan en `backend/alembic/versions` y se ejecutan con Alembic. No se permite crear tablas desde el arranque de FastAPI con `create_all`.

`documentos`: UUID, owner_id con FK a usuarios, filename, title, mime_type, size_bytes (1..10 MiB), sha256, status (uploaded/deleted), created_at y deleted_at. Índice por propietario; listas y detalles excluyen eliminados. Los bytes se guardan en almacenamiento privado identificado por el UUID, separado de PostgreSQL. La eliminación conserva metadatos mínimos y retira el archivo. Fragmentos y estados de ingesta se añadirán en migraciones futuras.
