# Generación de contenidos educativos

 Generación, consulta y trazabilidad de recursos mediante IA y RAG.

## Componentes

| Área | Tecnología | Responsabilidad |
|---|---|---|
| Interfaz | Angular, TypeScript, SCSS y KaTeX | Materiales, solicitudes, resultados e historial. |
| API | FastAPI y Pydantic | Contratos, autorización y coordinación de servicios. |
| Persistencia | PostgreSQL, pgvector, SQLAlchemy y Alembic | Metadatos, vectores, trazas y migraciones. |
| Recuperación | E5 multilingüe y ONNX Runtime | Embeddings y búsqueda local. |
| Generación | Adaptadores HTTP de proveedores | Modelo seleccionado, límites y errores. |
| Operación | Docker Compose y nginx | Entorno reproducible y proxy. |

## Ejecución

```powershell
./infraestructura/scripts/initialize-local.ps1
docker compose --env-file licencias/secure_data.env build
docker compose --env-file licencias/secure_data.env --profile embeddings run --rm --no-deps prepare-embeddings
docker compose --env-file licencias/secure_data.env up -d --build --wait
```

Interfaz: http://localhost:4200. API: http://localhost:8000/api/v1/docs.
Configuración Docker y claves: `licencias/secure_data.env`. Ejecución directa del backend: `licencias/backend.env`. Ambos archivos son privados y están excluidos de Git y Docker. Las dos configuraciones se conservan para no sobrescribir ajustes locales distintos.

Docker Desktop debe estar iniciado y usar contenedores Linux. La preparación de embeddings
verifica los artefactos existentes y descarga únicamente los que falten o no sean válidos.
Los datos se conservan en los volúmenes de Compose; no uses `down -v` para actualizar.
Comprueba el arranque con `docker compose --env-file licencias/secure_data.env ps` y `./infraestructura/scripts/check-health.ps1`.

## Compatibilidad

Se conservan identificadores existentes de base de datos, proyecto Compose y respaldos para mantener acceso a los datos. No representan el nombre del producto. Las cookies y la cabecera del cliente usan el identificador neutro `prototipo`; las sesiones anteriores requieren iniciar sesión otra vez.

## Validación

Backend: pytest y Ruff. Frontend: `npm test -- --watch=false` y `npm run build`.
Sin commits automáticos. Las evidencias de pruebas anteriores se conservan como registros históricos.

## Respaldo y recuperación

Los volúmenes postgres_data, document_data y embedding_data conservan base de datos, documentos y modelo. No cambiar sus identificadores ni borrarlos para reparar el arranque.

Antes de respaldar, esperar que terminen las operaciones y detener frontend/backend. Con PostgreSQL activo, ejecutar `./infraestructura/scripts/backup-local.ps1`; después reiniciar backend/frontend con el comando Compose anterior. Los respaldos completos están en documentacion-local/respaldos y contienen dump, documentos y manifiesto. La configuración privada se conserva por separado.

Comprobar una copia con `./infraestructura/scripts/verify-local-backup.ps1 -BackupDirectory <ruta>`: usa un contenedor temporal y no sustituye la base activa. Conservar el informe de verificación junto a la copia. Una copia en el mismo disco no cubre su pérdida.

## Desarrollo

Frontend: [instrucciones](frontend/README.md). Para backend directo, ejecutar desde backend con sus dependencias instaladas; carga licencias/backend.env mediante una ruta independiente del directorio actual. Docker recibe la configuración de licencias/secure_data.env. La única plantilla es `.env.example`, sin claves reales. Para backend directo, copiarla a `licencias/backend.env`, cambiar `DB_HOST=localhost` y configurar una base accesible desde el equipo: PostgreSQL de Compose está disponible en `127.0.0.1:5433` (`DB_PORT=5433` para el backend directo). No sobrescribir archivos privados existentes.


## Versión 0.2

La búsqueda y preparación de recursos requieren asignatura y materiales habilitados. Después de procesar, indexar y revisar una versión, usar **Habilitar como fuente** en sus detalles. **Retirar de recursos** conserva el original y evita nuevas recuperaciones; las preparaciones pendientes con esa fuente deben rehacerse. Los materiales anteriores a esta actualización necesitan habilitación explícita.

Claude utiliza el adaptador existente y requiere modelo, clave y confirmación de presupuesto mediante `LLM_PAID_USAGE_CONFIRMED=true`, además de `LLM_ENABLED=true` y `LLM_DEFAULT_PROVIDER=claude`. La plantilla mantiene los envíos deshabilitados. No se asigna un costo cero a Claude.

Alcance, API, pruebas, archivos nuevos y pendientes de aceptación: [versión 0.2](versionesDM/Version-0.2.md).
