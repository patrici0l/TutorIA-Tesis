# 0007 — Interfaz de generación y primer adaptador Gemini

Fecha: 6 de octubre de 2026. Estado: base técnica implementada; activación real pendiente.

El autor eligió Gemini como primer proveedor. El plan exige desacoplar proveedores mediante `generate()`; no obliga a desarrollar los tres adaptadores a la vez. OpenAI y Claude permanecen como opciones previstas, con rechazo explícito mientras no tengan implementación. No existe fallback automático ni modelo elegido por defecto.

## Contrato y responsabilidades

`modulos/proveedores_ia/interfaces/llm_provider.py` define `LLMProvider.generate(GenerationRequest) → GenerationResult`. La fábrica selecciona un adaptador según la configuración del backend. El adaptador se limita al transporte y la normalización de su respuesta: no consulta documentos, perfiles, sesiones ni PostgreSQL, ni construye instrucciones educativas. La composición RAG/prompt y la persistencia de trazabilidad corresponden al módulo de generación del siguiente hito.

El resultado conserva proveedor, modelo solicitado, versión real y responseId si están disponibles, texto visible, razón de finalización, latencia y uso de tokens de entrada, salida, razonamiento, caché y total. Campos ausentes permanecen `null`; no se inventa consumo cero ni costo. El texto y las instrucciones quedan fuera de `repr`. Esta metadata no sustituye la trazabilidad persistida exigida antes de activar contenido real.

## Transporte Gemini

Contrato REST `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`, verificado en la [referencia oficial de Google](https://ai.google.dev/api/generate-content). `systemInstruction` y `contents` se envían por separado; una candidata, texto plano, `maxOutputTokens` configurado y `store=false`. La [autenticación oficial](https://ai.google.dev/api) especifica `x-goog-api-key`: la clave va en header, nunca en la URL. `store=false` solicita el comportamiento de logging documentado; no se atribuye a este parámetro una garantía general de retención o privacidad del proveedor.

Se usa HTTPX ya fijado en dependencias, sin SDK adicional. TLS verificado, sin redirecciones, sin proxies del entorno, sin herramientas, archivos, búsquedas externas, caché explícita ni continuidad conversacional. Host/API confirmados son constantes; modelo restringido a un identificador sin ruta ni URL. No se enviarán documentos completos desde esta capa.

Solo `finishReason=STOP` con texto visible válido se acepta. Se excluyen partes de pensamiento; respuestas bloqueadas, vacías, malformadas o truncadas por tokens se rechazan. Razones desconocidas y herramientas se rechazan. No se valida todavía exactitud matemática, citas o estructura de recursos: eso corresponde al hito 7 y la evaluación académica.

## Activación y límites

`LLM_ENABLED=false` es el valor inicial. Activar requiere proveedor Gemini, `LLM_MODEL` explícito y `GEMINI_API_KEY` exclusivamente en configuración privada del backend. Arranque y fábrica rechazan configuración activa incompleta. No se lee/modifica el `.env` existente durante este bloque, ni se publica un endpoint vacío o una respuesta ficticia en Angular.

Límites: 12 000 caracteres sumados de instrucciones/consulta por defecto (máximo configurable 24 000), 65 536 bytes UTF-8; salida por defecto 1024 tokens (configurable 128–4096), cuerpo de respuesta máximo 1 MiB, texto normalizado máximo 65 536 caracteres. El límite de entrada es por caracteres/bytes, no un conteo exacto de tokens. Timeout HTTPX de operaciones de red 30 segundos por defecto (5–60), no un deadline global de toda la generación. Un cupo concurrente y cinco intentos por minuto por defecto (1–10) compartidos por proceso; los fallos enviados también consumen intento. Las validaciones locales y rechazos por cupo no consumen intento. Nunca reintentar automáticamente una petición que podría haber sido facturada.

Estos controles no son un presupuesto monetario. Antes de llamadas reales deben acordarse modelo, tarifas/cupo del proyecto y límite de gasto; también completar permisos de corpus y persistencia mínima. Varios workers o réplicas requieren coordinación y cuotas compartidas; el control local no es una solución de producción.

Errores públicos internos solo contienen códigos `llm_*`; no conservar cuerpos de errores del proveedor, claves ni prompts en logs. Mantener el logging HTTPX/HTTPCore en WARNING como en la base existente.

## Evidencia y alcance

Pruebas mediante `httpx.MockTransport` con clave y respuesta ficticias, sin red. Cubren payload/header, intercambio por fábrica, configuración, límites, errores HTTP/transporte, bloqueos/truncamiento, metadata desconocida y liberación del cupo. No demuestran disponibilidad del modelo, credenciales, calidad del contenido, costo real ni una integración institucional. Ver `pruebas/hito_06_proveedores.md`. Hito 6 permanece parcial hasta comprobar el primer proveedor real; hitos 7–12 no se consideran completados.
