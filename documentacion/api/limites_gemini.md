# Límites de Gemini en TutorIA

Estado local, 7 de octubre de 2026. El autor autorizó pruebas y mostró el proyecto de la clave con Nivel gratuito. Presupuesto permitido USD 0, sin activar facturación/comprar créditos/recargas/fallback pagado. Esa confirmación satisface el requisito previo; TutorIA no consulta ni certifica el nivel de facturación de Google. Gemini Pro de la aplicación no determina el nivel de Gemini Developer API.

## Configuración exclusiva del backend

La clave GEMINI_API_KEY ya está en .env privado; nunca enviarla por chat ni ponerla en Angular/Git. Valores locales vigentes:

```dotenv
LLM_ENABLED=true
LLM_FREE_TIER_CONFIRMED=true
LLM_DAILY_REQUEST_LIMIT=5
LLM_DEFAULT_PROVIDER=gemini
LLM_MODEL=gemini-3.1-flash-lite
LLM_REQUESTS_PER_MINUTE=1
LLM_MAX_INPUT_CHARS=12000
LLM_MAX_OUTPUT_TOKENS=512
LLM_TIMEOUT_SECONDS=30
```

.env.example mantiene habilitación y confirmación false, sin clave. Para detener las llamadas: LLM_ENABLED=false y recrear backend con docker compose up -d --wait backend. No ejecutar docker compose config: imprime secretos interpolados. LLM_FREE_TIER_CONFIRMED es una declaración del operador; no bloquea por sí misma un cambio posterior de facturación en Google.

## Cupos persistentes de la ruta educativa

POST /api/v1/content/{id}/generate reserva en PostgreSQL antes de llamar a Gemini. Cinco inicios globales por día UTC, incluidos fallos/timeouts, una generación simultánea y al menos 60 s entre inicios; en Ecuador el día UTC cambia a las 19:00. La reserva se serializa con bloqueo transaccional compartido entre procesos. Reiniciar Docker no borra el consumo. Una preparación admite un único envío; si hay fallo, revisar y crear otra preparación, sin reintento automático. Intentos interrumpidos tampoco se reenvían.

LLM_DAILY_REQUEST_LIMIT admite 1–20, local 5. Ese cap alcanza solo la ruta API; scripts manuales y otros clientes de la clave están fuera. No es un tope monetario, no mide gasto ni sustituye las cuotas/condiciones del proyecto gratuito de Google. Detenerse ante cuota agotada, sin activar pago. Comprobar que el proyecto conserva Free Tier si cambian la cuenta/clave/facturación; no volver a pedir confirmación durante esta sesión sin evidencia de cambio.

Entrada limitada por caracteres/bytes, salida máxima 512 tokens y respuesta remota hasta 1 MiB; sin grounding/herramientas/caché explícita ni retries. MAX_TOKENS, JSON inválido y citas desconocidas se rechazan, no se publican respuestas parciales. Usage desconocido y costo permanecen null, no cero.

## Pruebas externas explícitas

Los antiguos scripts app.modulos.proveedores_ia.smoke y app.modulos.contenidos.smoke
se retiraron el 9 de octubre: eran ensayos iniciales fuera del contador diario API.
Sus resultados y configuración históricos se conservan en la documentación de pruebas.
Las nuevas pruebas reales deben usar el flujo de preparación/generación autenticado
con cuota persistente; no ejecutar llamadas directas para eludir límites.

Prueba UI actual: una explicación sintética con citas S1, 1388 tokens totales, 2355 ms, persistida y mostrada. Ver ../pruebas/hito_07_generacion_ui.md; prueba anterior del coordinador en hito_07_coordinador.md. No afirmar cargo efectivo cero: no se verificó gasto en Google.

La política de datos del nivel gratuito debe revisarse antes de usar corpus institucional; estos ensayos usan únicamente textos sintéticos. Referencias oficiales consultadas en la preparación previa: [facturación](https://ai.google.dev/gemini-api/docs/billing/), [cuotas](https://ai.google.dev/gemini-api/docs/rate-limits), [precios](https://ai.google.dev/gemini-api/docs/pricing) y [modelo](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite). No se reproducen límites externos como si fueran fijos; observar los del proyecto en AI Studio.

Tres pruebas UI adicionales de ejercicio/quiz/feedback pasaron sobre material sintético dentro del cupo y sin reintentos. Sus fechas UTC son 8 de octubre, fecha local aún 7; total API del nuevo día UTC tres. Evidencia ../pruebas/hito_07_cuatro_recursos.md. Se conservan nivel gratuito confirmado y presupuesto USD 0; ningún cambio de facturación ni gasto efectivo verificado.
