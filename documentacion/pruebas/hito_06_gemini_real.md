# Primera prueba real de Gemini

7 de octubre de 2026; autorizada directamente por el autor tras configurar su clave en .env. No se cambió facturación, no se enviaron documentos ni datos personales, y no se habilitó generación desde Angular.

## Resultado

- Dos intentos de generación con gemini-2.5-flash-lite rechazados: el adaptador devolvió llm_rejected y el diagnóstico manual confirmó HTTP 404. El catálogo listaba el modelo con generateContent; no se atribuye una causa de retirada/región sin evidencia.
- Dos consultas GET al catálogo confirmaron acceso HTTP 200 y modelos publicados. No se imprimieron headers, clave ni cuerpos remotos de error.
- Un intento manual explícito con gemini-3.1-flash-lite tuvo éxito: versión gemini-3.1-flash-lite, finish_reason STOP, latencia 962 ms, 35 tokens de entrada, 20 de salida, 55 totales y 39 caracteres de respuesta. Reasoning/cached tokens no informados quedan null.
- Texto de prueba: derivada de x², en una sola frase. No se publica como recurso educativo validado ni como experimento académico. No demuestra el flujo RAG/validación/citas, que requiere el coordinador pendiente.

Tres solicitudes de generación en total, de las que una obtuvo respuesta; ninguna se reintentó automáticamente. No se conoce el nivel de facturación de la cuenta ni su cargo efectivo. No confundir rechazo HTTP con gasto garantizado cero.

## Límites y reproducción

La prueba manual ejecutable es app.modulos.proveedores_ia.smoke, que no llama API al importarse. Cada ejecución consume como máximo un intento, entrada limitada a 1000 caracteres y 65 536 bytes por el adaptador, salida 128 tokens, timeout 15 s, frecuencia una/minuto y concurrencia una por proceso. El proceso usa settings independientes; el backend general sigue LLM_ENABLED=false.

Modelo 3.1 como predeterminado de la prueba; la elección de otro modelo requiere un argumento explícito y no se hace fallback. La respuesta solo informa metadata y longitud, no cuerpo educativo ni secretos. Docker reconstruido al cierre, Ruff y comprobación de importación sin red limpios. No hay cambios en Angular, SQL, migraciones ni contratos del adaptador previamente probados; se mantiene la evidencia de 228 backend y 42 Angular, sin presentarla como una nueva ejecución de suites.

Consultar api/limites_gemini.md para cuotas, cap mensual y limitaciones. Las tarifas publicadas sirven para estimaciones; el cargo real debe consultarse en Google AI Studio. La clave está excluida de Git.
