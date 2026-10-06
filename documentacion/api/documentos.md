# API de documentos propios

Prefijo /api/v1. Requiere sesión válida, cuenta activa y rol teacher/admin. Escrituras requieren X-TutorIA-Client: web. La identidad y propietario provienen exclusivamente de la sesión; no se acepta owner_id del navegador.

| Método y ruta | Entrada | Respuesta |
|---|---|---|
| POST /documents/upload | multipart: file, title (1–160 caracteres) | 201 con metadatos |
| GET /documents | limit (1–100, defecto 20), offset (>=0) | 200: items, total, limit, offset |
| GET /documents/{id} | UUID propio | 200 con metadatos |
| DELETE /documents/{id} | UUID propio | 204, retirado de biblioteca y borrado físico |

Metadatos: id, filename, title, mime_type, size_bytes, sha256, status, created_at. No devuelve bytes ni rutas físicas. status=uploaded identifica material guardado, pendiente de procesamiento.

Errores: 401 sesión ausente/inválida; 403 rol insuficiente o cabecera de protección ausente; 404 identificador inexistente, ajeno o eliminado; 413 tamaño excedido; 415 extensión/MIME incompatible; 422 campos inválidos, archivo vacío/cifrado/corrupto o contenido activo no admitido; 500 fallo interno con mensaje genérico.

PDF application/pdf; DOCX application/vnd.openxmlformats-officedocument.wordprocessingml.document; TXT text/plain, UTF-8. Máximo 10 MiB (10 485 760 bytes), configurable hacia abajo mediante DOCUMENT_MAX_BYTES. No se aceptan URLs remotas ni se ejecuta el contenido. No subir corpus real hasta disponer de autorización de uso.

## Desarrollo local

AUTH_MOCK_USER=teacher permite iniciar una nueva sesión con docente.demo@example.org. Cambiar esa variable requiere recrear backend; salir y volver a entrar para seleccionar la identidad ficticia correspondiente. El cliente no puede elegir roles. La muestra datos/ejemplos/derivadas_sinteticas.txt es material creado para pruebas, sin datos personales.
