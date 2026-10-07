# Límites de Gemini para TutorIA

Actualizado el 7 de octubre de 2026. Restricción vigente del autor: presupuesto USD 0; usar únicamente el proyecto Free Tier confirmado por el autor mediante captura; no habilitar facturación ni hacer recargas. El autor autorizó pruebas reales. Se usa la clave del .env privado; nunca se muestra ni se envía por Angular. La autenticación UPS no cambia.

## Configuración local

Valores preparados en .env para la fase inicial:

```dotenv
LLM_DEFAULT_PROVIDER=gemini
LLM_MODEL=gemini-3.1-flash-lite
LLM_ENABLED=false
LLM_REQUESTS_PER_MINUTE=1
LLM_MAX_INPUT_CHARS=12000
LLM_MAX_OUTPUT_TOKENS=512
LLM_TIMEOUT_SECONDS=15
```

La aplicación sigue desactivada mientras se implementa el coordinador educativo. La prueba manual habilita únicamente su proceso, con una sola petición de texto sintético, 1000 caracteres de entrada como máximo, 128 tokens de salida y 15 segundos. No hay herramientas, grounding, caché explícita, fallback ni reintentos. El adaptador limita además la concurrencia a una petición por proceso. Una salida MAX_TOKENS se rechaza; no se publica texto incompleto.

Ejecutar manualmente solo cuando se quiera consumir una petición:

```powershell
docker compose exec -T backend python -m app.modulos.proveedores_ia.smoke --free-tier-confirmed
```

No incluir este comando en pytest, healthchecks ni arranque automático. Cada ejecución es una nueva petición, aunque se reinicie el contenedor. El cupo por minuto es por proceso y no equivale a un límite diario/mensual persistente. Los 12 000 caracteres de entrada son caracteres, no tokens; el consumo real se obtiene de usageMetadata.

## Límite económico en Google

1. Abrir Google AI Studio → Dashboard → Usage and Billing / Spend y seleccionar el proyecto de la clave.
2. Si el proyecto está en Free Tier, conservar ese nivel para ensayos sintéticos y observar sus cuotas; los límites concretos aparecen en AI Studio y dependen del modelo/proyecto. No activar facturación como efecto secundario de una prueba.
3. Si ya hay facturación, configurar Monthly spend cap → Edit spend cap. El autor no autoriza gasto: no usar este proyecto para pruebas pagadas. La propuesta previa de USD 1 quedó descartada. El estado de facturación se debe comprobar antes de cualquier petición adicional.
4. En Prepay, mantener auto-reload desactivado si se desea controlar las recargas manualmente. La compra mínima documentada es USD 5; no se realiza ninguna compra ni cambio de facturación desde esta tarea.
5. Revisar Usage y Spend después de las pruebas. Los caps de proyecto son experimentales y pueden tener retrasos de aproximadamente diez minutos; no garantizan un corte al centavo. Un presupuesto con alertas de Cloud Billing tampoco sustituye el bloqueo de solicitudes en TutorIA.

Para un tope diario o de dinero estricto dentro de TutorIA será necesario guardar reservas/consumo en PostgreSQL antes del envío, compartir cupos entre procesos y contemplar consumo desconocido en timeouts/fallos. Aún no existe esa función; no inventar LLM_MAX_DAILY_REQUESTS ni LLM_BUDGET_USD como variables efectivas.

Fuentes oficiales verificadas: [facturación y caps](https://ai.google.dev/gemini-api/docs/billing/), [cuotas](https://ai.google.dev/gemini-api/docs/rate-limits), [precios](https://ai.google.dev/gemini-api/docs/pricing), [modelo 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite). El nivel gratuito puede utilizar entradas/salidas para mejorar productos Google; se prueban únicamente textos sintéticos, sin corpus institucional ni perfiles reales.

## Prueba con RAG confirmada

El autor confirmó Nivel gratuito mediante captura. El coordinador interno ya generó y guardó una explicación con citas sobre la muestra sintética. Prueba manual: docker compose exec -T backend python -m app.modulos.contenidos.smoke --free-tier-confirmed. Cada ejecución hace una nueva petición; no usar sin confirmar el proyecto gratuito vigente. Máximo 512 tokens y 30 s; no reintenta. Ver ../pruebas/hito_07_coordinador.md. La aplicación general sigue desactivada hasta disponer de API/UI y controles persistentes.
