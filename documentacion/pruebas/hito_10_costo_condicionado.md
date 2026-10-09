# Hito 10 — Estimación condicionada al nivel gratuito

Verificación del 9 de octubre de 2026. Etapas 12–13. Sin solicitudes Gemini en este bloque.

## Reglas

Tras comprobar LLM_ENABLED y LLM_FREE_TIER_CONFIRMED, la API conserva cost_basis junto
con la reserva, antes de llamar al proveedor. Versión `confirmed-free-tier-v1`, procedencia
`operator_confirmed_free_tier`, proveedor Gemini, modelo solicitado, moneda USD y tarifas
asumidas de entrada/salida de 0 por millón. Es un supuesto del operador: no comprueba el
plan real de Google ni certifica ausencia de cargos. No activa facturación.

La versión v1 no admite tarifas positivas ni otros proveedores; no es un catálogo de
precios. Tarifas generales requieren otra política y autorización de presupuesto.
Con entrada/salida conocidas y proveedor/modelo coincidentes se persiste Decimal
0.00000000 USD. Consumo parcial no se reconstruye desde el total. Timeout sin uso reportado
permanece null. Una respuesta inválida conserva consumo/estimación pero no publica recurso.
La base guardada no cambia cuando se modifica la configuración posterior.

Alembic 0010 agrega cost_basis nullable con restricción de objeto JSON. No hace backfill.
El historial privado expone la base validada y Angular etiqueta el importe como estimación
condicionada. Valores antiguos sin base no reciben moneda inventada. Métricas conserva
conteos de cobertura, sin agregar importes de diferentes bases.

## Pruebas ejecutadas

```powershell
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --build --rm test-backend python -m pytest -q tests/unitarios/test_cost_estimation.py tests/unitarios/test_generation_api.py tests/integracion/test_generation_claim.py tests/integracion/test_content_trace_database.py tests/integracion/test_content_coordinator.py tests/integracion/test_content_history.py tests/integracion/test_content_adaptation.py
```

40 aprobadas en 2.33 s; aviso existente Starlette/httpx. PostgreSQL real, fixtures reversibles,
proveedor simulado. Cubre cero, uso parcial, modelo diferente, rechazo de tarifas pagadas,
reserva durable antes de red, contrato inválido/timeout, privacidad y compatibilidad v1/v2.

Desde frontend: `npm test -- --watch=false --include=src/app/modulos/contenidos/componentes/resource-audit/resource-audit.component.spec.ts`:
3 aprobadas. Compilación de producción Docker correcta; sin nueva inspección visual.
Ruff de archivos afectados y git diff --check sin errores.
`docker compose up -d --build --wait frontend` dejó servicios saludables.
`infraestructura/scripts/check-health.ps1` verificó nginx → FastAPI → PostgreSQL/pgvector.
SQL posterior: 0010_cost_basis; 15 registros, ninguno con base/importe retroactivo;
cuatro reservas globales UTC del día. Pruebas sin registros residuales.

## Continuación

Verificar una nueva traza real dentro del próximo protocolo de evaluación, sin consumir
una llamada solo para mostrar costo. Evaluación prospectiva v4, revisión humana, benchmark
y tarifas generales no se consideran completados. Este bloque no prueba facturación cero.
Commit humano sugerido: `feat: registra estimacion condicionada de costo por generacion`.
