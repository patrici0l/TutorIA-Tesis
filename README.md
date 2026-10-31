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
docker compose up -d --build --wait
```

Interfaz: http://localhost:4200. API: http://localhost:8000/api/v1/docs.
Configuración y claves exclusivamente en archivos de entorno privados.

## Compatibilidad

Se conservan identificadores existentes de base de datos, proyecto Compose y respaldos para mantener acceso a los datos. No representan el nombre del producto. Las cookies y la cabecera del cliente usan el identificador neutro `prototipo`; las sesiones anteriores requieren iniciar sesión otra vez.

## Validación

Backend: pytest y Ruff. Frontend: `npm test -- --watch=false` y `npm run build`.
Sin commits automáticos. Las evidencias de pruebas anteriores se conservan como registros históricos.
