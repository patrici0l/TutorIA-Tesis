# Protocolo prospectivo de personalización v4

Fijado el 9 de octubre de 2026 antes de ejecutar: `personalizacion-x2-v4-piloto-01`.
Estado: sin preparaciones nuevas ni inferencias. Etapas 11–13, no benchmark formal.
Manifiesto: [parámetros exactos](hito_09_protocolo_v4.json).

## Pregunta y controles

¿La política v2/prompt v4 produce apoyo guiado, concentrado y analítico según nivel,
sin salir del objetivo f(x)=x² ni añadir fundamentos ausentes?
Se conserva objetivo, corpus, métricas sintéticas y límites del piloto v3. Solo cambian
identidades ficticias, política y prompt. Una salida por nivel, low → medium → high,
tres intentos máximos en total. No reintentar errores ni seleccionar mejores respuestas.
No se fijan temperatura/semilla; comparación exploratoria sin atribución causal.

Gemini gemini-3.1-flash-lite, entrada 12000 caracteres, salida 512 tokens, timeout 30 s.
Presupuesto autorizado USD 0; sin activar pagos ni otros proveedores. Cinco inicios/día
UTC, uno simultáneo, separación mínima 60 s. Iniciar solo con al menos tres cupos libres.
El 9 de octubre a las 21:09 UTC había cuatro reservas y cero activas: no se envió nada.
No hay programación automática: al retomar se vuelve a comprobar el cupo real.

## Integridad del corpus

Reutilizar los documentos ya indexados del piloto v3, sin volver a cargarlos:

- Principal: documento 5b0e79d5-5989-453a-b1f3-a3946873f19a,
  fragmento 7dfe36e9-1a1c-4bd3-87e0-904b2fb839be.
- Complementario: documento 84ed0928-238d-46ec-9de2-8f704249ddc3,
  fragmento 25136e79-2641-45c7-938b-a295cc3a54e5.

El manifiesto conserva sha256 de bytes cargados y añade working_tree_sha256.
El complementario fue cargado con CRLF: 8a281568815d0381a75a66fe4004806aa424a520cb8f6b145eeda104e5f08789.
Git conserva LF: b7d0510c51faa4f51768eb24964dc17f63a5a54a8822efa082ba5e06b71d755d.
Se comprobó que convertir únicamente LF→CRLF reproduce exactamente la huella anterior.
No se alteraron archivo, corpus indexado ni evidencia v3. El principal coincide byte a byte.

## Ejecución al disponer de cupo

1. Confirmar versiones, configuración no sensible, corpus y cupo. Acceso mock docente.
2. Crear perfiles del manifiesto y preparar por API autenticada, sin llamar al proveedor.
3. Comprobar que las fuentes son iguales entre casos y coinciden con los snapshots v3,
   incluidos IDs, textos y hashes. Cualquier discrepancia detiene el envío y se documenta.
4. Guardar IDs, hashes de prompts, versiones y hash del manifiesto antes del primer envío.
5. Generar solo por POST /api/v1/content/{id}/generate con sesión/CSRF. Conservar cada
   éxito/fallo; si hay interrupción, consultar historial y no repetir una reserva existente.
6. Exportar respuestas sintéticas, tiempos y uso conocido. Verificar cost_basis versión
   confirmed-free-tier-v1 en historial; 0 condicionado con entrada/salida conocidas,
   null si faltan. No interpretar el dato como comprobante de factura.
7. Restaurar selector mock y cerrar sesión de prueba; guardar cuota final y limitaciones.

## Revisión previamente definida

Aplicar synthetic-review-v1: fidelidad, alcance, corrección, adaptación y claridad.
Low debe explicar símbolos/transiciones; medium concentrar pasos esenciales; high
justificar condiciones e interpretación. El número de pasos no es una calificación.
No añadir funciones, ejercicios o valores numéricos ausentes para aparentar complejidad.
Si aparece cociente incremental, revisar h≠0, límite y distinción de pendiente/función.
Registrar cada afirmación añadida y si es deducción válida o contenido explícito de fuente.
Truncamiento, fuente insuficiente y fallo de proveedor cuentan como resultados no aprobados.
Decisiones humanas permanecen pendientes hasta revisión real, sin notas automáticas.

## Revisión previa preparada

La herramienta offline procesó los tres resultados v3 guardados: cuatro controles mecánicos
verdaderos, 7365 tokens conocidos, revisión semántica pendiente. La plantilla editable está
en seguimiento_privado/revision_perfiles_v3.json y permanece fuera de Git. No implica que
una persona haya revisado o aprobado los resultados. Evidencia pública v3 sin modificaciones.
