# 0011 — Métricas con cobertura explícita

Fecha: 8 de octubre de 2026. Estado: implementada.

Se agregan las trazas persistidas de generaciones_contenido, filtradas por propietario antes
de una única consulta de agregación. La API y Angular distinguen estado, reserva persistente y
traza de ejecución: las generaciones internas iniciales no tienen fecha de reserva y el inicio
guardado no demuestra que una solicitud haya llegado al proveedor.

Cada suma de tokens y latencia muestra cantidad conocida/desconocida. No imputamos cero ni
inferimos total_tokens. No presentamos costos como cero por la declaración Free Tier ni
calculamos importes sin moneda y tarifas versionadas. La primera entrega muestra solo cobertura
de estimaciones. No se modifica el esquema, los límites ni el flujo de generación.

Teacher/admin consultan únicamente sus agregados; student no accede. Lecturas no-store sin
contenido académico o identidad de estudiantes. Angular carga una vez y actualiza por acción
explícita, sin polling/inferencia. Las métricas técnicas no son resultados de aprendizaje ni
certifican fundamentación matemática. Retención y evaluación se trabajan por separado.
