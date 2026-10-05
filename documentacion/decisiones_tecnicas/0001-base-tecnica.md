# Base técnica del primer hito

Fecha: 4 de octubre de 2026. Estado: implementada, validación registrada en pruebas/hito_01.md.

Se conserva el stack obligatorio. Angular se crea con CLI 22.2.1, Node local 24.15.0 y TypeScript 6, según los rangos publicados por Angular y los metadatos del registro npm. `package-lock.json` fija el árbol instalado. [Compatibilidad oficial](https://angular.dev/reference/versions).

FastAPI usa SQLAlchemy con psycopg síncrono para el primer chequeo; el endpoint síncrono evita bloquear el event loop. Las dependencias Python se fijan en requirements. El contenedor utiliza Python 3.12; la ejecución local puede usar una versión posterior compatible. Cada entorno se prueba por separado. [Contenedores FastAPI](https://fastapi.tiangolo.com/deployment/docker/).

PostgreSQL 17 con imagen pgvector 0.8.2 versionada ofrece la extensión vector. Alembic gestiona su activación; no se usan cambios manuales del esquema. [Repositorio oficial pgvector](https://github.com/pgvector/pgvector).

Una sola ubicación ejecuta migraciones: `backend/alembic/versions`. `app/base_datos/migrations` queda como reserva exigida por el árbol del plan y no duplica migraciones. No se diseñan tablas definitivas antes de validar los casos de uso, siguiendo la sección 10.

Las animaciones actuales se centralizan en SCSS con soporte nativo de movimiento reducido. Los archivos fade/slide/scale/route del documento son ejemplos de organización: solo se implementa fade en este bloque, sin introducir código de animaciones sin uso.

Nginx sirve Angular compilado y actúa como proxy del mismo origen. Esto evita una política CORS permisiva y conserva el contrato relativo `/api/v1`. Ningún secreto se inyecta en el build de Angular. Solo la contraseña de BD se entrega a los contenedores que la necesitan; las claves LLM no se conectan todavía.

LICENSE deja explícita la ausencia de concesión de licencia abierta hasta que el autor decida las condiciones. GitHub no se configura sin identificar cuenta y visibilidad. Ninguna de estas decisiones altera el criterio técnico del hito 1.
