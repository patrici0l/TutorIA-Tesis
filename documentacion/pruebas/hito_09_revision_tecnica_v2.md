# Revisión técnica asistida de las salidas v2

9 de octubre de 2026. Revisor: Codex. Es un análisis técnico de evidencia sintética;
no representa evaluación humana, aprobación del tutor ni medición del aprendizaje.
La [plantilla de revisión humana](hito_09_revision_offline.json) conserva sus campos
pendientes. No se modifican respuestas, fuentes ni métricas originales.

Entrada: [comparación íntegra](hito_09_comparacion_completa.json). La fuente S1 enuncia
f(x)=x² y f'(x)=2x; el objetivo de la fuente es reconocer la tasa de cambio instantánea.
Incluye el ejercicio g(x)=3x²+2x, pero no su solución ni reglas generales de derivación.
El objetivo de generación restringe la explicación al ejemplo de x².

## Cotejo por bloque citado

Los paths corresponden al informe offline. “Respaldo parcial” significa que al menos
una afirmación coincide con la fuente y otra no está explícita; no es una puntuación.

| Perfil / bloque | Cotejo técnico con S1 |
|---|---|
| low / summary | x² y su derivada 2x coinciden. La atribución a reglas de derivación polinómica añade fundamentos no enunciados: respaldo parcial. |
| low / steps[0] | Expresa la tasa de cambio instantánea y la notación del mismo ejemplo; consistente con objetivo y ejemplo de S1. La fuente no desarrolla la definición matemática. |
| low / steps[1] | Introduce d(x^n)/dx=n*x^(n-1), ausente en S1. La sustitución n=2 obtiene el resultado correcto; la regla general no queda respaldada. |
| low / worked_example | Mantiene x² y 2x, pero explica mediante una regla no presente. Respaldo parcial; el ejemplo sí está dentro del alcance. |
| medium / summary | Describe tasa de cambio de x², coherente con objetivo y función de S1. No aporta una justificación matemática que la fuente no proporciona. |
| medium / steps[0] | Identificar f(x)=x² está directamente respaldado. |
| medium / steps[1] | La regla para x^n no aparece en S1. Además, formulada sin dominio ni condiciones, es demasiado general fuera del contexto polinómico. |
| medium / steps[2] | El resultado 2x coincide; el procedimiento de bajar/restar exponente no está en S1. Respaldo parcial. |
| medium / worked_example | Misma función y resultado; vuelve a atribuirlo a la regla de la potencia ausente. Respaldo parcial. |
| high / summary | x², 2x y tasa instantánea son consistentes. La expresión sobre “comportamiento polinómico” es vaga y no aporta una justificación explícita en S1. |
| high / steps[0] | La redacción atribuye a f(x)=x² modelar una tasa proporcional a x. Quien es proporcional a x es f'(x)=2x; conviene distinguir función y derivada para evitar esta ambigüedad conceptual. |
| high / steps[1] | La relación f'(x)=2x y su interpretación coinciden con el objetivo y ejemplo de S1. |
| high / worked_example | g(x) existe como ejercicio en S1, pero g'(x)=6x+2 y las reglas término a término no están desarrolladas. El cálculo es correcto, pero sale del objetivo limitado al ejemplo x². |

## Comprobación matemática independiente

Para f(x)=x² y h≠0:
`[f(x+h)-f(x)]/h = [(x+h)²-x²]/h = 2x+h`, cuyo límite cuando h→0 es `2x`.
Para g(x)=3x²+2x:
`[g(x+h)-g(x)]/h = 6x+3h+2`, cuyo límite es `6x+2`.
Estos cálculos comprueban los resultados; no incorporan retroactivamente esas pruebas a S1.

## Conclusión técnica y cambio posterior

Hay diferencias observables de extensión/pasos y un ejemplo alto más complejo; no bastan
para concluir que cada recurso sea pedagógicamente adecuado. Ninguna de las tres salidas
permite certificar fidelidad completa a los fundamentos explícitos de S1.
La orientación avanzada debe profundizar dentro del alcance, sin introducir otra función.

El corpus original se diseñó para comprobar carga/gestión y es insuficiente para evaluar
explicaciones justificadas. El ensayo v3 empleará un texto sintético separado que explicita
el cociente incremental, el límite y la interpretación del signo para x². Cambiar corpus
y prompt simultáneamente impide atribuir una mejora solo al prompt v3. El nuevo ensayo
será una comprobación prospectiva del conjunto; una comparación causal v2/v3 exigiría
otro diseño con factores controlados. Ver [protocolo v3](hito_09_protocolo_v3.md).
