# Piloto v4 — ejecución y resultado no concluyente

9 de octubre de 2026, America/Guayaquil (10 de octubre UTC).
Protocolo personalizacion-x2-v4-piloto-01, sin modificación durante la ejecución.
Commit previo humano verificado adabe88. No se hicieron commits automáticos.

## Preparación

Docker estaba detenido y se inició conservando datos. Cupo consultado: 0/5 reservas
del nuevo día UTC y cero activas. Configuración: Gemini 3.1 Flash-Lite, 12000 caracteres
de entrada, 512 tokens de salida, timeout 30 s. Acceso mock docente temporal.
Se crearon tres perfiles ficticios y tres preparaciones por API autenticada, sin recargar
documentos. Fuentes idénticas entre casos y al snapshot v3, incluidos textos, IDs y hashes.
Versiones verificadas: profile-adaptation-v2 y educational-rag-profile-v4.
Preflight guardado antes de la primera inferencia en hito_09_piloto_v4_preparaciones.json.

## Resultados completos, incluidos fallos

| Nivel | ID | Inicio UTC | Estado | Uso total conocido | Latencia registrada |
|---|---|---|---|---|---|
| Bajo | c3ab007f-b3ba-472e-a805-39312ec0a29e | 2026-10-10 01:43:20.289264 | failed / llm_incomplete | null | null |
| Medio | 78efd789-7465-4865-b7e8-4489c7186963 | 2026-10-10 01:44:28.777856 | succeeded | 2476 | 19667 ms |
| Alto | d04edfe3-4860-4e3b-b0e0-92e5cb49997c | 2026-10-10 01:45:29.175312 | failed / llm_incomplete | null | null |

Equivalen a 20:43–20:45 del 9 de octubre en Guayaquil. Separaciones de inicio: 68.49 s
y 60.40 s. Una solicitud por caso, tres reservas, sin reintentos ni cambio de límites.
Detalles originales de historial: hito_09_piloto_v4_low.json, _medium.json y _high.json.

El adaptador convierte finishReason MAX_TOKENS en llm_incomplete. No se guardó contenido
truncado. Actualmente esa excepción se lanza antes de extraer usageMetadata: los null
no prueban que Google omitiera el consumo. No reconstruir ni dar por cero esos tokens.
El consumo total del lote es desconocido; 2476 es solo la parte conocida del caso medio
(2029 entrada, 447 salida). No comparar ese subtotal con el total completo v3.

Los tres casos conservaron cost_basis confirmed-free-tier-v1. Medio guardó 0E-8 USD,
equivalente a 0.00000000, condicionado al supuesto gratuito. Bajo/alto conservaron costo
null. Esto valida persistencia de base/importe en una ejecución real, no facturación.

## Lectura técnica asistida por Codex

El caso medio desarrolla x² por cociente incremental, explicita h≠0 y advierte contra
sustituir cero antes de simplificar; obtiene 2x. Sus cuatro pasos y ejemplo se apoyan
en S2, con S1 adicional en el ejemplo. No agrega otra función ni valores numéricos.
Esta observación no sustituye revisión humana. Solo un nivel tiene salida válida:
no se puede evaluar diferenciación entre niveles ni aprobar la personalización v4.
No se aplicó la herramienta de comparación de tres éxitos ocultando los dos fallos.

## Cierre y continuación

Sesiones de prueba cerradas, selector mock student restaurado; salud nginx/API/BD/vector
comprobada. Tres reservas del día UTC, cero activas, dos cupos restantes. No usarlos para
reintentar selectivamente este protocolo. Sin nuevas pruebas masivas ni cambios de código.

Siguiente bloque: conservar metadatos seguros de consumo/latencia ante respuestas
incompletas, con pruebas simuladas y sin guardar texto crudo. Después definir un protocolo
nuevo para investigar el límite de salida, antes de consumir más inferencias. No cambiar
el protocolo ni las salidas v4 ya ejecutadas. Revisión humana y benchmark siguen pendientes.
Commit humano sugerido: `test: conserva resultados completos del piloto v4`.
