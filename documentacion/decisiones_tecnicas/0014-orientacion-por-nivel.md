# 0014 — Orientaciones concretas de apoyo y profundidad

9 de octubre de 2026. Estado: ajuste técnico de instrucciones; evaluación real pendiente.

El piloto v3 produjo cuatro pasos de derivación similares para los tres niveles. Aunque
se respetó la función y se usaron fundamentos disponibles, la diferencia pedagógica fue
pequeña. La indicación genérica de mayor complejidad no especificaba qué debía cambiar.

Las nuevas preparaciones usan `profile-adaptation-v2` y `educational-rag-profile-v4`:

| Nivel | Prioridad propuesta |
|---|---|
| low | Apoyo guiado: símbolos/prerrequisitos disponibles, transiciones justificadas y advertencia sobre el error informado. |
| medium | Guía concentrada: transiciones esenciales y decisión que evita el error, agrupando operaciones rutinarias sin repetir todas las definiciones. |
| high | Profundidad conceptual: condiciones de validez, consecuencias e interpretación del mismo caso; sintetizar el cálculo rutinario. |

No se impone una cantidad de pasos como sustituto de calidad. Las orientaciones incluyen
indicaciones específicas para EXPLANATION y mantienen el contrato de ejercicio/quiz/feedback.
La selección de recurso del docente, el objetivo y las fuentes tienen prioridad. No inventar
valores numéricos ni fundamentos para aparentar diferencia; reconocer límites del contexto.
Se mantiene foco localizado sin inferir gravedad, notas o diagnósticos.

La API acepta snapshots históricos v1 y actuales v2. La ausencia de versión en un snapshot
antiguo sigue interpretándose como v1; solo el servicio de nuevas preparaciones emite v2
explícitamente. No se migra ni recalcula el contenido guardado. El envío usa instrucciones,
hash y perfil persistidos, incluso si después cambian las reglas. Angular acepta la versión
como texto y muestra el motivo guardado; no requiere cambios de contrato ni migraciones.

Este ajuste no es un validador semántico ni una prueba de eficacia. La evaluación posterior
necesita un protocolo nuevo, misma función/corpus/factores y presupuesto suficiente para
el conjunto; no repetir selectivamente un resultado. El piloto v3 queda íntegro y no se
atribuye a v4 ningún resultado anterior. No consumir el único intento diario restante para
presentarlo como comparación completa de tres niveles.
