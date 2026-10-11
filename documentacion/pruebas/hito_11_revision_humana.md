# Registro validado de revisión humana offline

10 de octubre de 2026. Preparación de evaluación del plan con evidencia ya guardada,
sin inferencias ni consulta de cuota. No constituye benchmark completado.

## Entregable y uso

`app.modulos.evaluacion.human_review` ofrece dos comandos locales. `prepare` revalida
tres historiales low/medium/high mediante trial_review y crea una plantilla. `apply`
revalida los mismos originales y las anotaciones, guarda un informe separado y conserva
el reporte técnico completo. Ambos rechazan destinos existentes; los originales no se
editan. No utiliza Settings, base de datos, proveedores ni endpoints nuevos.

Plantilla preparada con los originales v4:
[hito_11_revision_humana_v4_plantilla.json](hito_11_revision_humana_v4_plantilla.json).
Contiene contexto, fuentes y afirmaciones; decisiones, revisor y fecha siguen null.
Son datos sintéticos. Copiarla a seguimiento_privado antes de completar respuestas.

Desde backend, para crear una plantilla nueva con los tres JSON descargados del historial:

```powershell
../.venv/Scripts/python.exe -m app.modulos.evaluacion.human_review prepare ruta_low.json ruta_medium.json ruta_high.json plantilla_nueva.json
```

Para registrar una revisión rellenada en otro archivo:

```powershell
../.venv/Scripts/python.exe -m app.modulos.evaluacion.human_review apply ruta_low.json ruta_medium.json ruta_high.json informe_nuevo.json --assessment plantilla_revisada.json
```

Entradas de hasta2MiB, JSON sin claves duplicadas. Hash SHA-256 por historial vincula la
plantilla a los bytes originales; el informe también guarda el SHA de las anotaciones.
No acepta FEEDBACK sin respuesta original ni casos sin la adaptación/fechas terminales
requeridas por trial_review. No reconstruye datos ausentes.

## Qué completa el revisor

Declarar reviewer_name y reviewed_at juntos. Fecha ISO8601 con zona horaria, no futura.
Es una identidad declarada: el programa no autentica al revisor ni comprueba su autoridad.
No escribir secretos o datos institucionales en las notas.

En dimensions, cada dimensión acepta meets, partially_meets o does_not_meet con evidence
concreta. Sin decisión, ambos campos quedan null. Rúbrica propuesta synthetic-review-v1:

| Dimensión | Qué cotejar en el recurso disponible |
|---|---|
| fidelity_to_sources | Si las afirmaciones están respaldadas por las fuentes conservadas. |
| objective_scope | Si cumple el objetivo sin agregar funciones o tareas fuera de su alcance. |
| mathematical_correctness | Si fórmulas, operaciones y explicaciones son correctas. |
| difficulty_and_support | Si el apoyo responde al perfil y error declarado, sin inferir aprendizaje. |
| clarity | Si la explicación es comprensible y sus pasos están conectados. |

En claims, cada bloque admite support=supported/partial/unsupported, evidence y
source_aliases. Supported/partial necesitan al menos un alias citado por el bloque;
unsupported puede no tener alias, con evidencia del problema. No agregar, quitar o
duplicar afirmaciones. El texto de evidencia debe localizar el pasaje y explicar el cotejo,
no limitarse a repetir el veredicto. El programa exige texto, pero no juzga su calidad.

No cambiar context, id, level, status, content_review_available o input_files. No rellenar
dimensiones de un fallo sin contenido. La pertenencia de un alias no demuestra respaldo:
esa conclusión sigue siendo responsabilidad de la persona que revisa.

## Estados y límites

- pending_human: ninguna decisión registrada.
- partial: parte del contenido disponible revisada.
- available_content_reviewed: todas sus dimensiones/afirmaciones tienen decisiones.

El último estado significa cobertura del registro; no aprobación, puntuación, consenso,
causalidad ni revisión de casos fallidos. Se conservan los controles técnicos incompletos,
tokens desconocidos y disponibilidad original de los tres niveles. No se calcula una nota
promedio ni se declara un recurso apto automáticamente.

## Verificación del bloque

41 pruebas offline enfocadas aprobadas en0.45s: revisión nueva y regresiones de las dos
herramientas anteriores. Casos de plantilla pendiente, revisión parcial/completa del
contenido disponible, fallos conservados, evidencia/nombre ausentes, contexto alterado
(incluye cero convertido a booleano), hashes distintos, IDs/dimensiones/afirmaciones
ajenos, alias inválidos, fecha futura/sin zona y rechazo de sobrescritura de entradas.
Ruff/formato aprobados.

Plantilla v4 creada y validada sin anotaciones: pending_human, cero decisiones, cinco
dimensiones y seis afirmaciones disponibles en medium; low/high siguen fallidos.
No se asignó identidad ni se completó una evaluación humana real.

Backend reconstruido con el módulo y CLI --help comprobada en el contenedor. Al verificar
el entorno, PostgreSQL estaba inactivo y health respondió503; se inició el servicio con
su volumen existente y se recuperó la conexión, sin atribuir una causa no comprobada.
Frontend reanudado y check-health aprobado. Las21 generaciones conservan la huella de
campos previos `5c1ec598642e8d0c35e79d3d61aed1ae`. Sin migraciones ni cambios de límites.
La identificación del backend de la revisión técnica anterior es evidencia histórica;
una identificación futura deberá incluir este módulo nuevo.

Próximo: matriz experimental de A/B/C con requisitos y evidencia disponible, conservando
Gemini pendiente por instrucción del autor. Sigue pendiente una rúbrica aprobada y revisión
humana efectiva. Revisar/commitear módulo, pruebas, plantilla y documentación de este bloque.
Mensaje sugerido: `feat: valida revisiones humanas de resultados guardados`.
