# 0004 — Extracción y segmentación trazables

Fecha: 6 de octubre de 2026. Estado: implementado para desarrollo local. Alcance: primera parte del hito 4; embeddings e índices siguen pendientes.

## Flujo y propiedad

La biblioteca conserva sus permisos teacher/admin y acceso a documentos propios. POST /documents/{id}/process llama a IngestDocumentService y ChunkRepository; el router no extrae texto ni ejecuta SQL. Un proceso Python separado comprueba tamaño y SHA-256 del archivo privado, extrae unidades y devuelve un resultado JSON privado. Su salida y los diagnósticos del parser no se registran. No se abren URLs del documento ni se envía contenido a terceros.

## Trazabilidad y reproducción

Versión text-v1 cubre extracción, normalización y segmentación. Se conserva SHA-256 del archivo cargado, versión, límite/solapamiento en caracteres, fecha, número de fragmentos y caracteres normalizados. Cada fragmento guarda el SHA-256 UTF-8 de su unidad normalizada y referencias a página o párrafo. Los offsets son [inicio, fin) en puntos de código Unicode. La normalización NFC conserva superíndices Unicode; no aplica NFKC, desguionización automática ni simplificación de fórmulas.

Configuración inicial: DOCUMENT_CHUNK_CHARS=1000 y DOCUMENT_CHUNK_OVERLAP=150, ambos configurables y validados. Los cortes prefieren finales de oración/salto de línea y luego espacios; el solapamiento mantiene offsets exactos y progreso. Nunca se cruza una página o párrafo. Son caracteres, no tokens: el próximo bloque deberá controlar límites del tokenizer del modelo elegido.

La operación processed es idempotente y conserva IDs/configuración. No se reprocesa silenciosamente al cambiar .env. La reconstrucción explícita y versionado de índices se concretarán antes de vectorizar. Las dependencias están fijadas en requirements/base.txt; la evidencia registra los entornos efectivamente probados.

## Límites e intentos

Hasta 10 MiB de archivo, 200 páginas PDF, 500 000 caracteres y 1000 unidades/fragmentos. DOCX limita también entradas ZIP, ratio, tamaño por entrada y total expandido (50 MiB), XML seguro, referencias externas y contenido activo. La validación inicial de carga continúa vigente.

EXTRACTION_TIMEOUT_SECONDS=15, configurable entre 5 y 20, limita tiempo de pared y termina el proceso hijo. En Docker Linux se aplican además RLIMIT_AS=384 MiB y RLIMIT_CPU=20 segundos por hijo. En Windows nativo se mantiene timeout y límites de contenido, pero no RLIMIT; la comprobación de aislamiento corresponde a Docker. Hay como máximo dos hijos simultáneos por proceso API; más réplicas requieren una cola/coordinación compartida. Nginx espera 30 segundos para las rutas de API generales.

Una actualización SQL condicional reclama pending/failed o un intento processing vencido tras dos minutos, asignando un UUID interno. La publicación comprueba token/estado/no eliminación y conserva el bloqueo de fila hasta guardar todos los fragmentos y metadatos. Un intento tardío no modifica resultados posteriores. DELETE invalida el token y borra fragmentos en la misma transacción. No hay transacciones abiertas durante la extracción que bloqueen el documento. Un fallo no publica resultados parciales.

## Límites del contenido académico

PDF requiere capa de texto. No se realiza OCR ni reconstrucción de imágenes, fórmulas dibujadas o lectura garantizada de columnas; un PDF vacío/escaneado informa empty_text. El docente debe cotejar los fragmentos antes de usar corpus real.

DOCX extrae párrafos del documento principal, incluidos los de tablas, conservando referencias XML originales. Encabezados/pies, notas y disposición visual no se reconstruyen. Super/subscript directo de Word se representa como ^(texto)/_(texto). OfficeMath y estilos verticales heredados detectados se rechazan con unsupported_document para evitar convertir una fórmula en otra. No se implementa toda la cascada de estilos Word en esta etapa. TXT admite UTF-8/BOM y párrafos separados por líneas vacías.

El corpus de demostración es sintético. Procesar no equivale a aprobación del tutor ni a verificación de ecuaciones. CAS real sigue pendiente de TI; no cambia la arquitectura de autenticación.
