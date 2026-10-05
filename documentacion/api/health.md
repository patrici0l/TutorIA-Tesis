# Contrato de disponibilidad

GET `/api/v1/health`, sin cuerpo ni autenticación en el entorno local inicial.

Respuesta 200:

```json
{"status":"ok","api":"ok","database":"ok","pgvector":"ok","version":"0.1.0"}
```

Respuesta 503 con API accesible y base de datos inaccesible:

```json
{"status":"degraded","api":"ok","database":"unavailable","pgvector":"unavailable","version":"0.1.0"}
```

Si la conexión funciona pero falta la extensión, `database` será `ok` y `pgvector` será `unavailable`, también con 503. No se incluyen host, contraseña, consultas fallidas ni excepción original. Los esquemas reales se consultan en `/api/v1/openapi.json`; Swagger está en `/api/v1/docs`.

Frontend: timeout de 10 segundos, estado de carga, resultado, error y botón para reintentar. El estado positivo solo aparece después de una respuesta con el contrato esperado.
