# 0008 — Contratos educativos y preparación trazable

Fecha: 6 de octubre de 2026. Estado: preparación técnica; generación real desactivada por el autor.

Se preparan los cuatro recursos iniciales del plan: EXPLANATION, EXERCISE, QUIZ y FEEDBACK. No se adelantan perfiles/rendimiento ni personalización automática: dificultad basic/intermediate/advanced seleccionada manualmente; no se aceptan perfiles, identidades, proveedor ni modelo en ContentRequest. Gemini sigue desactivado. Recursos ampliados, rutas educativas e interfaz quedan pendientes.

## Entradas y salidas

Solicitud interna con tema, objetivo, tipo, dificultad, cantidad de preguntas solo para quiz (1–5, tres por defecto) y respuesta estudiantil solo para feedback (obligatoria). FEEDBACK inicial se centra en la respuesta al tema/objetivo; aún no incluye un expediente de intentos o una calificación académica. Campos extra, textos vacíos, controles/surrogates y opciones incoherentes se rechazan.

Cada salida tiene estructura propia y bloques de texto con citas obligatorias. Explicación: resumen/pasos/ejemplo resuelto. Ejercicio: enunciado/pistas/pasos/respuesta. Quiz: preguntas, cuatro opciones distintas, índice correcto 0–3 y explicación. Feedback: diagnóstico del contenido, corrección y siguiente paso. Textos con límite de longitud; JSON estricto sin claves duplicadas, campos extra, markdown envolvente o recursión excesiva. Las referencias deben pertenecer a los alias S1…S10 dados al modelo. Una salida cortada, de otro tipo o con un número distinto de preguntas no se publica.

Se valida estructura y pertenencia de referencias, no verdad matemática ni que una fuente justifique efectivamente cada afirmación. La revisión docente y una rúbrica independiente siguen pendientes. No se declara que el validador detecte todas las alucinaciones o inyecciones.

## Construcción del prompt

PrepareContentService usa SearchService con propietario del contexto autenticado, tema+objetivo y top-k=3. No modifica filtros de propiedad/elegibilidad. EducationalPromptBuilder mantiene instrucciones separadas del JSON de usuario/fuentes. Los textos no confiables quedan como valores JSON escapados; las instrucciones establecen que no son órdenes, no se ejecutan ni autorizan herramientas. Esto reduce ambigüedad de formato; no es una garantía de inmunidad del LLM.

Prompt educational-rag-v1, esquema de salida correspondiente y hash SHA-256 de la representación canónica de instructions/prompt. Fuentes con alias, UUID de documento/fragmento, página/párrafo, offsets, hashes existentes de documento/unidad y hash adicional del texto del fragmento. Hash de unidad no se confunde con hash del fragmento. Snapshot privado también conserva query efectiva, versiones/modelo de recuperación, similitud y parámetros. Cero fuentes impide preparar; exceso de contexto falla sin truncar o quitar citas silenciosamente. La respuesta insufficient_sources del proveedor se traduce a error seguro.

Los prompts se prueban como contratos con datos sintéticos. No se ha medido calidad de generación ni comportamiento de seguridad de Gemini real.

## Trazabilidad mínima durable

Migración nueva e inmutable 0006_content_trace crea generaciones_contenido sin alterar 0001–0005. Registra propietario, request/sources/retrieval snapshots JSONB, instructions/prompt exactos, versión/hash, fechas, estado, proveedor/modelo solicitado/versión/id de respuesta, latencia/uso conocidos, costo nullable, recurso validado y código de error. Perfil académico todavía no implementado: no se inventa ni se acepta un perfil arbitrario; se añadirá en hito 8. Costo y metadata desconocida permanecen null, no cero.

La preparación se confirma antes de una eventual llamada externa y se libera la transacción. Puede vincularse a GenerationTarget elegido en backend para registrar modelo/proveedor incluso si la red falla; un resultado de otro modelo/proveedor se rechaza. Preparaciones sin selección quedan sin ese dato y no autorizan por sí mismas llamar IA. Snapshot nunca se reconstruye a partir de documentos que hayan cambiado.

Estados prepared → succeeded o failed. Solo propietario y estado prepared permiten finalizar mediante update condicional; no hay sobrescritura de un estado terminal. La validación del recurso ocurre antes de guardarlo como éxito. Si salida inválida: recurso no guardado, error seguro y metadata de consumo conocida conservados. Fallos de transporte: código allowlist, datos desconocidos null. SQL comprueba coherencia de estado/fecha/recurso/error, costo y latencia no negativos. No se conserva salida inválida ni cuerpo de error remoto.

No hay coordinador que llame al proveedor, endpoints de historial ni métricas. Prepared no significa que se envió o se generó contenido; una interrupción futura podrá marcarse generation_interrupted explícitamente sin reintento automático. La persistencia de trazabilidad por sí sola no cierra hito 10.

## Acceso y retención

Snapshots son privados en PostgreSQL, pueden contener la respuesta estudiantil y texto fuente; no se imprimen, publican ni se guardan en navegador. Antes de habilitar historial se requiere autorización teacher/admin del corpus propio, filtros por propietario, paginación y no-store. Corpus compartido con estudiantes sigue pendiente de asignación.

Los snapshots preservan texto aun si la biblioteca elimina o cambia un documento; no existe FK de fragmento/documento que destruya evidencia por cascada. Debe definirse retención/purga antes de usar datos institucionales reales. La política actual de eliminación de archivos/vectores no purga este historial. Las pruebas hacen rollback de todos sus registros sintéticos. No se envía corpus fuera del entorno.

Ver api/contenidos.md y pruebas/hito_07_preparacion.md. Hitos 6 real, 7 completo y 10 completo permanecen pendientes.
