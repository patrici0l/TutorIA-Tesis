# 0009: Observaciones sintéticas privadas y versionadas

Estado: implementado en desarrollo local, 7 de octubre de 2026.

El plan requiere recibir desempeño de un módulo externo, validarlo y persistirlo antes de personalizar. TutorIA no calcula notas. Como todavía no hay contrato institucional ni autorización para datos reales, el primer recorrido usa observaciones ficticias creadas por un docente autenticado.

Se conserva un payload validado y versionado en JSONB, ligado al creador, con UUID y fecha propios. Esto permite validar el caso de uso sin inventar una entidad definitiva de estudiante ni vincular identificadores enviados a cuentas UPS. Las instantáneas son inmutables y las observaciones sucesivas se guardan separadas. Los niveles y el apoyo se conservan como datos informados, sin deducirlos del porcentaje.

POST/GET privados, validación estricta, CSRF y límites reutilizan los controles existentes. La pantalla Angular permite recorrer el contrato completo sin LLM. No se modifica autenticación, corpus ni generación.

Consecuencias: la declaración synthetic no detecta información real, repetir un POST puede crear duplicados y el limitador inicial es por proceso. Deben definirse identidad/autenticación del emisor externo, idempotencia, vocabularios, retención y política institucional antes de ampliar el alcance. El hito 9 añadirá reglas explicables de adaptación y snapshot del perfil en la trazabilidad; no atribuir rendimiento académico a esta demostración.
