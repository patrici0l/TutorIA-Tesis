# Hito 5 — Recuperación de fuentes sin LLM

Fecha: 6 de octubre de 2026. Entorno Docker local, modelo ONNX real fijado por revisión/SHA-256, PostgreSQL/pgvector y datos sintéticos. Hito cerrado técnicamente; validación académica pendiente con corpus autorizado y consultas independientes.

## Evidencia reproducible

```powershell
docker compose up -d --build --wait
docker compose --profile embeddings run --no-deps --rm prepare-embeddings
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml build test-backend
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --no-deps --rm -e RAG_REPORT_PATH=/reports/hito_05_recuperacion.json --volume "${PWD}/documentacion/pruebas:/reports" test-backend
docker build --target build -t tutoria-frontend-validation:local -f frontend/Dockerfile .
docker run --rm tutoria-frontend-validation:local npm test -- --watch=false
.venv/Scripts/ruff.exe check backend
.venv/Scripts/ruff.exe format --check backend
```

Resultado final: 138 backend/PostgreSQL aprobadas, ninguna omitida; 38 Angular aprobadas en 10 archivos. Advertencias conocidas de Starlette TestClient/HTTPX y pypdf add_js en prueba de PDF activo. El corpus de integración se revierte al terminar; los registros de usuario no se modifican permanentemente. No hay secretos en el reporte.

Corpus/consultas: backend/tests/fixtures/rag_reference.json (calculo-sintetico-v1). Resultado generado: hito_05_recuperacion.json. Ocho documentos y ocho consultas. Base pura: top-1 y recall@3=0,875. Con normalización de términos matemáticos: top-1=0,875, recall@3=1, MRR@3=0,9375. Cociente ocupa segundo lugar, no primero. HNSW coincide con los tres resultados exactos en todas las consultas; EXPLAIN comprueba ix_fragmentos_embedding_cosine. ef_search=80 e iterative_scan=strict_order. No se hizo prueba de rendimiento a escala.

La consulta de división detectó la limitación antes de añadir el vocabulario. Se conservaron consulta, etiqueta y corpus; el reporte permite comparar ambos flujos. Esta misma muestra motivó el ajuste y por tanto NO sirve como conjunto independiente de validación. No se atribuye aprobación académica, resultados finales de tesis ni precisión general del modelo.

## Seguridad y comportamiento

Pruebas comprueban sesiones/roles/CSRF, límites de cuerpo/consulta/top-k, normalización NFC, rechazo de campos de propietario y parámetros desconocidos; errores del modelo seguros y cupo compartido liberado ante fallo. Vectores ideales en documentos ajenos, eliminados, en indexación/fallo o de modelo/revisión/versión incompatible no aparecen. Fuentes conservan texto, offsets y SHA-256; tras eliminar una fuente deja de recuperarse. API real usa worker query y respuesta sin vectores/no-store. Sin corpus no invoca el modelo; consulta ajena con filtro alto no produce coincidencias ni respuesta inventada.

Angular verifica carga/éxito/error/reintento, resultados anteriores retirados al consultar, doble envío bloqueado, entradas inválidas, estudiante sin petición y texto fuente interpolado sin ejecutar HTML. Navegación mantiene roles, activo, desplegable y slider. Navegador comprobado: consulta de tasa de cambio recupera el material de derivadas (similitud 0,851), párrafo 1 y referencia expandible; filtro de similitud 1 devuelve cero coincidencias sin generar contenido. Capturas hito_05_busqueda_desktop.png y hito_05_busqueda_mobile.png; 390×844 y tamaño normal restaurado. Pestaña activa visible tras transición y lectura móvil sin desbordamiento horizontal. Se reanudaron contenedores detenidos conservando volúmenes y se volvió a recuperar el mismo material; backend/frontend/postgres saludables. .env intacto.

Contrato: api/rag.md. Arquitectura/limitaciones: decisión 0006. El siguiente hito prepara interfaz/fábrica de proveedores; CAS real, autorización de corpus y claves/modelos/presupuesto todavía requieren definición.
