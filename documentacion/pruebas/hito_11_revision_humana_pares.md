# Revisión humana declarada de pares A

11 de octubre de 2026. `app.modulos.evaluacion.paired_assessment` crea una plantilla
pendiente y valida decisiones humanas contra el manifiesto y lote originales.
Se confirmó el commit anterior b3b0e68 y árbol limpio al iniciar este bloque.

## Uso

Desde backend, usando el manifiesto y lote del registro offline de pares:

```powershell
../.venv/Scripts/python.exe -m app.modulos.evaluacion.paired_assessment prepare ../documentacion/pruebas/hito_11_par_a_manifiesto_sintetico.json ../seguimiento_privado/intentos_a.json ../seguimiento_privado/plantilla_a.json
../.venv/Scripts/python.exe -m app.modulos.evaluacion.paired_assessment apply ../documentacion/pruebas/hito_11_par_a_manifiesto_sintetico.json ../seguimiento_privado/intentos_a.json ../seguimiento_privado/revision_a_validada.json --assessment ../seguimiento_privado/plantilla_a.json
```

Crear primero el lote como explica [registro de respuestas](hito_11_registro_pares.md).
prepare nunca inventa respuestas, identidad o juicios. El revisor rellena solamente
reviewer_name, reviewed_at, dimensions y claims; conserva context y las rutas originales.
Los destinos deben ser nuevos; no se sobrescriben archivos ni se modifican los originales.

- Nombre y fecha se declaran juntos. Fecha con zona horaria, no futura.
- Las cinco dimensiones existentes usan meets, partially_meets o does_not_meet, junto
  con evidencia concreta. Si están pendientes, verdict/evidence permanecen null.
- Cada bloque usa supported, partial o unsupported y evidencia. supported/partial
  requieren source_aliases del corpus de referencia; unsupported puede no citar fuentes.
- Las fuentes de revisión son comunes a ambos brazos. El revisor puede indicar S1 para
  respaldar una afirmación directa aunque su salida tenga citations=[]. No se agregan
  citas al contenido original ni se confunden referencias del revisor con las del modelo.

El contexto incluye el recurso completo (también opciones y respuesta correcta de quiz),
solicitud, controles y fuentes. Claims cubre los bloques text/citations; la revisión de
opciones y estructura del recurso se documenta en las dimensiones generales.

## Comprobaciones y resultado

Se reconstruye el reporte técnico desde manifiesto y lote en cada operación. La revisión
queda vinculada a su hash; se rechazan modificaciones del contexto, casos repetidos,
omitidos/reordenados, rutas de afirmaciones ajenas, dimensiones incompletas, fuentes
ajenas/duplicadas y decisiones sin evidencia o revisor. Un caso sin recurso válido
(fallo, abstención o salida inválida) se conserva, pero no puede recibir juicios semánticos.

El resultado indica pending_human, partial o available_content_reviewed, con cobertura
explícita de dimensiones, bloques y casos sin contenido. El último estado solo significa
que se rellenaron los juicios de todo el contenido disponible, no que sean positivos.
benchmark_complete permanece false. Nombre/fecha son declaraciones, no autenticación;
la herramienta no comprueba veracidad del argumento ni otorga aprobación académica.
Se conserva la procedencia sintética/proveedor mediante el reporte original vinculado.

## Evidencia

81 pruebas enfocadas aprobadas en 2,08 s: contratos de los cuatro recursos, preparación/
aplicación CLI, revisiones pendientes/parciales/completas sintéticas, citas de referencia
para directo, manipulación, evidencia/identidad/fechas, fallos y no sobrescritura.
Incluye regresión de paired_review, paired_preparation y human_review. Ruff limpio.
Los juicios de tests son ficticios, no evaluaciones humanas reales. Sin IA, DB, cambios
de configuración, reconstrucción de contenedores ni commits automáticos.

Siguiente bloque técnico: adaptadores OpenAI/Claude con transporte simulado. Siguen
pendientes selección/autorización de modelos, credenciales para uso real, diseño aprobado,
ejecuciones y revisión académica efectiva. Gemini continúa aplazado por el autor.
