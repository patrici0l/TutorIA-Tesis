# Revisión de personalización sobre evidencia guardada

9 de octubre de 2026. Preparación técnica de revisión humana de la comparación v2,
sin nuevas inferencias ni aprobación académica. No es el benchmark formal de etapa 14.

## Procedimiento reproducible

Desde `backend/`, con las dependencias locales instaladas:

```powershell
../.venv/Scripts/python.exe -m app.modulos.evaluacion.offline_review ../documentacion/pruebas/hito_09_comparacion_completa.json ../seguimiento_privado/revision_perfiles.json
```

El destino debe ser un archivo nuevo: la herramienta no sobrescribe archivos, incluso
si el destino es la propia entrada. No importa configuración, credenciales, conexión BD
ni proveedores. Solo usar exportaciones sintéticas revisadas, sin información privada.
La marca synthetic valida el contrato del perfil, no anonimiza documentos o texto libre.
La revisión humana se guarda en la carpeta privada; el informe público inicial se encuentra
en [hito_09_revision_offline.json](hito_09_revision_offline.json), con decisiones pendientes.

La herramienta revalida recursos y pertenencia de citas, exige los tres niveles sin
duplicados y compara objetivo/tipo, entradas académicas, fuentes y proveedor/modelo/
versión de prompt/política. Excluye solo dificultad del request e identidad/nivel/fecha
del perfil. Conserva discrepancias como comprobaciones falsas, sin descartar selectivamente
casos. Extrae cada bloque citado y su ubicación para cotejarlo con el snapshot de entrada.
Registra SHA-256 del JSON original; no prueba que un tercero no haya alterado previamente
la exportación ni reconstruye el prompt a partir de un hash.

## Resultado técnico

Tres casos válidos, mismos factores comprobables salvo dificultad/nivel/identidad.
4577 tokens totales conocidos en 3/3 casos; separación de inicios superior a nueve horas.
La igualdad mecánica no controla aleatoriedad ni prueba causalidad. Parámetros de envío
ausentes en esta exportación se consultan en el protocolo y no se dan por verificados.
Todas las decisiones semánticas siguen null. No se asignan calificaciones automáticas.

Seis pruebas nuevas enfocadas cubren comparabilidad de fixtures sintéticas, objetivo distinto,
consumo ausente, cita desconocida, perfil no sintético, nivel inconsistente y protección
de una revisión ya existente. Con regresiones afectadas de adaptación y contratos: 57
pruebas locales aprobadas (6.17 s). Ruff aprobado. No se repitieron suites backend/frontend
completas; los conteos previos de 298/61 pertenecen a su última ejecución, no a este bloque.

## Rúbrica de revisión propuesta — synthetic-review-v1

Rúbrica operativa propuesta para revisión exploratoria; no validada por tutor/evaluador.
Completar verdict como cumple/parcial/no_cumple/no_evaluable, con evidence que señale
el bloque y texto de la fuente. Mantener null hasta revisarlo. Sin promedios ni nota global.

| Dimensión | Pregunta y evidencia necesaria |
|---|---|
| fidelity_to_sources | ¿Cada afirmación está respaldada por las fuentes citadas? Registrar fragmento y cualquier regla añadida. |
| objective_scope | ¿Respeta conceptos, función y ejemplos limitados por el objetivo? Identificar ampliaciones. |
| mathematical_correctness | ¿Los razonamientos y resultados son correctos? Mostrar comprobación independiente; no confundirla con respaldo documental. |
| difficulty_and_support | ¿El apoyo y profundidad corresponden a la política del perfil dentro del mismo objetivo? Señalar pasos, prerrequisitos y complejidad observables. |
| clarity | ¿Es legible y consistente, sin ambigüedades conceptuales? Citar pasajes concretos. |

Para cada claim completar source_support (respaldado/parcial/no_respaldado/no_evaluable)
y reviewer_note. Un bloque puede contener varias afirmaciones: separarlas en la nota y
no marcarlo respaldado solo porque una parte coincida. Anotar quién revisó y fecha en
la copia privada. No inferir satisfacción ni mejora del aprendizaje sin estudio de usuarios.

## Próximo paso dentro de etapas 11–13

Aplicar la revisión a v2 sin reemplazar sus salidas y fijar antes de ejecutar el protocolo
v3: corpus con fundamentos suficientes, mismos factores, criterios de rechazo,
repeticiones y presupuesto de intentos disponibles. La versión v3 de instrucciones no ha
sido evaluada con Gemini. Después iniciar evaluación de etapa 14 con su protocolo propio.
No conectar sistemas universitarios ni activar proveedores adicionales por este informe.
