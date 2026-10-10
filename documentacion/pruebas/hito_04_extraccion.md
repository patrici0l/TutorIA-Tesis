# Hito 4 — Extracción y segmentación (primera parte)

Verificado el 6 de octubre de 2026. El hito 4 completo continúa abierto: embeddings e índices vectoriales del corpus todavía no están implementados. No se probaron CAS institucional ni LLM.

## Resultado verificable

PDF con texto, DOCX y TXT se extraen y normalizan en un proceso separado. La segmentación guarda fragmentos reales en PostgreSQL con página/párrafo, offsets y SHA-256 de unidad, junto a versión y configuración en el documento. Angular permite procesar, revisar fragmentos paginados, ver errores persistentes y reintentar procesos fallidos/interrumpidos. El estilo y navegación UPS se conservan.

## Entorno y comandos

Docker Linux, Python 3.12, PostgreSQL 17 con pgvector 0.8.2, Node 24.15 y Angular 22. La migración 0004_document_chunks se aplicó sobre 0003 sin modificar las anteriores. Los servicios backend, frontend y postgres quedaron healthy después de recrear el entorno conservando volúmenes.

Desde la raíz del repositorio:

```powershell
docker compose up -d --build --wait
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --build --no-deps --rm test-backend
docker build --target build -t tutoria-frontend-validation:local -f frontend/Dockerfile .
docker run --rm tutoria-frontend-validation:local npm test -- --watch=false
```

Resultados finales: backend 105 aprobadas, sin omisiones; Angular 32 aprobadas en 9 archivos. Build de producción: 299,59 kB iniciales, sin advertencias de presupuesto. Ruff check y format check sin errores al cierre. Las dos advertencias conocidas permanecen: TestClient de Starlette/HTTPX y add_js de pypdf usado exclusivamente para comprobar rechazo de un PDF activo.

Prueba local anterior al último caso concurrente: Python 3.14, 98 aprobadas y 6 integraciones omitidas; la evidencia final de los 105 casos corresponde a Docker/PostgreSQL, no a una base simulada.

## Cobertura relevante

- NFC, superíndices Unicode y formato vertical directo DOCX conservados; OfficeMath y estilos verticales heredados detectados rechazados.
- PDF con páginas vacías conserva numeración original; sin texto informa empty_text/OCR pendiente. DOCX incluye párrafos de tablas; TXT UTF-8/BOM y separación de párrafos.
- Límites de archivo, ZIP/XML, páginas, caracteres, unidades y fragmentos; offsets exactos, solapamiento, cobertura y progreso sin cruzar fuentes.
- Permisos por sesión/rol/propietario, CSRF, paginación, no-store y ausencia de rutas/tokens privados en respuestas.
- Worker real para TXT; SHA distinto/archivo ausente, timeout y salida de proceso fallida; errores seguros y ausencia de fragmentos parciales.
- Idempotencia: POST repetido conserva IDs, fecha y configuración. Reintento tras fallo y recuperación de intento vencido.
- PostgreSQL: publicación tardía no pisa un intento posterior; eliminación invalida publicaciones. Dos sesiones y transacciones independientes compiten por la misma reclamación: exactamente una gana. Publicación y eliminación simultáneas dejan el documento eliminado y sin fragmentos. Los registros sintéticos del caso concurrente se limpian por UUID en finally; el resto de integraciones usa transacción exterior con rollback.
- Angular: éxito/error, cambio de selección durante procesamiento, cancelación de detalle, recuperación de intento interrumpido, fragmentos paginados y contenido interpolado sin ejecutar HTML.

## Navegador

Se inició sesión con docente.demo@example.org ficticio y se procesó la muestra sintética ya cargada. Resultado: un fragmento, Párrafo 1, texto con ejemplo y ejercicio de derivadas. Después de recrear backend/frontend y recargar, estado y texto permanecieron. Capturas: hito_04_fragmentos_desktop.png y hito_04_fragmentos_mobile.png. Se verificó tamaño móvil 390×844; texto y paginación visibles, y se restauró tamaño normal. No se borraron materiales desde la interfaz ni se utilizaron credenciales UPS.

Para la demostración se seleccionó teacher mediante variable temporal de proceso y después se recreó backend con la configuración original. La sesión docente iniciada sigue válida; un acceso nuevo emplea AUTH_MOCK_USER configurado en .env.

## Próximo criterio de cierre

Elegir/configurar modelo de embeddings, controlar su tokenizer, persistir versión/dimensión y vectores, crear índices y probar reproducción del corpus. Después validar recuperación top-k con consultas de referencia sin LLM. Cotejo docente y corpus real autorizado siguen pendientes; estos tests no acreditan calidad académica de fórmulas extraídas.
