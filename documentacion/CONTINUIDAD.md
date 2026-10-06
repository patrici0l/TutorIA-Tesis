# Continuidad de TutorIA-Lucero

Actualizado: 6 de octubre de 2026. Este apartado conserva el estado al cerrar cada bloque y antes de una interrupción o reducción de contexto. No se dispone de un porcentaje fiable de tokens restantes; no se inventa uno.

## Instrucciones vigentes

El plan original continúa como base. La actualización directa del autor del 5 de octubre reemplaza la autenticación local y el registro abierto: acceso institucional SSO/CAS UPS con modo mock de usuarios ficticios para desarrollo. Angular no solicita contraseñas ni almacena tokens. CAS real no se conecta hasta recibir parámetros autorizados por TI. Se mantienen Angular, FastAPI, PostgreSQL/pgvector, Alembic y Docker.

## Qué tenemos terminado

- Hito 1: estructura modular, FastAPI, health real, Angular, Docker, Alembic/pgvector y documentación. Arranque conjunto comprobado.
- Hito 2, parte local: cuatro rutas auth, intento ligado al navegador de un solo uso, cookie HttpOnly/SameSite, sesión persistida por hash, expiración y revocación; usuario institucional sin contraseña; alta/actualización automática y conservación del rol local.
- Adaptador CAS: endpoints, parámetros y atributos configurables; validación de ticket en backend, XML seguro, dominios institucionales y HTTPS obligatorio. URLs institucionales vacías hasta confirmación de TI.
- Angular: botón UPS, guard, consulta /auth/me, logout y aviso visible de usuario ficticio. Flujo mock validado en navegador con recarga y rechazo de acceso tras logout.
- Migración 0002 aplicada en PostgreSQL local. Se retiró la implementación provisional de contraseñas antes de ejecutar su migración.
- Entorno Docker funcionando, tres servicios saludables y volumen de PostgreSQL conservado.

## Pruebas y evidencia

Backend local: 35 aprobadas y 2 integraciones omitidas; Docker/PostgreSQL: 37 aprobadas sin omisiones. Angular: 15 aprobadas; compilación de producción correcta (253.33 kB iniciales). Ruff y revisión de whitespace correctos. Consultar pruebas/hito_02.md y las capturas hito_02_login.png / hito_02_dashboard.png. Hay una advertencia de deprecación de TestClient documentada.

## Punto exacto de continuación

Hito 2 mock cerrado; integración real UPS pendiente exclusivamente de parámetros y pruebas autorizadas por TI. La administración de permisos todavía debe implementarse según la política que se concrete. La siguiente implementación es hito 3: documentos docentes PDF/DOCX/TXT, validación de extensión/MIME/tamaño, propiedad y permisos, almacenamiento y gestión. No se han implementado ingesta, embeddings, recuperación RAG, proveedores LLM ni generación.

## Próximos pasos

1. Leer el alcance del corpus en la fuente; concretar permisos de carga docente y gestión administrativa con el rol local actual.
2. Diseñar migración de documentos, almacenamiento fuera de archivos públicos y contratos upload/list/detail/delete; rechazar cargas inválidas y acceso ajeno.
3. Implementar y verificar un flujo completo de gestión de documentos con muestras sintéticas autorizadas. No ejecutar contenido cargado.
4. Mantener pendiente de TI: URLs CAS, callback con state autorizado, atributos, dominios y ambiente de pruebas; lista en decisiones_tecnicas/0002-sso-ups.md.
5. Después: extracción/segmentación/embeddings (hito 4), recuperación validada sin LLM (5), proveedor IA (6) y recursos educativos (7).

## Git y cómo retomar

Repositorio C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero. Rama feature/authentication; base c7db36d en main/develop. El cierre se guarda en commit descriptivo de autenticación UPS; consultar git log -1 para su identificador. Sin remoto GitHub.

Leer AGENTS.md, este archivo, PLAN_DE_TRABAJO.md y la decisión 0002. Revisar git status antes de editar y preservar cambios existentes. Ejecutar docker compose up -d --build --wait desde la raíz con el .env local, sin imprimir secretos ni eliminar volúmenes. Interfaz http://localhost:4200/login; las pruebas de PostgreSQL se ejecutan con el compose de pruebas documentado. No repetir verificaciones terminadas si no hay cambios que lo requieran.
