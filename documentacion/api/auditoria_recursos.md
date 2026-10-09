# Auditoría privada por recurso

Implementada el 8 de octubre de 2026; cierre documental el 9 de octubre.
GET `/api/v1/content/history/{id}` añade `audit` al contrato existente.
Autorización/propiedad/no-store se mantienen: teacher/admin propios, mismo 404 para recurso
ajeno/inexistente, student 403, sesión ausente 401. No hay inferencia ni mutación al consultar.
La lista paginada permanece ligera; audit solo aparece en detalle.

## Campos de audit

| Campo | Significado |
|---|---|
| generation_started_at | Reserva persistente; nullable en preparaciones/trazas antiguas |
| provider, requested_model, model_version | Proveedor/modelo conservados al ejecutar, no configuración actual |
| prompt_version, prompt_sha256 | Versión e identificador SHA-256 del prompt conservado |
| usage | input/output/total/reasoning/cached_input_tokens, cada uno nullable; uso entero reportado |
| latency_ms | Latencia registrada del proveedor, nullable |
| estimated_cost | Decimal nullable; cero condicionado a la base gratuita guardada y uso de entrada/salida conocido |
| cost_basis | Nullable; versión, moneda, proveedor/modelo y tarifa asumida del nivel gratuito confirmado por el operador |
| error_code | Solo códigos de error controlados; desconocidos se omiten como null |
| retrieval | method, query_version, embedding_model/revision/version, top_k, min_similarity, available_chunks, elapsed_ms |

Fechas de creación/finalización siguen en el nivel superior. Fuentes y adaptación se
conservan en preparation. No se devuelve prompt/instrucciones completos, response_id,
owner_id, vectores ni errores crudos. query/embedding_query se excluyen de audit: tema y
objetivo ya están disponibles. La respuesta de feedback original sigue conservada en BD,
sin añadir su texto a esta entrega de metadatos.

Angular muestra un desplegable “Ver trazabilidad de este recurso” al abrir Mis recursos.
Las ausencias se representan como Desconocido/Sin dato; cero reportado se conserva.
No renderiza HTML activo. La auditoría anterior se descarta al cambiar la preparación o
enviarla: para consultar el estado posterior hay que abrir el recurso guardado de nuevo.
No se añaden consultas automáticas, polling ni persistencia del contenido en navegador.

Los datos guardados pueden faltar tras un fallo o en trazas antiguas; no se reconstruyen
con la configuración actual. Fecha de reserva no demuestra recepción de red. El hash no
garantiza salida idéntica de un modelo probabilístico. Una cita válida no certifica todas
las afirmaciones. Esta auditoría no equivale a una exportación íntegra de experimento ni
a una política de purga. Ver [métricas](metricas.md).

Desde 0010, nuevas ejecuciones Gemini guardan `confirmed-free-tier-v1` antes del envío
bajo LLM_FREE_TIER_CONFIRMED: USD, 0 por millón de entrada/salida, procedencia
`operator_confirmed_free_tier`. No comprueba el plan real de Google ni la factura.
Uso parcial, fallo sin consumo e históricos sin base permanecen desconocidos; sin backfill.
Ver [reglas y pruebas](../pruebas/hito_10_costo_condicionado.md).
