# Hito 6 — Preparación de proveedores IA

Fecha: 6 de octubre de 2026. Rama: feature/llm-provider, base 88ae1fb.

El autor seleccionó Gemini y pidió dejar la conexión real para después. Se implementó la interfaz/fábrica y el primer adaptador; no se cierra todavía el criterio de integración real del hito 6. No hubo llamadas LLM, gasto, claves reales ni contenido generado presentado en la interfaz.

## Verificación reproducible

Desde la raíz:

```powershell
.venv/Scripts/ruff.exe check backend
.venv/Scripts/ruff.exe format --check backend
docker compose up -d --build --wait
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml build test-backend
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --rm --no-deps test-backend
git diff --check
```

Resultado final: **180 pruebas backend aprobadas, sin skips**, 17,73 segundos en el entorno Docker de esta ejecución. Incluyen PostgreSQL/pgvector, embeddings locales reales y recuperación. De ellas, 42 pruebas nuevas del proveedor usan HTTPX MockTransport, modelo `model-test-v1`, clave inequívocamente ficticia y texto sintético; no necesitan internet. Esta duración corresponde a la suite, no a latencia del proveedor.

Ruff check limpio; 102 archivos con formato correcto; diff sin errores de whitespace. `docker compose up -d --build --wait` terminó con código 0 y backend/frontend/postgres saludables. `LLM_ENABLED=false` comprobado desde la configuración del backend, imprimiendo solo ese booleano; nunca claves o `.env`. Sin nuevas dependencias ni migraciones, volúmenes conservados. Frontend sin cambios: compilación previa reutilizada por caché Docker; las 38 pruebas Angular corresponden al cierre anterior y no se repitieron en este bloque.

Advertencias conocidas: deprecación Starlette TestClient/HTTPX y `pypdf.add_js` usado para comprobar rechazo de PDF activo. No son fallos nuevos del proveedor.

## Cobertura del adaptador

- Fábrica desactivada/incompleta/proveedor sin adaptar rechaza antes de cualquier envío.
- Headers y JSON REST verificados: clave en header, sin query, instrucciones separadas, una candidata, store=false y límite de salida.
- Modelo solicitado/versión/id y tokens conservados; ausencias siguen desconocidas. Texto de pensamiento no expuesto ni prompts/texto/claves en repr.
- Entrada vacía, NUL/surrogates, caracteres sumados y bytes UTF-8 excesivos rechazados antes de red/cuota.
- HTTP 401/403/429/5xx/400/302 convertidos a códigos seguros; una única solicitud, sin reintento/redirección.
- Timeout y fallo de conexión liberan cupo. Cupo ocupado y ventana compartida rechazan sin envío; la ventana expira a los 60 segundos.
- Bloqueo, salida cortada, vacía, herramientas, tokens negativos/bool, JSON inválido, UTF-8 inválido, cuerpo excesivo y JSON demasiado profundo rechazados.

Durante la primera ejecución Windows, los identificadores automáticos de una parametrización con 1 MiB de bytes generaron problemas de preparación y salida enorme; se corrigieron con IDs cortos explícitos. La versión final cubre esos casos y pasa en Windows (42 pruebas aisladas) y Docker (suite completa). No se omiten los casos.

## Pendientes para la prueba real

Modelo/acceso del proyecto, presupuesto/cupo, credencial privada en backend, corpus autorizado y trazabilidad persistida antes de activar generación. Preparar contratos/prompts de recursos sin habilitar respuestas ficticias en el producto. Las pruebas de transporte no acreditan disponibilidad de Gemini, costo, calidad matemática ni evaluación académica. Consultar decisión 0007 y api/proveedores_ia.md.
