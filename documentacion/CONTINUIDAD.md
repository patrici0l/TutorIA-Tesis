# Continuidad de TutorIA-Lucero

Actualizado: 6 de octubre de 2026. Este apartado conserva el estado al cerrar cada bloque y antes de una interrupción o reducción de contexto. No se dispone de un porcentaje fiable de tokens restantes; no se inventa uno.

## Instrucciones vigentes

El plan original continúa como base. La actualización directa del autor del 5 de octubre reemplaza la autenticación local y el registro abierto: acceso institucional SSO/CAS UPS con modo mock de usuarios ficticios para desarrollo. Angular no solicita contraseñas ni almacena tokens. CAS real no se conecta hasta recibir parámetros autorizados por TI. Se mantienen Angular, FastAPI, PostgreSQL/pgvector, Alembic y Docker. La instrucción del 6 de octubre incorpora colores relacionados con la UPS; consultar la decisión 0003 para la fuente y paleta aplicada.

## Qué tenemos terminado

- Hito 1: estructura modular, FastAPI, health real, Angular, Docker, Alembic/pgvector y documentación. Arranque conjunto comprobado.
- Hito 2, parte local: cuatro rutas auth, intento ligado al navegador de un solo uso, cookie HttpOnly/SameSite, sesión persistida por hash, expiración y revocación; usuario institucional sin contraseña; alta/actualización automática y conservación del rol local.
- Adaptador CAS: endpoints, parámetros y atributos configurables; validación de ticket en backend, XML seguro, dominios institucionales y HTTPS obligatorio. URLs institucionales vacías hasta confirmación de TI.
- Angular: botón UPS, guard, consulta /auth/me, logout y aviso visible de usuario ficticio. Flujo mock validado en navegador con recarga y rechazo de acceso tras logout.
- Migración 0002 aplicada en PostgreSQL local. Se retiró la implementación provisional de contraseñas antes de ejecutar su migración.
- Hito 3: carga PDF/DOCX/TXT hasta 10 MiB, validación estructural, biblioteca paginada, detalle y eliminación de documentos propios; rol teacher/admin obligatorio y controles de propietario en backend. Migración 0003 aplicada; bytes privados en volumen document_data.
- Estilo: azules digitales UPS, acento amarillo, blanco y fondo claro; navegación, login, dashboard y biblioteca consistentes.
- Entorno Docker funcionando, tres servicios saludables y volúmenes de PostgreSQL/documentos conservados.

## Pruebas y evidencia

Verificación actual: backend local 54 aprobadas y 3 integraciones omitidas; Docker/PostgreSQL 57 aprobadas sin omisiones. Angular 19 aprobadas, compilación correcta. Ruff sin errores. La muestra sintética se cargó desde el navegador y persiste tras recarga y recreación de backend. Consultar pruebas/hito_03.md y capturas hito_03_inicio_ups.png / hito_03_documentos_ups.png. TestClient/HTTPX y add_js de pypdf tienen advertencias de deprecación documentadas.

## Punto exacto de continuación

Hitos 1, 2 mock y 3 cerrados. CAS real sigue pendiente de TI; gestión administrativa global de roles y corpus no implementada. La próxima etapa es hito 4: extracción, normalización y segmentación con referencias; luego embeddings e índices. No se han implementado ingesta, recuperación RAG, proveedores LLM ni generación.

## Próximos pasos

1. Diseñar las referencias de página/párrafo, versión de extractor y estados de procesamiento antes de crear fragmentos_documento. Mantener inmutables las migraciones ya aplicadas.
2. Implementar extracción PDF/DOCX/TXT con límites de recursos y errores por documento, sin ejecutar contenido. Usar primero materiales sintéticos; corpus docente real requiere autorización.
3. Normalizar y segmentar conservando trazabilidad con documento/SHA-256 y referencias; verificar casos vacíos, documentos escaneados y fallos de extracción.
4. Concretar estrategia de embeddings, dimensiones, proveedor/modelo y presupuesto antes de indexar; después validar recuperación sin LLM (hito 5).
5. Pendiente de TI: URLs CAS, callback con state, atributos, dominios y ambiente de pruebas. Pendiente de producción: análisis/aislamiento de documentos, limpieza de archivos huérfanos, retención y autorización de roles. Decisiones 0002 y 0003.

## Git y cómo retomar

Repositorio C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero. Rama feature/document-upload, basada en 82fabe6 (autenticación); c7db36d sigue en main/develop. El cierre del corpus y estilo se guarda en commit descriptivo; consultar git log -1 para su identificador. Sin remoto GitHub.

Leer AGENTS.md, este archivo, PLAN_DE_TRABAJO.md y la decisión 0002. Revisar git status antes de editar y preservar cambios existentes. Ejecutar docker compose up -d --build --wait desde la raíz con el .env local, sin imprimir secretos ni eliminar volúmenes. Interfaz http://localhost:4200/login; las pruebas de PostgreSQL se ejecutan con el compose de pruebas documentado. No repetir verificaciones terminadas si no hay cambios que lo requieran.

## Estado local al cerrar

Se deja una muestra derivadas_sinteticas.txt en la biblioteca del docente ficticio y el navegador abierto en /documentos. Para verificar la carga se seleccionó temporalmente AUTH_MOCK_USER=teacher mediante variable de proceso; después se restauró backend a la configuración .env original (student). La sesión docente ya iniciada continúa válida hasta logout/expiración. Un nuevo acceso usa la identidad configurada en .env; para demostrar documentos después de salir, configurar teacher y recrear backend. No se usaron credenciales UPS.
