# API de documentos propios

Prefijo /api/v1. Requiere sesión válida, cuenta activa y rol teacher/admin. Escrituras requieren X-TutorIA-Client: web. La identidad y propietario provienen exclusivamente de la sesión; no se acepta owner_id del navegador.

| Método y ruta | Entrada | Respuesta |
|---|---|---|
| POST /documents/upload | multipart: file, title (1–160 caracteres) | 201 con metadatos |
| GET /documents | limit (1–100, defecto 20), offset (>=0) | 200: items, total, limit, offset |
| GET /documents/{id} | UUID propio | 200 con metadatos |
| DELETE /documents/{id} | UUID propio | 204, retirado de biblioteca y borrado físico |
| POST /documents/{id}/process | Sin body; UUID propio | 200 con estado y configuración de extracción |
| GET /documents/{id}/chunks | limit (1–50, defecto 10), offset (>=0) | 200: items, total, limit, offset |

Metadatos: id, filename, title, mime_type, size_bytes, sha256, status, created_at. No devuelve bytes ni rutas físicas. status=uploaded identifica material guardado; su extracción usa un estado independiente: processing_status=pending/processing/processed/failed. También devuelve processing_error (código seguro o null), processing_started_at, processed_at, processing_version, chunk_chars, chunk_overlap, chunk_count y text_chars. El token interno de procesamiento no se expone. Las respuestas de documentos llevan Cache-Control: no-store.

Cada fragmento devuelve id, position (desde 0), source_kind (page/paragraph), source_index (desde 1), char_start, char_end y text. Los offsets [inicio, fin) cuentan puntos de código Unicode dentro de la unidad normalizada; no son posiciones en el archivo binario ni tokens del modelo. PDF usa páginas; DOCX usa párrafos XML, incluidos los de tablas; TXT usa párrafos separados por líneas vacías. No se unen distintas unidades de origen.

El procesamiento es síncrono, acotado e idempotente: un documento processed conserva sus fragmentos, IDs y configuración aunque se repita POST. Un intento en curso responde 409; puede recuperarse tras dos minutos si quedó interrumpido. La interfaz permite actualizar su detalle y reintentar. No se aceptan parámetros de segmentación ni rutas desde Angular. Los documentos failed admiten reintento. Cambiar las variables de segmentación solo afecta documentos aún sin procesar; la reconstrucción explícita de corpus se diseñará con el índice vectorial.

422 en extracción conserva processing_status=failed y un código entre empty_text, unsupported_document, invalid_document, extraction_limit, file_missing, file_unavailable, file_changed, extraction_timeout y extraction_failed. Un fallo de persistencia devuelve 500 seguro y no publica fragmentos parciales. Capacidad ocupada devuelve 429 sin reclamar el documento. Al eliminarlo se invalidan los intentos y se borran sus fragmentos dentro de la misma transacción, antes de retirar el archivo.

processed significa texto extraído y segmentado, no indexación vectorial ni aprobación académica. No hay OCR, embeddings, búsqueda semántica o llamadas a LLM en este bloque. Consultar decisión 0004 y evidencia hito_04_extraccion.md.

Errores: 401 sesión ausente/inválida; 403 rol insuficiente o cabecera de protección ausente; 404 identificador inexistente, ajeno o eliminado; 413 tamaño excedido; 415 extensión/MIME incompatible; 422 campos inválidos, archivo vacío/cifrado/corrupto o contenido activo no admitido; 500 fallo interno con mensaje genérico.

PDF application/pdf; DOCX application/vnd.openxmlformats-officedocument.wordprocessingml.document; TXT text/plain, UTF-8. Máximo 10 MiB (10 485 760 bytes), configurable hacia abajo mediante DOCUMENT_MAX_BYTES. No se aceptan URLs remotas ni se ejecuta el contenido. No subir corpus real hasta disponer de autorización de uso.

## Desarrollo local

AUTH_MOCK_USER=teacher permite iniciar una nueva sesión con docente.demo@example.org. Cambiar esa variable requiere recrear backend; salir y volver a entrar para seleccionar la identidad ficticia correspondiente. El cliente no puede elegir roles. La muestra datos/ejemplos/derivadas_sinteticas.txt es material creado para pruebas, sin datos personales.
