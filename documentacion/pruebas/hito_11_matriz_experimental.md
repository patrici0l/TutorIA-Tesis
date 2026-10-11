# Matriz experimental A/B/C y evidencia disponible

10 de octubre de 2026. Diseño propuesto, no ejecutado ni aprobado académicamente.
La instrucción vigente del autor permite continuar estas tareas dejando Gemini pendiente.
La fuente es la sección26 del plan original. [Matriz JSON](hito_11_matriz_experimental.json)
conserva ocho fuentes locales con SHA-256, capacidades verificadas y campos aún por decidir.

## Matriz de comparación

| Experimento | Qué cambia | Celdas iniciales propuestas | Qué se mantiene | Estado real |
|---|---|---|---|---|
| A: directo frente a RAG | Contexto documental entregado al generador | Directo y RAG; perfil medium | Objetivo, tipo de recurso, perfil, modelo, instrucciones comunes y límites | Falta contrato/preparación directa; no hay pares ejecutados. |
| B: personalización | Nivel low/medium/high y adaptación derivada | Tres perfiles con RAG | Observaciones sintéticas restantes, tema, objetivo, recurso, corpus, modelo, prompt/política y límites dentro de cada lote | Pilotos exploratorios disponibles; revisión humana pendiente. |
| C: proveedores | Proveedor y modelo | OpenAI, Gemini, Claude; RAG y perfil medium | Fuentes recuperadas, texto/versiones de prompt, perfil, objetivo y política de límites | Solo adaptador Gemini implementado; no hay comparación de tres proveedores. |

Punto de partida local propuesto: explicación de la derivada de f(x)=x² usando el corpus
sintético existente. No es una selección académica definitiva ni representa todo Cálculo
Diferencial. El experimento D queda condicional al tiempo y a elegir una segunda asignatura.
Se proponen2/3/3 celdas para A/B/C, no ocho ejecuciones autorizadas. Repeticiones, orden,
modelos, presupuesto, rúbrica aprobada y asignación de revisores siguen sin fijar.

## A: condiciones para una comparación válida

PrepareContentService siempre busca fuentes y construye una preparación RAG. No existe
modo directo en la API actual; no equivale a directo ocultar las fuentes en Angular.
Hace falta preparar explícitamente sin contexto recuperado y guardar su modo en la traza.
El contrato directo debe permitir ausencia de citas; no inventar S1 ni adaptar su respuesta
con citas sintéticas para superar el validador actual.

Ambos brazos deben compartir las instrucciones comunes y la estructura educativa acordada.
La diferencia esperada es el bloque de contexto/citas, no un prompt arbitrariamente mejor
para un brazo. El corpus de referencia se conserva para la evaluación humana de ambos,
aunque no se entregue al generador directo. No medir la falta de citas del brazo directo
como fallo estructural si su contrato las declara opcionales. Cotejar afirmaciones,
alcance, corrección y claridad con la misma rúbrica.

## B: qué permiten los pilotos existentes

| Lote exploratorio | Contenido disponible | Consumo total registrado | Alcance de revisión |
|---|---|---|---|
| v3, prompt v3/política v1 | Tres recursos válidos estructuralmente |7365 tokens conocidos en3 casos | Se puede revisar su contenido; faltan aprobación humana y controles de ejecución completos. |
| v4, prompt v4/política v2 | Un recurso y dos fallos llm_incomplete |2476 subtotal conocido en1 caso; total del lote desconocido | Se pueden revisar5 dimensiones/6 bloques de medium; no comparar semántica de los tres niveles. |

Fuentes: [revisión v3](hito_09_revision_offline_v3.json),
[revisión terminal v4](hito_09_revision_terminal_v4.json) y
[plantilla humana v4](hito_11_revision_humana_v4_plantilla.json).
No sumar v3 y v4 como repeticiones de una misma configuración: cambian versiones de prompt
y política, y las fechas son distintas. Las comprobaciones mecánicas del reporte antiguo
v3 no equivalen al control completo de límites que comprueba la herramienta terminal nueva.

El nivel informado también cambia dificultad y guía por diseño de AdaptationService.
Se evalúa ese conjunto de adaptación, no un efecto aislado del campo mastery_level.
Las observaciones numéricas fijas de estos perfiles son sintéticas; no representan tres
estudiantes reales ni demuestran mejora de aprendizaje. En futuras repeticiones, fijar
manifiesto y orden antes de enviar y conservar cada intento/fallo sin escoger el mejor.

## C: preparación técnica pendiente

create_provider rechaza proveedores distintos de Gemini. Nombres permitidos en Settings
o una interfaz común no significan que OpenAI/Claude ya funcionen. Faltan adaptadores,
modelos concretos autorizados y validación de sus contratos/errores con transporte ficticio
antes de cualquier llamada real. Esta matriz no solicita instalar claves ni habilitar pagos.

Fijar el mismo texto lógico de instrucciones/contexto/perfil, conservando envoltura API y
parámetros específicos por proveedor. Registrar modelo solicitado/devuelto, parámetros
explicitados y desconocidos. Un mismo límite numérico de tokens no asegura capacidad
idéntica, dado que los proveedores pueden tokenizar distinto. No normalizar costos o uso
inventando valores ausentes; la base gratuita actual solo aplica a la configuración
local registrada de Gemini, no a otros proveedores ni a una comparación futura.

## Métricas y reglas de registro

| Dimensión | Registro previsto | Regla de interpretación |
|---|---|---|
| Fidelidad, alcance, matemáticas, apoyo y claridad | Decisiones humanas con evidencia en human_review | Identidad declarada y validación del archivo no certifican conclusiones ni aprobación. |
| Validez estructural/estabilidad técnica | Estados y códigos seguros de todos los intentos | Denominador incluye fallos; recurso válido no implica calidad académica. Repeticiones aún pendientes. |
| Personalización | Cotejo de guía/apoyo/errores por nivel | No sustituir por longitud; sin tres recursos no hay comparación completa. |
| Latencia | Latencia del proveedor y recuperación separadas, con cobertura | No confundir con todo el recorrido; desconocida no es cero. |
| Tokens | Entrada/salida/total reportados y número de casos conocidos | Subtotal conocido no se etiqueta total de lote; no inventar totales. |
| Costo aproximado | Base versionada, moneda, tarifa asumida y cobertura | No certificar facturación ni trasladar una tarifa gratuita a otra configuración. |

No asignar medias pedagógicas ni pruebas estadísticas mientras no haya diseño/repeticiones
y decisiones humanas pertinentes. Mostrar tamaño de muestra, cobertura, fallos y límites.
La matriz no convierte evidencia exploratoria en resultados de benchmark A/C.

## Qué queda fijado y qué falta

La matriz identifica las preguntas, factores, celdas propuestas, controles y evidencias
actuales. Sus ocho hashes fueron cotejados contra los archivos existentes. Los conteos
v3/v4 y decisiones humanas pendientes fueron verificados; no se modificaron los originales.

Antes de un benchmark real quedan por concretar: corpus/rúbrica aprobados, repeticiones,
asignación y posible ocultamiento de proveedor al revisor, orden/bloques de ejecución,
modelos/versiones, presupuesto autorizado y modo directo/adaptadores ausentes. Los campos
son null en JSON, no se interpreta el silencio como aprobación. No se ejecutó IA, DB,
migración ni cambios de configuración. Sin suites repetidas por este bloque documental.

Próximo activo sin proveedor: implementar y probar la preparación directa interna con
modo/contrato explícitos, antes de exponer un envío o empezar comparación real.
La generación directa y benchmark siguen pendientes; se puede avanzar en su construcción
local sin llamadas. Revisar/commitear matriz MD/JSON y actualizaciones de README/plan/
continuidad. Mensaje sugerido: `docs: define matriz experimental y evidencia disponible`.
