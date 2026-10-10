# Verificación de orientaciones v4 / política v2

9 de octubre de 2026. Ajuste motivado por la poca diferenciación observable en
[el piloto v3](hito_09_piloto_v3.md). Alcance: nuevas preparaciones, sin modificar
resultados o prompts guardados.

Cambios: apoyo guiado/concentrado/analítico mediante `profile-adaptation-v2`, instrucciones
`educational-rag-profile-v4` y motivo de nivel alto actualizado. Objetivo/fuentes conservan
prioridad y las etiquetas de error continúan en datos no confiables. No se introduce un
número obligatorio de pasos como sustituto de calidad ni se cambian contratos educativos.

58 pruebas enfocadas aprobadas en Docker (1.15 s); Ruff limpio. Se ejecutaron adaptación
unitaria, adaptación SQL/API, historial SQL y contratos educativos. Un aviso de deprecación
de Starlette/httpx, sin fallo. No se amplió a suite completa ni a Angular sin cambios.

Cobertura relevante:

- Doce combinaciones nivel/tipo conservan selección de recurso, privacidad y mapeo de dificultad.
- Prioridad del objetivo, errores no confiables y límite de contexto siguen verificados.
- Snapshots v1 explícitos y antiguos sin versión se leen como v1, sin renombrarlos a v2.
  Versiones desconocidas se rechazan.
- Integración parametrizada conserva y envía una vez el payload persistido tanto de
  política v1/prompt v3 como de política v2/prompt v4, usando proveedor ficticio.
  Política, hash y versión guardados permanecen intactos.
- Historial propio y rechazos por propiedad/tema siguen cubiertos; el cambio de reglas
  no reconstruye las preparaciones existentes al consultarlas o enviarlas.

Backend reconstruido en Docker. Sin migración ni cambio de Angular. No hubo llamadas
reales v4; los tres éxitos del piloto anterior pertenecen exclusivamente a v3/política v1.
Estas pruebas validan implementación y compatibilidad, no obediencia semántica del modelo.
Falta una evaluación prospectiva v4 con conjunto completo y revisión humana; no gastar
un único intento restante y presentarlo como comparación de tres perfiles.
