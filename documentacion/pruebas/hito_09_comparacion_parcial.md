# Comparación exploratoria: resultados bajo y medio

8 de octubre de 2026, America/Guayaquil. Protocolo fijado antes de ver las salidas: [comparación sintética](hito_09_protocolo_comparacion.md). Evidencia exportada desde PostgreSQL: [JSON de tres preparaciones](hito_09_comparacion_parcial.json), únicamente entradas/salidas sintéticas y metadata; sin propietario, correo institucional, sesiones ni claves.

## Control de entradas

Tres preparaciones EXPLANATION con mismo tema, objetivo, dificultad solicitada basic y datos ficticios, salvo identificador y dominio. Consulta SQL: tres registros, un sources_snapshot distinto, un request_snapshot distinto al excluir difficulty y un perfil distinto al excluir UUID/fecha/student_id/mastery_level. Por tanto, las fuentes completas y datos académicos fijos coinciden; la política modifica orientación/dificultad. Solo se usan el fragmento 25136e79-2641-45c7-938b-a295cc3a54e5 y alias S1. Hash del texto recuperado: 6a88d828d463dd478ed9927fc3c2aedd190b91ebd0387e88156d70f08d3f34c1.

| Dominio | Preparación | Estado | Dificultad efectiva | Entrada/salida/total | Latencia |
|---|---|---|---|---|---|
| low | c00981b5-8f00-4e76-87fe-c4384ab11d47 | succeeded | basic | 1161 / 381 / 1542 | 1951 ms |
| medium | 39f18cd0-5529-4e25-a025-81f098d56033 | succeeded | intermediate | 1154 / 339 / 1493 | 1999 ms |
| high | 32960f76-5d6d-43b7-9e9b-8d552c9970ed | prepared, sin enviar | advanced | Desconocido; no hay llamada | No aplica |

Gemini gemini-3.1-flash-lite, prompt educational-rag-profile-v2 y política profile-adaptation-v1. Límites existentes: 512 tokens de salida, 30 s, cinco inicios por día UTC, 60 s entre inicios; sin cambios. No se fija temperatura ni semilla en el adaptador actual: variaciones no pueden atribuirse exclusivamente al perfil. Bajo inició 2026-10-08 23:12:00.014684 UTC; medio 23:13:24.999215 UTC. Dos llamadas nuevas, sin reintentos. Uso total de este bloque: 3035 tokens conocidos. Costo estimado permanece null/desconocido; no se afirma importe facturado cero.

## Revisión exploratoria, sin puntuación académica

Ambas salidas cumplen el contrato JSON, preservan S1 y muestran concepto, pasos y ejemplo identificado como propuesto. Ambas explican f'(x)=2x. Bajo presenta dos pasos; medio tres pasos más breves. El menor consumo de salida del medio no prueba menor complejidad ni mejor adecuación. Los recursos mantienen una estructura y contenido muy similares; no se demuestra una separación pedagógica sólida entre niveles en esta muestra.

Limitación concreta de fidelidad: ambos añaden la regla general de la potencia para x^n, no enunciada expresamente en el fragmento recuperado. El ejemplo de derivada de x² coincide con la fuente y es correcto, pero una cita conocida no certifica respaldo de toda la regla general. Debe ampliarse el corpus de un futuro experimento controlado o endurecerse su revisión antes de atribuir fidelidad académica. No modificar retrospectivamente las entradas de esta comparación para ocultar la limitación.

Tras recargar Angular, las dos salidas se consultan desde historial; esto no crea nuevas llamadas. Capturas: [bajo](hito_09_comparacion_low.png) y [medio](hito_09_comparacion_medium.png). La preparación alta permanece intacta. El contador UTC 8 termina en cinco (tres anteriores + dos de este bloque). No se intentó enviarla ni se aumentó/bypasseó el cupo. El día UTC 9 empieza el 8 de octubre a las 19:00 de Guayaquil; retomar explícitamente cuando corresponda, conservando esta preparación y verificando proveedor/modelo/límites. La separación temporal será un factor documentado.

## Cierre de este punto

Comparación real parcial registrada; hito 9 completo y evaluación académica pendientes. Las suites funcionales conservan el último resultado de 292 backend/56 Angular; no se repiten por añadir evidencia y corregir textos informativos. Build Angular aprobado tras actualizar la pantalla Perfiles, que ahora explica que una observación puede usarse en Preparar recursos. Se conserva la bitácora personal fuera de Git.
