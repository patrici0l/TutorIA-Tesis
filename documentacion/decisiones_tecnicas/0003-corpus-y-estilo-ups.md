# Decisión 0003: corpus privado y estilo UPS

Fecha: 6 de octubre de 2026. Instrucción directa del autor: continuar e incorporar colores relacionados con la UPS. Se consultó el [manual de identidad institucional](https://www.ups.edu.ec/documents/20121/257878/Manual%2Bde%2BIdentidad%2BCorporativa%2B-%2BUniversidad%2BPolit%C3%A9cnica%2BSalesiana.pdf), sección 5 (página 20 del PDF): azules digitales #0065B0 y #07508E, fondo #F3F7FB y primarios Pantone 281/130. TutorIA usa los azules digitales, blanco, un azul oscuro de interfaz #002D62 y acento amarillo #F5B51B. Los dos últimos son elecciones de interfaz, no equivalencias certificadas de Pantone. Se conserva la marca propia TutorIA; no se recrea el isologo institucional.

## Gestión del corpus

En esta etapa teacher y admin gestionan exclusivamente documentos propios. Student recibe 403 en los endpoints y una explicación en la interfaz. Ningún rol obtiene acceso a archivos ajenos. El administrador no tiene todavía gestión global de corpus ni interfaz de permisos. Esto reduce el alcance al criterio del hito 3: cargar, listar, consultar y eliminar documentos propios. La difusión a estudiantes se diseñará al implementar recuperación y cursos.

Carga multipart: archivo y título de hasta 160 caracteres. Límite inicial 10 MiB configurable hacia abajo; cuerpo multipart hasta 11 MiB en FastAPI y nginx. PDF/DOCX/TXT deben concordar con MIME y contenido; los nombres no permiten rutas ni controles. TXT debe ser UTF-8 no vacío. PDF debe ser estructuralmente válido, no cifrado y sin acciones automáticas, scripts o adjuntos detectados. DOCX debe tener los componentes OOXML esperados: se rechazan XML con entidades, referencias externas, macros, objetos incrustados y ZIP con rutas o expansión excesiva. Estas comprobaciones no equivalen a un antivirus; en producción se deberá evaluar un servicio de análisis y aislamiento del procesamiento.

Los bytes se almacenan fuera del directorio público bajo un UUID generado por el servidor, en un volumen Docker privado document_data. PostgreSQL conserva dueño, título, nombre, MIME, tamaño, SHA-256, fecha y estado uploaded. No se descarga ni previsualiza contenido en esta etapa; GET detalle devuelve metadatos. El hash permite trazar el corpus futuro. La ruta física nunca se expone.

La eliminación marca estado deleted y fecha, oculta el documento y elimina sus bytes. Si el borrado físico falla, se registra un aviso sin datos sensibles y queda pendiente de limpieza operativa. La retención o purga definitiva de metadatos se decidirá antes del despliegue. El guardado limpia archivos si falla el commit. BD y archivos usan recursos distintos: un corte del proceso entre operaciones puede dejar un archivo huérfano; prever reconciliación operativa antes de producción. No se elimina el volumen al reiniciar.

## Continuación

La migración 0003 crea documentos. No se modifican las migraciones aplicadas de autenticación. Estado uploaded significa almacenado y validado, todavía sin extracción, chunks ni embeddings. El hito 4 añadirá extracción, normalización y segmentación con referencias; el hito 5 validará recuperación sin LLM.
