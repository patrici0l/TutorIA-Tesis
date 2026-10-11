# Límites configurados persistidos por ejecución

10 de octubre de 2026. Mejora de trazabilidad de etapas 12–13, sin inferencias reales,
cambio de límites activos ni evaluación académica. No reintenta pilotos.

## Problema y cambio

El historial tenía prompt/modelo/uso, pero dependía de una comprobación manual externa
para conocer si la ejecución usó límite 512 o 1024. Leer Settings al consultar después
podría atribuir a un histórico los límites actuales.

0011 añade execution_configuration JSONB nullable, con restricción de objeto.
GeneratePreparationService toma una lista explícita de tres valores no secretos del
proceso; GenerationClaimRepository los confirma junto al estado generating y la reserva
antes de llamar a Gemini. HistoryService los lee de la fila y Angular los muestra en
trazabilidad, separados de tokens y latencia reportados.

Formato: generation-config-v1, max_input_chars, max_output_tokens, timeout_seconds.
No cambia configuración del proveedor, texto, política de adaptación, fuentes, cupo,
reintentos o costos. HTTPX timeout no es un deadline global. Los parámetros implícitos
del proveedor no se inventan. El coordinador interno legado queda sin snapshot nuevo;
la ruta API con reserva es la que captura estos límites.

## Migración comprobada

Antes: 21 filas, migración 0010. Después: 21 filas, 0011_execution_configuration,
cero valores de configuración añadidos a históricos. Comparación de todos los campos
previos ordenados por ID mediante MD5 de su representación JSONB: misma huella antes y
después, excluyendo únicamente la nueva columna. Huella de control
5c1ec598642e8d0c35e79d3d61aed1ae. Es un control local de conservación, no una firma de
autenticidad. No hay backfill ni cambios retrospectivos de límite en los pilotos.

## Pruebas enfocadas

66 pruebas backend/PostgreSQL aprobadas en 1.93 s: reserva, historial, API y adaptador
Gemini con transportes ficticios. Una advertencia conocida Starlette/HTTPX. Casos nuevos:

- Configuración persistida y transacción cerrada antes de red.
- Conservación al finalizar con éxito, recurso inválido y timeout.
- Reenvío con otros límites rechazado sin reemplazar el snapshot terminal.
- Reserva ajena rechazada sin anexar configuración y lectura ajena rechazada.
- Histórico sin límites conserva null, sin defaults retrospectivos.
- Truncamiento simulado conserva los límites junto con sus metadatos seguros.
- Adaptador Gemini real con MockTransport: maxOutputTokens enviado coincide con 1024
  guardado; tras cambiar Settings a 512 el historial sigue devolviendo 1024.
- API rechaza execution_configuration enviado en el cuerpo por el cliente.

Ruff aprobado para archivos afectados. Compilación Angular local y Docker de producción
aprobadas: inicial 306.23 kB, módulo de preparación 35.91 kB; sin advertencias de tamaño.
Cinco pruebas de la vista Angular aprobadas en Docker sin red (1.98 s): límites guardados
en fallo, históricos sin defaults, ausencia de auditoría, ceros/desconocidos, metadatos
escapados y costo condicionado. El intento en Windows no ejecutó pruebas: timeout del
worker de Vitest. No se cuenta como aprobado ni se atribuye una causa no comprobada.

Despliegue Docker reconstruido y healthy; check-health confirma el recorrido nginx/API/DB.
Login mock temporal y lectura real de la preparación low salida1024: HTTP 200, contrato
HistoryDetail válido, campo execution_configuration null presente, prepared sin reserva.
Sesión de comprobación cerrada. Sin envío a generación. Conteo/huella de las 21 filas
originales siguen iguales al final; reservas diarias 3/5 y cero activas.

Reproducir el subconjunto backend con Compose de pruebas y los cinco archivos indicados
arriba. Para la vista, se usó la etapa build existente:

```powershell
docker build --file frontend/Dockerfile --target build --tag tutoria-frontend-tests:local .
docker run --rm --network none tutoria-frontend-tests:local npm test -- --watch=false --include=src/app/modulos/contenidos/componentes/resource-audit/resource-audit.component.spec.ts
```

El contexto Docker ahora excluye respaldos_locales y seguimiento_privado, además de los
secretos ya excluidos. No se añade contenido privado a las imágenes.

## Alcance y continuación

No hay consumo Gemini en estas pruebas. La ejecución salida1024 requiere comprobar
nuevamente cupo, integridad y cambio temporal de configuración antes de enviar. Sus
prompts/manifiesto no se modifican por este campo adicional de auditoría; registrar la
revisión de código utilizada al ejecutar. La recepción efectiva/estabilidad, calidad
pedagógica, revisión humana y benchmark continúan pendientes.
