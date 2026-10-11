# Registro offline de respuestas directo/RAG

11 de octubre de 2026. Implementado `app.modulos.evaluacion.paired_review` para revisar
estructuralmente respuestas aportadas contra un manifiesto `experiment-a-pair-v1`.
Sin llamadas a IA, búsqueda, DB, endpoints ni despliegue. No es ejecución del benchmark.

## Entrada

La CLI recibe manifiesto, lote de intentos y destino nuevo. Cada lote declara:

- `manifest_sha256`: huella del manifiesto original, que se reconstruye y valida.
- `evidence_origin`: `synthetic_fixture` o `declared_provider_output`; no mezclar procedencias.
- `attempts`: entre 1 y 100 registros, con UUID `attempt_id` único, `mode` direct/rag,
  `prompt_sha256` del brazo y `outcome` response/provider_failure.
- Cada respuesta incluye `text` y no error de proveedor; cada fallo incluye un
  `error_code` conocido y no texto parcial. El estado técnico se calcula, no se acepta
  un succeeded declarado sin validar contenido.
- `target` debe coincidir con el manifiesto; es obligatorio para salida declarada de
  proveedor. `usage` y `latency_ms` son opcionales; ausencia significa desconocido.

Ejemplo de lote mínimo sintético (sustituir las dos huellas por las del manifiesto):

```json
{
  "manifest_sha256": "HUELLA_MANIFIESTO",
  "evidence_origin": "synthetic_fixture",
  "attempts": [{
    "attempt_id": "00000000-0000-4000-8000-000000000003",
    "mode": "direct",
    "prompt_sha256": "HUELLA_PROMPT_DIRECTO",
    "outcome": "response",
    "text": "{\"error\":\"unable_to_answer\"}"
  }]
}
```

Desde backend, después de guardar el lote en seguimiento_privado:

```powershell
../.venv/Scripts/python.exe -m app.modulos.evaluacion.paired_review ../documentacion/pruebas/hito_11_par_a_manifiesto_sintetico.json ../seguimiento_privado/intentos_a.json ../seguimiento_privado/revision_a.json
```

Destino exclusivo, archivos de entrada limitados a 2 MiB y rechazo de claves duplicadas.
Los errores de CLI no imprimen contenido. Conservar el lote original junto al reporte:
el reporte guarda el recurso normalizado o código seguro y huella del texto JSON canónico,
no la respuesta cruda inválida. Es material potencialmente privado; el ejemplo es sintético.

## Resultado y límites

Cada intento queda como valid_resource, abstained, invalid_output o provider_failure.
Los validadores de cada modo mantienen sus reglas: citations=[] es válido en directo;
RAG requiere alias del manifiesto. Se conserva el recurso completo, incluidos opciones
y respuestas del quiz, y bloques de texto con veredicto semántico null para revisión.
Las fuentes de referencia son las mismas para ambos modos. No hay decisiones humanas
inventadas ni puntuación automática de fidelidad/matemáticas.

Resumen por modo con todos los intentos aportados y sus estados. El subtotal conocido
de tokens se separa del total: este último es null si falta uso de cualquier intento.
Un brazo sin registros tiene cero intentos y total desconocido, no un éxito ni consumo cero.
Un cero explícito sí cuenta como dato conocido. Nunca se suman tokens sintéticos con
mediciones reales de otro lote. Latencias se conservan por intento sin medias selectivas.

UUID y hashes comprueban consistencia interna, no autentican que se hizo una llamada ni
que se aportaron todos los intentos. El orden del archivo no prueba orden de ejecución.
El manifiesto aún no fija repeticiones/aprobaciones; benchmark_complete siempre es false.
No es compatible con human_review basado en HistoryDetail: el registro de veredictos
humanos de estos pares requiere su propio contrato y sigue pendiente.

## Verificación

111 pruebas locales aprobadas en 0,99 s: registro de cuatro recursos, fallos/abstenciones,
JSON inválido, citas cruzadas, uso parcial/cero, brazo ausente, vínculo a prompt/manifiesto/
modelo, UUID duplicados, CLI sin sobrescritura y regresiones de preparación y contratos.
Ruff limpio. Todas las respuestas de prueba son fixtures; no hay nuevas salidas de IA.

Siguiente bloque: contrato de revisión humana de pares con evidencia por afirmación,
sin aprobar automáticamente la calidad. Los adaptadores OpenAI/Claude y ejecución
experimental real continúan pendientes; Gemini permanece fuera del avance activo.
