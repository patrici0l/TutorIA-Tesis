# 0013 — Objetivo y fuentes antes de adaptación

9 de octubre de 2026. Estado: implementada en instrucciones; evaluación semántica pendiente.

La comparación v2 mostró que orientación avanzada podía ampliar el ejemplo fuera del
objetivo explícito y que citas válidas no aseguraban respaldo de las reglas matemáticas.
Las nuevas preparaciones adaptadas usan educational-rag-profile-v3: objetivo educativo
delimitado y fuentes disponibles tienen prioridad sobre dificultad/apoyo. Un ejemplo
limitado no se sustituye ni se amplía, incluso si el corpus contiene otros ejercicios.
No se atribuyen reglas generales a un ejemplo ni se completa una solución sin respaldo.
Si no se puede cumplir el objetivo, el contrato insufficient_sources sigue vigente.

La orientación adapta profundidad y apoyo dentro de ese alcance. learning_objective y
errores siguen siendo datos: no autorizan cambios de seguridad y no se interpolan en
instrucciones. Identificadores de perfil permanecen excluidos del prompt. El límite de
contexto incluye las instrucciones nuevas, sin retirarlas/truncarlas para encajar.

El flujo manual permanece educational-rag-v1, la política profile-adaptation-v1 no cambia.
No se reescriben prompts/versiones/hashes de preparaciones guardadas; el envío usa su
snapshot original. Se preservan las tres salidas v2 y sus limitaciones. Instrucciones
reforzadas no son un validador semántico ni garantía de obediencia del LLM: hace falta un
experimento posterior predefinido, corpus suficiente y revisión docente. No declarar
fidelidad o evaluación académica resueltas por pasar tests de contrato.
