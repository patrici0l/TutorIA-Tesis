# Instrucciones adaptadas v3 — verificación técnica

9 de octubre de 2026. Respuesta técnica a las limitaciones de
[comparación v2](hito_09_comparacion_completa.md), sin modificar sus resultados.

Backend Docker: **298 pruebas aprobadas**, 45.99 s; dos avisos de deprecación previos.
Ruff aprobado. Las 12 combinaciones de nivel/recurso construyen v3. Caso de dominio alto
con objetivo limitado y error malicioso: alcance fijo en instrucciones antes de orientación,
objetivo/error solo en datos, sin interpolación que eleve sus órdenes a instrucciones.
Límite de contexto justo probado: rechazo cuando falta un carácter, aceptación exacta y
hash estable sin quitar las restricciones. Integración existente verifica que el proveedor
ficticio recibe una sola vez el payload realmente persistido, conservando adaptación/historial.

SQL sobre los tres resultados reales originales confirma succeeded, versión v2 y hashes
sin cambios: a66539… (alto), 5dc1a2… (bajo), d967dc… (medio). No se ejecutaron llamadas
Gemini para v3. Solo hubo una llamada externa nueva en la sesión, para completar el alto v2.
Frontend sin modificaciones en este punto; conserva 61 pruebas aprobadas y build de auditoría.

Límite explícito: estos tests validan construcción/versionado/transporte de instrucciones,
no obediencia semántica del proveedor ni calidad de aprendizaje. Evaluación real de v3 queda
para protocolo posterior, sin reemplazar selectivamente el experimento anterior.
