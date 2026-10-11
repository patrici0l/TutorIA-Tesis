# Pares directo/RAG offline — 10 de octubre de 2026

Implementado `app.modulos.evaluacion.paired_preparation`: prepara un par del experimento A
sin buscar documentos, invocar proveedores ni modificar PostgreSQL. Disponible en código
local; no se reconstruyeron contenedores ni se cambió la interfaz.

## Controles y alcance

Ambos brazos comparten solicitud, dificultad intermedia, instrucciones pedagógicas comunes,
perfil de protocolo sintético medium, modelo candidato y límites declarados. La política
`experiment-a-medium-v1` es nueva y común a ambos brazos; no usa un perfil institucional ni
equivale a `profile-adaptation-v2`. Rechaza otra dificultad en vez de ajustarla silenciosamente.
Los prompts tienen versiones `experiment-a-pair-v1-direct` y `experiment-a-pair-v1-rag`;
los prompts de producción e históricos siguen intactos.

Varían contexto, reglas de citas/abstención y esquema: directo exige citations=[]; RAG
exige citas de las fuentes proporcionadas. Por ello el diseño evalúa ese conjunto de
diferencias, no un efecto causal aislado de añadir texto documental. Cada brazo incluye
solo su GenerationRequest. Las fuentes comunes para revisión quedan en el manifiesto,
pero no aparecen en la entrada al generador directo. No enviar el manifiesto completo a IA.

La preparación comprueba los límites y referencias del snapshot con el constructor RAG
existente, sin ejecutar una búsqueda. No autentica propiedad de documentos ni garantiza
la calidad del corpus aportado. El formato es interno, no un endpoint para clientes.
Objetivo/respuesta/fuentes pueden contener texto privado: guardar los manifiestos conforme
a la política de datos del proyecto. Los ejemplos adjuntos son totalmente sintéticos.

## Manifiesto reproducible

Conserva entrada normalizada, fuentes/snapshot de recuperación, controles comunes, prompts,
huellas SHA-256, tamaños de entrada y versiones. Estado prepared_offline, ejecuciones null.
Modelo, salida y timeout quedan null si no se declaran; orden, repeticiones, aprobación
académica y autorización de presupuesto siguen null. Declarar candidatos no autoriza envío.

`validate` reconstruye ambos brazos desde la entrada y compara el manifiesto completo:
detecta cambios de prompts, fuentes, controles, orden y estados incluso si se recalcula
su hash. Las huellas no son firmas: quien sustituya toda la entrada y reconstruya el par
obtendrá otro manifiesto válido; hace falta conservar externamente el original para acreditar
procedencia. La CLI limita archivos a 2 MiB, rechaza claves duplicadas, evita sobrescrituras
y no imprime el contenido en errores.

## Evidencia y reproducción

- [Entrada sintética](hito_11_par_a_entrada_sintetica.json).
- [Manifiesto sintético](hito_11_par_a_manifiesto_sintetico.json).

Los UUID, hashes de documentos, similitud y tiempo de recuperación del ejemplo son valores
de fixture, no mediciones reales ni documentos guardados. text_sha256 y hashes de prompts/
manifiesto sí se calculan sobre el contenido adjunto. No hay salida generada ni tokens medidos.

Desde backend:

```powershell
../.venv/Scripts/python.exe -m app.modulos.evaluacion.paired_preparation prepare ../documentacion/pruebas/hito_11_par_a_entrada_sintetica.json --output ../seguimiento_privado/par_a_nuevo.json
../.venv/Scripts/python.exe -m app.modulos.evaluacion.paired_preparation validate ../seguimiento_privado/par_a_nuevo.json
../.venv/Scripts/python.exe -m pytest -q tests/unitarios/test_paired_preparation.py tests/unitarios/test_direct_content.py tests/unitarios/test_content_contracts.py
```

Resultado real: 94 pruebas aprobadas en 0,65 s; Ruff y formato limpios. CLI prepare/validate
ejecutadas correctamente sobre el ejemplo. Pruebas de cuatro recursos, aislamiento del
contexto, controles compartidos, mutaciones, JSON duplicado, límites, no sobrescritura y
regresión de contratos directo/RAG. Sin proveedores, migraciones, despliegues o commits.

## Pendientes

El siguiente bloque local es registrar y revisar respuestas offline de ambos brazos contra
este manifiesto, conservando fallos y abstenciones sin depender de HistoryDetail RAG ni
castigar al directo por citations=[]. Después corresponde integrar ejecución/persistencia
explícitas cuando el protocolo esté acordado. Corpus/rúbrica aprobados, repeticiones,
modelo, presupuesto y revisión humana efectiva siguen pendientes; no hay benchmark cerrado.
La matriz anterior se conserva como fotografía histórica del diseño inicial.
