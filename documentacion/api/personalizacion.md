# Personalización de preparaciones sintéticas

8 de octubre de 2026. POST `/api/v1/content/prepare` conserva los campos anteriores y admite `profile_id` UUID opcional. Sin identificador, el flujo manual conserva `educational-rag-v1`. No acepta payload de perfil ni reglas desde Angular. El servidor busca el perfil propio, lo valida y aplica `profile-adaptation-v1` antes de preparar fuentes/prompt.

Ejemplo: solicitud de explicación de Derivadas, dificultad advanced y perfil sintético de dominio low → respuesta prepared con dificultad basic y objeto adaptation. El recurso sigue siendo una explicación: las sugerencias de tipo son revisables por el docente, no cambian la selección automáticamente.

| Dominio informado | Dificultad efectiva | Orientación | Tipos sugeridos |
|---|---|---|---|
| low | basic | Prerrequisitos presentes en fuentes, pasos y pistas | Explicación, ejercicio, quiz |
| medium | intermediate | Explicación breve, práctica guiada | Ejercicio, quiz, explicación |
| high | advanced | Mayor complejidad y razonamiento, menos explicación básica | Ejercicio, quiz |

La política usa el dominio informado, no deduce niveles del porcentaje ni asigna notas. Desempeño, intentos, tiempo, progreso y apoyo recomendado se conservan para auditoría; no se convierten en ponderaciones sin rúbrica validada. El dominio tiene prioridad sobre el apoyo recomendado si ambos discrepan. Los retos iniciales se expresan como ejercicios/quiz de mayor complejidad; no se inventa un contrato CHALLENGE ya implementado.

Si existen etiquetas de errores, el apoyo se concentra en ellas dentro del tema. No hay ranking de gravedad ni diagnóstico de “mayor debilidad”: el contrato externo no proporciona esos datos. Se conserva el orden informado, sin extender dificultades a otros temas. Se usan los mismos corpus y consulta RAG por tema/objetivo para permitir comparaciones controladas; no se promete recuperar fuentes suficientes para cada etiqueta.

El tema debe coincidir tras NFC, casefold y compactación de espacios; se rechaza otro tema con 422. No se infieren equivalencias semánticas ni alias entre perfiles. Perfil ajeno/inexistente: mismo 404. CSRF, roles, no-store y límites existentes se conservan.

## Snapshot y prompt

La respuesta adaptation contiene política, perfil completo versionado, dificultad solicitada/efectiva, motivo, orientación, errores focalizados y recursos sugeridos. La migración 0009 añade adaptation_snapshot JSONB nullable a generaciones_contenido, con restricción de objeto. Registros previos siguen con null. No hay FK que haga depender el historial de la disponibilidad futura del perfil. Otro POST de perfil no cambia una preparación guardada.

Solo la orientación generada por reglas del servidor pasa a instrucciones del sistema. Las etiquetas de error pasan como datos no confiables `focus_errors`; no se interpolan como instrucciones. No se transmiten al proveedor el identificador ficticio, UUID, porcentaje, fechas o perfil completo. Prompt adaptado: `educational-rag-profile-v2`, con hash sobre instrucciones y datos finales y límites de entrada existentes. No se trunca contexto para ocultar excesos.

Angular `/recursos`: consultar perfiles paginados, elegir una observación (completa su tema), revisar ajuste/motivo/foco y luego generar explícitamente. La selección bloquea dificultad manual; “Usar dificultad manual” retira el perfil e invalida el resultado anterior. Reabrir historial muestra la adaptación guardada, independientemente del formulario de una nueva solicitud. Sin localStorage ni inferencia al consultar/seleccionar/preparar/restaurar.

La ruta de generación envía el prompt conservado y mantiene una llamada, cuotas y validación existentes. Este bloque verifica política/preparación/historial offline; la calidad y diferencia efectiva entre salidas Gemini para tres perfiles requieren experimentos controlados posteriores. No afirmar beneficio académico antes de evaluarlo.
