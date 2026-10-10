# Revisión técnica y preparación de revisión humana del piloto v4

10 de octubre de 2026. Observaciones técnicas de Codex sobre evidencia sintética
guardada. No constituye evaluación humana, aprobación del tutor ni medición de aprendizaje.
Etapas 11–13: no cierra personalización ni inicia el benchmark formal.

## Evidencia y cobertura

[Paquete de revisión](hito_09_revision_v4.json): conserva los tres casos del
[piloto v4](hito_09_piloto_v4.md), sus fuentes, adaptación, auditoría y SHA-256 de
cada archivo de entrada. Las decisiones humanas, revisor y fecha permanecen null.
Las observaciones de Codex están en un campo independiente.

| Nivel | Estado original | Recurso revisable | Consumo total conocido |
|---|---|---|---|
| Bajo | failed / llm_incomplete | No | null |
| Medio | succeeded | Sí, seis bloques citados | 2476 |
| Alto | failed / llm_incomplete | No | null |

Las tres exportaciones pasan el contrato HistoryDetail; el recurso medio también
pasa ResourceValidationService con su petición y aliases de fuentes. Los snapshots
de fuentes son idénticos entre casos. Estas comprobaciones validan estructura y
pertenencia de citas, sin certificar respaldo semántico.

2476 es un subtotal conocido de un caso, no el consumo total del lote. Los dos fallos
conservan uso, latencia y costo desconocidos. No se reconstruyen con la corrección
posterior de metadatos. No existe contenido truncado guardado para evaluar.

## Cotejo del caso medio con las fuentes originales

Los paths se refieren al campo resource. S1 enuncia x², 2x y el objetivo de tasa de
cambio; S2 desarrolla el cociente incremental, las condiciones, el límite y la
interpretación de la pendiente para la misma función.

| Bloque | Observación técnica de respaldo |
|---|---|
| summary | La interpretación como tasa instantánea y el límite del cociente aparecen en S2. Mantiene x². |
| steps[0] | Cociente [f(x+h)−f(x)]/h y condición h≠0 explícitos en S2. |
| steps[1] | Expansión (x+h)²=x²+2xh+h² y resta de x² explícitas en S2. |
| steps[2] | Cancelación de h y resultado 2x+h explícitos en S2. La condición h≠0 queda establecida en el primer paso. |
| steps[3] | Límite h→0 y advertencia sobre división por cero explícitos en S2. |
| worked_example | S1 respalda función y resultado; S2 respalda además procedimiento e interpretación. No añade otra función ni un valor numérico. |

Comprobación matemática independiente: para x real y h≠0,
[(x+h)²−x²]/h=(2xh+h²)/h=2x+h; su límite al tender h a cero es 2x.
El cálculo comprueba el resultado; no convierte una cita en aprobación pedagógica.

La advertencia sobre h=0 atiende el error informado cociente_incremental. La salida
mantiene cuatro pasos elementales separados. La guía de nivel medio pedía concentrar
operaciones rutinarias: el evaluador debe revisar si esa organización ofrece el apoyo
intermedio esperado. No asignar una nota por cantidad de pasos, longitud o metadatos.

## Cómo realizar la revisión humana

Copiar el JSON a seguimiento_privado antes de completarlo; conservar el paquete público
como evidencia inicial. Leer cada bloque junto con sus fuentes y registrar source_support
y reviewer_note. Para las cinco dimensiones de synthetic-review-v1, completar verdict
y evidence según la [rúbrica](hito_09_revision_offline.md), con revisor y fecha reales.

En bajo/alto registrar no_evaluable por ausencia de recurso, sin inventar respuestas.
En medio distinguir corrección, respaldo, alcance, apoyo y claridad. La diferenciación
entre tres niveles sigue no evaluable: un recurso válido de tres no permite compararla.
No rellenar campos humanos con las observaciones de Codex como si fueran aprobación.

## Disponibilidad de la comparación de salida 1024

Comprobación del 10 de octubre, 15:42 UTC (10:42 Guayaquil): tres reservas de cinco,
cero activas. No alcanza para iniciar el lote de tres. No se hicieron inferencias,
modificaciones de configuración ni aumento de cuota.

[Lectura inicial](hito_09_salida1024_disponibilidad_20261010.json) conserva configuración
no sensible y estado de los tres IDs. El cotejo directo de fuentes DB/API dio false:
la DB tiene el campo interno text_sha256, ausente de la representación de la API.
No es evidencia de alteración del texto. El [cotejo específico posterior](hito_09_salida1024_integridad_20261010.json)
confirma todos los campos públicos iguales, snapshots internos idénticos a sus casos
v4 originales y hashes internos de texto correctos. No se ocultó el resultado inicial.

Los tres IDs siguen prepared, sin reserva; prompts y adaptación coinciden con el preflight.
Los documentos siguen disponibles. La configuración observada es mock teacher y salida
512; se conserva como estaba al consultar. No equivale a verificación de envío con 1024.
El SHA del manifiesto coincide con el preflight guardado.

La siguiente renovación diaria corresponde al 10 de octubre a las 19:00 de Guayaquil.
Al retomar, volver a comprobar cuota, actividad, integridad y configuración: esta consulta
no reserva cupos futuros. Ejecutar únicamente los IDs existentes según el
[protocolo salida1024](hito_09_protocolo_salida1024.md), con cambio temporal verificado
a 1024 y restauración posterior. No hay ejecución automática ni reintentos del piloto v4.

## Verificación de este bloque

Contratos revalidados localmente sobre las tres exportaciones; recurso/citas del medio
revalidados; seis bloques extraídos y hashes de entrada conservados. Consultas SQL de
solo lectura para cuota e integridad, sin consultar identidades ni secretos. No se
repitieron suites completas por cambios únicamente documentales. Revisión humana y
ejecución salida1024 siguen pendientes.
