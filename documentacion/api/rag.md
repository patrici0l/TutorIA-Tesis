# Búsqueda de fuentes

POST /api/v1/rag/search. Cookie de sesión vigente, teacher/admin y X-TutorIA-Client: web; autorización por propietario en backend. Estudiantes: 403 hasta definir asignación de corpus/curso. No acepta owner_id, roles ni selección de índice desde Angular. Cache-Control: no-store. Cuerpo JSON limitado a 16 KiB.

```json
{"query":"¿Qué representa la tasa de cambio instantánea?","top_k":3,"min_similarity":0}
```

query: 1..1000 caracteres, no vacío, NFC y espacios normalizados, sin controles ilegibles; top_k entero estricto 1..10 (defecto 5); min_similarity finita 0..1 (defecto 0). Campos extra rechazados. Tokenizer verifica límite de 512 tokens con prefijo query:; no trunca.

Respuesta 200: query original normalizada, embedding_query y query_version (calculo-alias-v1), top_k, min_similarity, available_chunks, results, method=exact_cosine, embedding_model/revision/version y elapsed_ms. available_chunks describe el corpus elegible al iniciar la búsqueda; los filtros se vuelven a aplicar en la consulta final. results contiene id del fragmento, document_id/title, filename, position, source_kind/index, char_start/end, text, document_sha256, source_sha256, processing_version y similarity coseno (-1..1, tolerancias numéricas acotadas). Nunca devuelve embeddings, tokens de sesión o identidad de otro propietario.

Selección: documento propio uploaded/no eliminado, processed/indexed y modelo/revisión/versión compatibles; vector no nulo. SQL materializa ese corpus antes de ordenar por distancia coseno ascendente y UUID para empates. Límite antes de filtrar similitud; puede devolver menos que top_k. Sin corpus devuelve results=[] sin invocar el modelo; con filtro sin coincidencias devuelve vacío sin generar una respuesta. Similitud no equivale a certeza académica ni detecta automáticamente una pregunta fuera del corpus.

Errores: 401 sesión inválida; 403 rol o CSRF; 413 cuerpo excesivo; 422 validación o exceso de tokens; 429 modelo ocupado (cupo compartido con indexación); 503 pesos ausentes/alterados, timeout o salida inválida; 500 fallo interno seguro. No se registran consultas/texto ni errores sensibles. Los resultados no se guardan en historial; trazabilidad de generación corresponde al hito 10.

El vocabulario matemático explícito normaliza división/dividir hacia cociente y multiplicación/multiplicar hacia producto para la consulta del modelo; conserva la consulta original y expone la versión/consulta efectiva. No usa un LLM. La misma muestra detectó y motivó ese ajuste, por lo que debe validarse en consultas independientes antes de atribuir generalización.
