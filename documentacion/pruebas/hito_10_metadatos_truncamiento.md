# Metadatos seguros ante truncamiento

Implementación iniciada el 9 y validada el 10 de octubre de 2026, continuación del piloto v4.
El piloto original permanece inmutable.

## Cambio

Gemini MAX_TOKENS sigue produciendo llm_incomplete y ningún recurso publicable. Ahora
ProviderError puede transportar FailureMetadata: proveedor/modelo configurados, TokenUsage
y latencia. No contiene texto parcial, pensamiento, respuesta cruda, claves ni IDs externos.
El texto de la excepción sigue siendo exclusivamente el código estable.

Cada contador solo se acepta si es entero no negativo (bool no cuenta como entero).
Valores ausentes, negativos, booleanos o cadenas permanecen null; no se convierten ni
se infieren desde el total. Un campo inválido no descarta otro válido. La latencia mide
la solicitud completada, no el tiempo total del flujo. Timeouts y fallos sin respuesta
mantienen su comportamiento anterior sin mediciones inventadas.

Ambos coordinadores internos pasan estos metadatos al cierre de la traza. Antes de
persistirlos se comprueba propietario, estado y proveedor/modelo reservado. La actualización
terminal sigue siendo condicional. Se conserva la base de costo original; importe cero
condicionado solo si entrada/salida son conocidas. No hay migraciones ni nuevo endpoint.
El historial y métricas existentes leen las mediciones sin cambios Angular.

Solo MAX_TOKENS incorpora esta extracción; otros errores conservan su contrato anterior.
No se recuperan retrospectivamente las mediciones descartadas de low/high v4. No se cambia
el límite de 512 tokens ni se repiten llamadas reales para verificar esta corrección.

## Validación

Pruebas con transporte HTTP simulado: consumo completo, parcial, inválido y ausente,
exclusión de texto parcial y una sola llamada. Integración PostgreSQL con proveedor
ficticio: fallo preservado, recurso null, consumo/latencia/costo en historial y sin reintento.
Comando de la comprobación enfocada:

```powershell
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --build --rm test-backend python -m pytest -q tests/unitarios/test_llm_provider.py tests/unitarios/test_cost_estimation.py tests/integracion/test_generation_claim.py tests/integracion/test_content_coordinator.py tests/integracion/test_content_trace_database.py
```

Siguiente paso: protocolo independiente que investigue el límite de salida antes de otra
evaluación. No confundir mayor capacidad de salida con mejora pedagógica ni cerrar hito 9.

Resultado confirmado el 10 de octubre: 80 pruebas aprobadas en 2.79 s, PostgreSQL real
y transporte/proveedores simulados. Ruff y git diff --check sin errores. La sesión de
pruebas anterior se perdió tras la interrupción; no se le atribuye un resultado. Cero
llamadas Gemini en este bloque. Sin pruebas Angular porque su contrato y vista no cambian.
