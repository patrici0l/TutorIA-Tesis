# Protocolo prospectivo de personalización v3

Identificador: `personalizacion-x2-v3-piloto-01`. Fijado el 9 de octubre de 2026, antes
de generar sus resultados. Estado al fijarlo: preparación local, todavía sin inferencias.
Etapas 11–13 del plan. No equivale al benchmark formal ni a una evaluación humana aprobada.

## Pregunta y alcance

¿Las tres orientaciones de perfil producen explicaciones distintas dentro de la misma
función y con fundamentos disponibles en el contexto? Es una comprobación exploratoria
de alcance y respaldo, sin medir aprendizaje, satisfacción ni eficacia educativa.

Nuevo corpus principal: `datos/ejemplos/derivada_x2_v3.txt`. Contiene una derivación por
definición y la interpretación del signo para x²; no incluye la regla general de potencia
ni funciones adicionales. Es sintético y fue elaborado por Codex. El corpus v2 se conserva.
Los hashes y solicitudes exactas están en [manifiesto](hito_09_protocolo_v3.json).

## Factores fijados antes de enviar

- Tema `Derivadas`, tipo `EXPLANATION`, dificultad solicitada `basic` para los tres casos.
- Objetivo idéntico del manifiesto, restringido a f(x)=x², sin otras funciones/ejercicios.
- Perfil sintético común: 42 %, cuatro intentos, error `cociente_incremental`, refuerzo,
  120 segundos y tendencia improving. Solo varían nivel low/medium/high e identificador.
- Política `profile-adaptation-v1`, instrucciones `educational-rag-profile-v3`; dificultad
  efectiva básica/intermedia/avanzada según política vigente. No cambiar reglas tras ver salidas.
- Proveedor Gemini, modelo `gemini-3.1-flash-lite`; entrada máxima 12000 caracteres,
  salida máxima 512 tokens, timeout 30 s. Sin semilla/temperatura fijadas: registrar limitación.
- Piloto de **una llamada por nivel**, orden low→medium→high, máximo tres intentos.
  No reintentar fallos ni reemplazarlos por resultados más favorables. Sin repetición estadística.
- Presupuesto autorizado USD 0, configuración local gratuita ya confirmada por el autor.
  Mantener cinco reservas/día UTC, una llamada simultánea y al menos 60 s entre inicios.
  No activar facturación, proveedores extra ni aumentar límites. Costo desconocido sigue null.

## Preparación y condiciones de envío

1. Verificar hashes del manifiesto y que las versiones/configuración coincidan.
2. Cargar/procesar/indexar el corpus principal a través del flujo docente con usuario mock.
   No eliminar ni reemplazar el corpus original para favorecer la búsqueda.
3. Registrar los tres perfiles y preparar por API/UI autenticada. Confirmar el mismo
   snapshot de fuentes en las tres preparaciones y presencia íntegra del corpus principal.
   Las únicas fuentes admitidas son el corpus principal nuevo y la muestra sintética v2
   `derivadas_sinteticas.txt`, que puede recuperarse como material adicional.
4. El top-k actual es 3, sin filtro por documento. Si aparecen otras fuentes, faltan
   fundamentos o difieren los snapshots, **no enviar**. Registrar la incidencia y corregir
   la preparación mediante una revisión del protocolo previa a cualquier resultado;
   no cambiar resultados ni fuentes ya enviados.
5. Registrar IDs, SHA de prompts/fuentes, orden, fechas UTC y parámetros reales antes
   del primer envío. Las preparaciones locales simuladas no sustituyen este control RAG.
6. Enviar solo por `POST /api/v1/content/{id}/generate`, con sesión y reserva persistente.
   Si no hay tres reservas disponibles, conservar los casos sin enviar hasta disponer de
   cupo; no eludir límites con scripts del proveedor. Documentar separación temporal.
7. Conservar cada éxito/fallo con estado, metadatos conocidos y respuesta. Recuperar del
   historial sin inferencia y exportar evidencia sintética sin cookies ni datos personales.

## Criterios fijados de lectura

Usar las cinco dimensiones de [la rúbrica propuesta](hito_09_revision_offline.md).
Revisión humana pendiente; Codex puede dejar observaciones técnicas identificadas como tales.

- Alcance: ninguna función adicional ni ejercicio nuevo. El ejemplo trabajado sigue siendo x².
- Respaldo: cada afirmación matemática debe corresponder a una fuente recibida; alias
  conocido no implica respaldo. No derivar reglas generales solo del ejemplo.
- Corrección: si se desarrolla el cociente, exigir h≠0 antes de simplificar y el límite
  correcto; distinguir función de derivada y pendiente cero puntual de función constante.
- Adaptación observable: low presenta apoyo y pasos explícitos; medium sintetiza con guía;
  high profundiza en justificación/interpretación sustentada con menos explicaciones básicas.
  No usar longitud o número de pasos como única medida de dificultad/calidad.
- Claridad: notación coherente y ausencia de ambigüedades conceptuales.

Un incumplimiento se documenta, no se oculta. `insufficient_sources`, truncamiento o error
de proveedor cuentan como resultados del intento y no aprueban el caso educativo.
El piloto solo se considera ejecutado al registrar los tres intentos; su éxito técnico
no cierra la validación académica. Si exige corrección, crear una versión posterior de
protocolo/prompt, conservando esta evidencia.

## Límites de interpretación

Una salida por nivel no mide estabilidad. El corpus y el prompt cambian frente a v2;
no atribuir diferencias exclusivamente a la instrucción nueva. No hay participantes
ni evaluadores humanos en esta preparación. CAS/integración universitaria fuera del
alcance. El experimento formal de etapa 14 deberá definir corpus, rúbrica revisada,
repeticiones y análisis antes de ejecutarse.
