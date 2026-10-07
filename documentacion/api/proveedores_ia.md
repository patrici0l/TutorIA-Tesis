# Contrato interno de proveedores de IA

No hay endpoint público nuevo en este bloque. `POST /api/v1/content/generate` y los contratos educativos siguen pendientes del hito 7; no exponer prompts arbitrarios ni claves desde Angular.

## Uso interno

```python
from app.modulos.proveedores_ia.schemas import GenerationRequest
from app.modulos.proveedores_ia.servicios.llm_factory import create_provider

# Invocar solo desde el servicio educativo después de autorización,
# recuperación, composición de prompt y trazabilidad persistida.
provider = create_provider(settings)
result = provider.generate(GenerationRequest(instructions=instructions, prompt=prompt))
```

Entrada interna: `instructions` y `prompt`, texto no vacío, sin NUL/controles no textuales ni sustitutos Unicode, campos extra prohibidos. La suma debe respetar `LLM_MAX_INPUT_CHARS` y 65 536 bytes UTF-8. Modelo, proveedor, salida máxima y credenciales los fija backend; no los impone el cliente.

Salida: `provider`, `requested_model`, `model_version?`, `response_id?`, `text`, `finish_reason=STOP`, `latency_ms`, `usage` con `input_tokens?`, `output_tokens?`, `reasoning_tokens?`, `cached_input_tokens?`, `total_tokens?`. Los ausentes son `null`. Costo no calculado, versión de prompt y fuentes se añadirán al registro educativo. Ninguna clave, vector o cuerpo completo del proveedor forma parte de la salida.

## Errores internos estables

| Código | Significado |
|---|---|
| llm_disabled | Integración desactivada |
| llm_not_configured | Modelo/credencial/configuración incompletos |
| llm_unsupported_provider | Adaptador todavía no implementado |
| llm_input_limit | Entrada excede caracteres/bytes |
| llm_busy | Cupo concurrente ocupado |
| llm_rate_limit | Ventana local o cuota remota agotada |
| llm_timeout | Timeout de operación de red |
| llm_unavailable | Red/TLS o fallo remoto 5xx |
| llm_credentials | HTTP 401/403; puede requerir revisar permisos de proyecto |
| llm_rejected | Otro estado HTTP, incluyendo redirección |
| llm_blocked | Bloqueo de entrada/salida por el proveedor |
| llm_incomplete | Salida cortada por límite de tokens |
| llm_invalid_response | JSON/esquema/texto/metadata inválidos o respuesta excesiva |

El servicio educativo deberá traducirlos a respuestas HTTP seguras cuando exista; esta tabla no establece todavía códigos HTTP de rutas pendientes. No devolver texto parcial como recurso terminado ni hacer fallback/reintentos silenciosos.

## Variables del backend

Consultar `.env.example`: LLM_ENABLED, LLM_DEFAULT_PROVIDER, LLM_MODEL, GEMINI_API_KEY, LLM_TIMEOUT_SECONDS, LLM_MAX_INPUT_CHARS, LLM_MAX_OUTPUT_TOKENS y LLM_REQUESTS_PER_MINUTE. El `.env` local existente no se sobrescribe. Si conserva LLM_DEFAULT_PROVIDER=openai de una plantilla anterior, cambiarlo explícitamente a gemini antes de activar; mientras LLM_ENABLED=false no se requiere modelo/clave. No usar `docker compose config` para diagnóstico porque mostraría secretos interpolados.

Las claves existentes de OpenAI/Anthropic en la plantilla son reservas del plan; no hay adaptadores implementados para ellas. No añadir configuración de IA al frontend.
