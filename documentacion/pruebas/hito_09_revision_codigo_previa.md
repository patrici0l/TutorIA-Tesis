# Revisión técnica previa al piloto salida1024

10 de octubre de 2026. Revisión de Codex del flujo de reserva, límites, proveedor y
lectura del historial; no es revisión independiente ni aprobación pedagógica.

## Resultado y alcance

Sin hallazgos nuevos que requieran modificar el código en el alcance revisado:

- La ruta genera sobre una preparación propia con sesión/rol y cabecera de protección;
  el cuerpo no acepta límites del cliente (GenerationCommand extra=forbid).
- GeneratePreparationService toma los tres límites de Settings y los entrega a la reserva.
  GenerationClaimRepository comprueba propiedad/estado/fuentes, cap UTC, intervalo y
  concurrencia bajo advisory lock; guarda límites junto al inicio y confirma antes de red.
- ExecutionConfiguration valida tipos/rangos/versionado. 0011 añade un objeto nullable
  sin reconstruir límites históricos; no altera fuentes, prompts ni política de adaptación.
- GeminiProvider utiliza el mismo Settings para entrada, maxOutputTokens y timeout, sin
  reintentos. Los parámetros no explicitados por el proveedor permanecen desconocidos.
- La finalización conserva la configuración; historial toma el snapshot de DB, no Settings
  actuales. Errores seguros/metadatos disponibles se preservan sin publicar texto truncado.

Se revisaron router/dependencias, GeneratePreparationService, GenerationClaimRepository,
GenerationRepository, GenerationTraceService, HistoryService/Repository/schemas,
ExecutionConfiguration, migración 0011, fábrica/adaptador Gemini y construcción del prompt.
La definición Owner vigente limita acceso al rol permitido por backend.

La evidencia de pruebas del bloque anterior sigue en
[límites persistidos](hito_10_configuracion_ejecucion.md): 66 backend y cinco Angular.
La prueba MockTransport verifica límite 1024 enviado y almacenado, y lectura posterior
tras cambiar Settings a 512; los casos de éxito/fallo/reenvío conservan el snapshot.
No se repitieron suites al no modificar lógica. Esta revisión no acredita una llamada
real de 1024 ni fidelidad semántica. Settings es mutable en Python, pero no existe una
ruta de actualización en caliente; si se introduce, habrá que fijar configuración por
solicitud. HTTPX timeout tampoco equivale a un plazo global de generación.

## Identificación del código comprobado

[Manifestación de hashes](hito_09_revision_codigo_previa_20261010.json), capturada
17:27 UTC /12:27 Guayaquil. 127 archivos de backend coinciden byte a byte entre workspace
y contenedor: fuentes Python de app/Alembic, requirements/base.txt y alembic.ini.
No abarca frontend, paquetes efectivamente instalados, sistema operativo, datos ni secretos.

SHA del manifiesto canónico de rutas/hashes:
`66591b104e15043970db4fc3a0c41d43fb68aff145209f2fb6d63f5c85c70c15`.
Imagen backend: `sha256:197c7b1de4e7615a48c00c343f0a9d7286b3ecbe107b0c794719137478ae82b5`.
HEAD verificado: `7dcc36d4d780a7ace4247d8a577366a299c85bd9`, rama
feature/resource-preparation. Hay cambios sin commit: HEAD por sí solo no identifica
la implementación desplegada. Usar los hashes/imagen y registrar nuevamente antes de
enviar si cambian el código o la imagen. Esto conserva evidencia técnica local, no firma
autenticidad ni sustituye el commit humano.

Reproducir hashes: para cada ruta del JSON, SHA-256 de sus bytes en backend local y /app
del contenedor; serializar el mapa ruta→SHA con json.dumps(sort_keys=True,
separators=(',', ':')) y calcular SHA-256 UTF-8. Ningún contenido de archivo se publica.

## Continuación

Preflight 17:25 UTC: tres casos íntegros, 3/5 usadas y cero activas; salida512 y selector
teacher intactos. El piloto requiere tres llamadas libres y cambio temporal1024 con
comprobación renovada. Renovación prevista19:00 local, sin ejecución automática.
No hubo Gemini, cambios de configuración, migraciones o datos en esta sesión.
Evaluación humana, comparación completa y benchmark pendientes.

Revisar/commitear únicamente esta nota, JSON y actualizaciones de plan/continuidad,
conservando separados los bloques previos. Mensaje sugerido:
`docs: registra revision e identidad del backend previo al piloto`.
