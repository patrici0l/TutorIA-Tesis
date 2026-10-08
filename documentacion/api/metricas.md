# Métricas privadas de generación

GET `/api/v1/metrics`: sesión válida, rol teacher/admin, `Cache-Control: no-store`.
Solo agrega registros cuyo owner_id corresponde a la sesión, incluido el administrador.
No acepta selección de otro propietario; no devuelve identificadores, perfiles, prompts,
textos, errores del proveedor ni credenciales. Una consulta SQL produce el resumen coherente
de todo el historial propio (`scope=own_all_time`), con `observed_at` en fecha con zona horaria.
No inicia inferencia, reservas, reintentos ni escrituras. No requiere migración adicional.

Angular `/metricas` consulta al entrar y permite actualizar explícitamente; no hace polling,
no persiste datos en navegador y no permite consultas con rol student. Carga y error se
muestran sin sustituir un fallo por cifras ficticias. La navegación docente incluye Métricas.

## Interpretación

- `total_records` y prepared/generating/succeeded/failed: preparaciones y estado almacenado
  al consultar. Succeeded significa validación de estructura/citas, no calidad académica.
- `reserved_attempts`: registros con generation_started_at. No equivale a recepción por el
  proveedor. Existen trazas previas a la reserva persistente sin este campo.
- `execution_records`: fecha de reserva presente **o** estado distinto de prepared; incluye
  trazas antiguas, en curso y fallidas. Tampoco certifica una llamada de red efectiva.
- input_tokens/output_tokens/total_tokens: `known_sum`, `known_records`, `unknown_records`.
  Cobertura referida a execution_records, excluyendo las preparaciones sin enviar. Un campo
  ausente/null no se suma; sin observaciones conocidas la suma es null. Un cero reportado
  sí es conocido. Cada campo tiene cobertura independiente. El total reportado no se infiere
  sumando entrada y salida y puede incluir otros tokens según proveedor.
- latency: promedio/min/max en ms de los valores registrados, con cobertura. No representa
  extracción, recuperación, cola ni duración completa de la aplicación. Fallos sin medición
  no cuentan como cero en el promedio. Decimal del promedio se serializa como cadena JSON.
- cost_known_records/cost_unknown_records: cobertura de estimated_cost entre execution_records.
  No se calcula tarifa ni importe agregado: falta una política de precio/moneda/versionado.
  Null significa estimación desconocida; Free Tier confirmado no prueba facturación cero.

Sin registros, los conteos son cero y sumas/promedios/min/max son null. La vista no representa
el cupo global diario, no consulta Google y no mide aprendizaje. Una traza generating antigua
se muestra tal como está; la lectura no ejecuta recuperación de procesos interrumpidos.

## Límites pendientes

No hay filtros temporales, agrupación por modelo, exportación, dashboard administrativo global
ni evaluación pedagógica. El índice de owner_id existente limita la lectura a registros propios;
para volúmenes de producción habrá que medir costo de agregación y planificar paginación temporal
o resúmenes. Retención/purga y estimación monetaria versionada siguen pendientes del hito 10.
