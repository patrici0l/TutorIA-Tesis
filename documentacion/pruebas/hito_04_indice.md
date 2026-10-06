# Hito 4 — Embeddings e índice vectorial

Fecha: 6 de octubre de 2026. Complementa hito_04_extraccion.md. Entorno Docker local, usuarios y material sintéticos, sin CAS real ni proveedor LLM.

## Implementación y reproducción

E5 multilingüe local ONNX CPU: intfloat/multilingual-e5-small, revisión 614241f622f53c4eeff9890bdc4f31cfecc418b3. Artefactos fijados por tamaño y SHA-256 en model_spec.py, 384 dimensiones, prefijos passage:/query:, mean pooling con attention_mask y normalización L2. Máximo 512 tokens incluyendo prefijo y tokens especiales; no se trunca texto. Modelo/tokenizer permanecen en embedding_data, fuera de Git.

```powershell
docker compose up -d --build --wait
docker compose --profile embeddings run --no-deps --rm prepare-embeddings
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml build test-backend
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --no-deps --rm test-backend
docker build --target build -t tutoria-frontend-validation:local -f frontend/Dockerfile .
docker run --rm tutoria-frontend-validation:local npm test -- --watch=false
.venv/Scripts/ruff.exe check backend
.venv/Scripts/ruff.exe format --check backend
```

Preparar requiere internet para pesos públicos; la inferencia no realiza conexiones. No imprimir .env ni eliminar volúmenes. POST /api/v1/documents/{id}/index exige propietario teacher/admin, sesión y protección CSRF; rebuild=true reconstruye explícitamente conservando fragmentos. La migración 0005 añade Vector(384), contador de tokens e índice HNSW coseno. Metadatos del documento conservan estado, modelo, revisión, versión e instante de indexación.

## Cobertura

Pruebas unitarias/API: pooling enmascarado, norma L2, checksum, prefijos y exceso de tokens antes de inferencia; rechazo de vectores incompletos/no finitos/no normalizados; propiedad/CSRF y documento sin procesar; idempotencia, reconstrucción sin alterar IDs/texto y eliminación de vectores; persistencia de errores seguros sin publicación parcial.

PostgreSQL: reclamación exclusiva, expiración/recuperación y token que bloquea publicación/fallo tardíos; eliminación invalida publicación. Con el modelo real: worker separado sin transacción de sesión activa durante inferencia, vector/tokens persistidos, reproducción con tolerancia absoluta 1e-6, tres pasajes sintéticos con consulta de referencia en español, distancia coseno en pgvector e índice HNSW existente. Exceso de tokens se rechaza explícitamente. Las filas de integración se revierten al finalizar.

Angular: indexación/progreso/éxito/error, conservación de detalle actual ante respuestas tardías y reconstrucción explícita. Compilación de producción: 299,59 kB iniciales, sin advertencias de presupuesto. 35 pruebas aprobadas en 9 archivos. Ruff check/format limpios (85 archivos).

## Resultados y navegador

Ejecución final completa: 119 backend/PostgreSQL aprobadas, ninguna omitida, con modelo real; 35 Angular aprobadas. Se mantienen dos advertencias conocidas: Starlette TestClient/HTTPX y pypdf add_js en una prueba de rechazo de PDF activo. La primera muestra de exceso de tokens (caracteres CJK consecutivos) no excedía realmente 512 tokens; se corrigió por 600 palabras «x» y se verifica el conteo del tokenizer antes de comprobar el rechazo. La suite completa pasó después de esa corrección.

Descarga y verificación SHA-256 de ambos artefactos completadas. Segunda preparación reutilizó ambos archivos y terminó con Verified, sin descarga. Antes de prepararlos, la interfaz devolvió model_unavailable de forma segura y habilitó Reintentar indexación, conservando fragmentos. Después, el docente ficticio indexó derivadas_sinteticas.txt y reconstruyó explícitamente desde el navegador: estado Índice vectorial listo, modelo y fecha visibles, un fragmento con la misma referencia/texto. Backend reiniciado y detalle recargado para comprobar persistencia. Docker deja backend/frontend/postgres saludables. Ninguna credencial UPS o clave LLM utilizada; .env no se modificó.

Capturas: hito_04_indice_desktop.png y hito_04_indice_mobile.png (390×844). El tamaño normal se restaura al terminar. La paleta UPS y navegación superior se conservan. Hito 4 cerrado técnicamente con material sintético; pendiente validación académica con corpus autorizado y recuperación del siguiente hito.

## Alcance

Esta evidencia comprueba ingesta e infraestructura vectorial. Los tres pasajes sintéticos son una comprobación mínima del modelo, no un benchmark académico ni validación completa de RAG. Hito 5 requiere endpoint top-k, filtros compatibles de estado/modelo/propiedad y evaluación de recuperación exacta/aproximada con corpus/consultas de referencia. No hay LLM ni generación en este bloque. Decisión técnica: 0005-embeddings-locales.md.
