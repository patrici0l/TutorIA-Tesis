# Adaptadores OpenAI y Claude — 11 de octubre de 2026

Implementados OpenAIProvider y ClaudeProvider mediante HTTPX, integrados en create_provider.
Contrato común GenerationRequest/GenerationResult, modelo explícito, errores seguros y
limitador compartido. Gemini conserva su transporte y añade comprobación del proveedor
seleccionado para impedir una instancia directa con configuración de otro adaptador.

## Contratos oficiales consultados

OpenAI usa POST /v1/responses, instructions e input separados, max_output_tokens,
store=false, stream=false y herramientas vacías. Lee mensajes output_text dentro de output,
sin asumir la primera posición ni devolver elementos de razonamiento. Referencias:
[generación de texto](https://developers.openai.com/api/docs/guides/text) y
[salidas incompletas](https://developers.openai.com/api/docs/guides/reasoning).

Claude usa POST /v1/messages, system separado, mensajes de usuario, max_tokens,
x-api-key y anthropic-version=2023-06-01. Acepta end_turn; max_tokens/contexto agotado
se consideran incompletos, refusal se clasifica como bloqueo. Referencias:
[API y autenticación](https://platform.claude.com/docs/en/api/overview),
[Messages](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) y
[motivos de parada](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons).
Alcance inicial: clave asociada a un solo workspace; no soporte de claves multi-workspace.

Ambos rechazan salidas vacías, herramientas o formatos inesperados, sin ejecutar acciones,
continuar automáticamente ni usar fallback. No se selecciona un modelo comercial en este
bloque; model-test identifica exclusivamente fixtures. No se afirma acceso real a modelos.

## Configuración y autorización

Settings agrega OPENAI_API_KEY y ANTHROPIC_API_KEY como SecretStr, con entradas vacías
en .env.example y paso al backend mediante Compose. No se leyó/modificó .env ni se
añadieron claves reales. LLM_DEFAULT_PROVIDER admite gemini/openai/claude; la clave se
valida para el proveedor seleccionado, con modelo explícito y sin espacios/control.
La configuración desactivada no requiere credenciales. No hay nuevas dependencias SDK.

La fábrica puede construir los adaptadores internos, pero GeneratePreparationService
rechaza OpenAI/Claude antes de construir proveedor o reservar una generación. La bandera
LLM_FREE_TIER_CONFIRMED pertenece al flujo Gemini existente: no autoriza estos proveedores.
La integración de envío API/UI con autorización y límites de presupuesto sigue pendiente.
No se hicieron peticiones reales, pagos, consultas de cuota ni cambios de proveedor activo.

El adaptador de bajo nivel tiene capacidad de red si se lo invoca explícitamente con
configuración válida; no implementa el cupo diario persistente del coordinador. No debe
usarse como endpoint ni como alternativa para eludir las reservas/presupuesto.

## Límites y trazabilidad

Entrada limitada por caracteres/bytes, respuesta HTTP a 1 MiB, texto a 65536 caracteres,
timeout HTTP configurado, exclusión mutua y límite de peticiones por minuto. Sin proxies
de entorno, redirecciones ni reintentos. Timeout es de operaciones HTTPX, no una garantía
de tiempo total absoluto frente a un servidor que entregue fragmentos lentamente.
401/403, 429, 5xx, rechazos y problemas de conexión se convierten en códigos estables.
No se registran cuerpos de error, claves ni texto parcial en FailureMetadata.

Se conserva modelo solicitado/devuelto, ID, latencia y uso disponible; valores inválidos
quedan null. OpenAI conserva total y detalles de razonamiento/caché si son informados.
Claude conserva entrada, salida y lectura de caché, pero total_tokens permanece desconocido:
no se inventa un total ni se suma ignorando categorías como escritura de caché.
Truncamiento/bloqueo conservan mediciones disponibles sin respuesta parcial.
No se calcula precio ni se afirma costo cero por disponer de un adaptador.

## Pruebas y estado de entrega

107 pruebas enfocadas aprobadas en 1,65 s: adaptadores nuevos, Gemini, Settings y ruta API.
HTTPX MockTransport y claves ficticias en todos los casos; payload/headers, respuestas,
refusals/truncamiento, datos inválidos/voluminosos, uso faltante/cero, HTTP/timeout/conexión,
límites, ausencia de reintentos y bloqueo del envío API. Ruff limpio. Una advertencia
conocida de compatibilidad Starlette/HTTPX.

La primera ejecución de ruta API no recolectó por falta de pgvector en el entorno virtual.
Docker estaba detenido y la construcción de test-backend no pudo iniciarse. Se instaló
localmente pgvector==0.5.0, versión ya fijada en requirements/base.txt, y las pruebas pasaron.
No se cambió el archivo de dependencias, no se desplegó ni se modificaron datos/volúmenes.

Próximo bloque: integrar y probar el recorrido experimental desde manifiesto hasta registro
con proveedores simulados, fijando controles de ejecución. Después quedan autorización/
presupuesto por proveedor, elección de modelos y comprobaciones reales explícitas, más
la evaluación humana efectiva. Esta entrega no cierra benchmark ni prueba disponibilidad real.
