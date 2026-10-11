# Preparación directa interna — 10 de octubre de 2026

Primer bloque de implementación del experimento A de la matriz experimental.
Disponible en código local; sin llamadas a proveedores, recuperación, persistencia,
endpoint nuevo, migraciones ni cambios de interfaz. No se reconstruyeron contenedores
para este bloque interno. El flujo público de generación conserva su contrato RAG.

## Contrato

`PrepareDirectContentService.prepare(ContentRequest, max_input_chars=12000)` devuelve
`PreparedDirectContent`: mode=direct, prompt_version=educational-direct-v1, solicitud,
GenerationRequest y SHA-256 del JSON canónico de instructions/prompt (UTF-8, claves
ordenadas, sin espacios separadores). No contiene sources_json ni retrieval_json;
no es una preparación aceptable para el repositorio RAG existente.

El prompt incluye solamente modo, solicitud y esquema de salida. Utiliza dificultad
manual, sin perfil ni política de adaptación. La solicitud y respuesta estudiantil se
delimitan como datos no confiables. Esto no demuestra resistencia empírica a inyección.
Se comprueba el presupuesto conjunto de caracteres y bytes, sin truncar entradas.

Los cuatro recursos mantienen estructura y límites educativos, con un contrato separado
de textos que exige citations=[] en cada bloque. Rechaza alias S1 u otras citas no vacías,
campos extra, textos vacíos/control, opciones repetidas y número incorrecto de preguntas.
El validador RAG sigue exigiendo sus citas habituales. No se cambiaron sus prompts/versiones.

`DirectResourceValidationService.validate(text, request)` valida JSON estricto, claves
únicas, tamaño, tipo solicitado y esquema. La abstención exacta
`{"error":"unable_to_answer"}` produce el código interno `content_unable_to_answer`;
no se expone un nuevo error HTTP. Otros códigos reutilizados: content_invalid_output,
content_wrong_resource, content_quiz_count y content_context_limit para preparación.
La validación estructural no acredita corrección matemática, suficiencia pedagógica
ni ausencia de atribuciones inventadas dentro del texto libre: requieren revisión.

## Uso local reproducible

Desde backend, con las dependencias del entorno virtual instaladas:

```powershell
../.venv/Scripts/python.exe -m pytest -q tests/unitarios/test_direct_content.py tests/unitarios/test_content_contracts.py
```

Ejemplo Python interno, sin ejecutar ningún proveedor:

```python
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.prepare_direct_content_service import (
    PrepareDirectContentService,
)

prepared = PrepareDirectContentService().prepare(ContentRequest(
    topic="Derivadas",
    learning_objective="Comprender la tasa de cambio",
    resource_type="EXPLANATION",
    difficulty="intermediate",
))
assert prepared.mode == "direct"
```

Resultado real: 74 pruebas aprobadas en 0,32 s, incluyendo los contratos RAG existentes.
Cobertura: cuatro recursos por tres dificultades, separación de modos, hash determinista,
datos no confiables, presupuestos de contexto, abstención, JSON inválido/duplicado,
profundidad/tamaño/Unicode, citas, opciones y conteos. Ruff y formato verificados.
La primera ejecución encontró errores de preparación de pruebas por nombres de casos
demasiado largos en Windows; se asignaron IDs cortos y se repitió la suite afectada.

## Lo siguiente

Construir un preparador offline de pares A con controles compartidos explícitos y
manifiesto reproducible, antes de añadir ejecución o persistencia directas. Este contrato
manual no permite afirmar que se mantiene fijo el perfil medio propuesto en la matriz:
falta resolver las instrucciones comunes y adaptación comparable de ambos brazos.
También faltan fijar corpus, rúbrica, repeticiones, modelo y presupuesto del benchmark.
No comparar automáticamente este prompt con pilotos RAG de otras versiones ni llamar
al proveedor. La matriz JSON anterior conserva su valor de fotografía histórica.
