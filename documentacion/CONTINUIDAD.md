# Continuidad de TutorIA-Lucero

Actualizado: 6 de octubre de 2026. Este apartado conserva el estado al cerrar cada bloque y antes de una interrupción o reducción de contexto. No se dispone de un porcentaje fiable de tokens restantes; no se inventa uno.

## Instrucciones vigentes

El plan original continúa como base. La actualización directa del autor reemplaza autenticación local/Google y registro abierto por SSO/CAS UPS, modos mock/cas y cookie HttpOnly/SameSite. Angular no solicita contraseñas ni almacena tokens. CAS real no se conecta hasta recibir parámetros autorizados por TI. Se mantienen Angular, FastAPI, PostgreSQL/pgvector, Alembic y Docker. Colores relacionados con UPS y navegación superior interactiva/responsiva, con movimiento reducido. Consultar decisiones 0002, 0003 y arquitectura/navegacion.md.

## Qué tenemos terminado

- Hito 1: estructura modular, FastAPI, health real, Angular, Docker, Alembic y pgvector; arranque conjunto comprobado.
- Hito 2 local: cuatro rutas auth, estado ligado al navegador de un solo uso, sesión opaca persistida por hash, expiración/revocación, alta/actualización automática y conservación del rol. Usuario institucional sin contraseña. Adaptador CAS preparado, URLs vacías hasta TI.
- Hito 3: carga PDF/DOCX/TXT hasta 10 MiB, validación estructural, biblioteca paginada, detalle y eliminación de documentos propios; teacher/admin y propietario comprobados. Bytes privados en volumen document_data.
- Navegación: cabecera superior, pestañas con scroll, desplegable Explorar animado, foco/Escape, roles, responsive y movimiento reducido; paleta azul/amarillo/blanco UPS.
- Hito 4, primera parte: extracción/normalización/segmentación real en worker separado, referencias de página/párrafo, offsets Unicode y SHA-256 de unidad. Estados, versión y configuración persistidos. Fragmentos paginados en Angular; fallos persistentes, reintentos y recuperación tras interrupción. Operación idempotente; intentos tardíos no pisan resultados ni restauran documentos eliminados.
- Migraciones 0001–0004 aplicadas en PostgreSQL local. No se modificaron las anteriores. No hay columnas de contraseña ni llamadas institucionales reales.

## Pruebas y evidencia

Verificación final de este bloque: Docker/PostgreSQL 105 aprobadas sin omisiones; Angular 32 aprobadas en 9 archivos; compilación de producción 299,59 kB iniciales, sin advertencias de presupuesto. Ruff check/format check limpios. Las advertencias de Starlette TestClient/HTTPX y pypdf add_js de prueba siguen documentadas.

Pruebas cubren extracción, límites, offsets/solapamiento, integridad de archivo, errores seguros, propiedad, CSRF, idempotencia, rollback y recuperación. PostgreSQL incluye sesiones independientes para reclamación concurrente y carrera publicación/eliminación. La muestra sintética se procesó desde el navegador y conservó su fragmento después de recrear servicios/recargar. Capturas hito_04_fragmentos_desktop.png y hito_04_fragmentos_mobile.png; tamaño normal restaurado después de 390×844. Detalles en pruebas/hito_04_extraccion.md y decisión 0004.

## Punto exacto de continuación

Hitos 1, 2 mock y 3 cerrados. Hito 4 en curso: extracción/segmentación terminadas; embeddings e índices pendientes. Todavía no hay búsqueda semántica, proveedores LLM ni generación. El indicador de motor vectorial del inicio comprueba pgvector, no un corpus indexado.

PDF escaneados necesitan OCR, aún no implementado. PDF con fórmulas dibujadas/columnas requiere cotejo; DOCX OfficeMath y ciertos estilos verticales heredados se rechazan para evitar alterar fórmulas. No se afirma validación académica ni autorización de corpus real.

## Próximos pasos

1. Concretar embeddings multilingües y dimensionamiento. Se planteó al autor modelo local recomendado frente a API externa; todavía no hay una respuesta registrada ni un modelo instalado/seleccionado definitivamente. Investigar modelo local CPU con licencia/revisión/pesos trazables y sin enviar corpus fuera del equipo.
2. Controlar tokenizer y longitud antes de vectorizar: los fragmentos actuales usan caracteres, no tokens. Diseñar nueva migración para vectores, versión/modelo/dimensión e índices; conservar migración 0004 inmutable.
3. Implementar indexación idempotente/reconstrucción explícita, errores y retirada de vectores al eliminar material. Validar con corpus sintético y persistencia pgvector para cerrar hito 4.
4. Hito 5: recuperación top-k y consultas de referencia, fuentes y permisos; probar sin LLM antes de hito 6.
5. Pendientes externos: TI (URLs CAS, callback, atributos, dominios y pruebas), corpus autorizado/rúbrica, administración global de roles, licencia y cuenta/visibilidad GitHub. Producción requiere cola/coordinación de workers, aislamiento completo de documentos, retención y limpieza de archivos huérfanos.

## Git y cómo retomar

Repositorio C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero. Rama feature/document-ingestion, basada en 019c56b (navegación), precedido por 31270c6 (corpus/UPS), 82fabe6 (autenticación) y c7db36d (base en main/develop). El bloque se guarda en commit descriptivo; consultar git log -1 para su identificador. Sin remoto GitHub.

Leer AGENTS.md, este archivo, PLAN_DE_TRABAJO.md y decisiones 0002/0004. Revisar git status antes de editar y preservar cambios existentes. Ejecutar docker compose up -d --build --wait desde raíz sin imprimir secretos ni eliminar volúmenes. No repetir verificaciones ya cerradas sin cambios que lo justifiquen.

## Estado local al cerrar

Docker deja backend, frontend y postgres saludables. Navegador abierto en /documentos con detalle del docente ficticio y un fragmento del ejemplo derivadas_sinteticas.txt. Para demostrar se usó AUTH_MOCK_USER=teacher temporalmente; se restauró backend a la configuración original del .env (student), sin modificar el archivo ni exponer secretos. La sesión docente ya iniciada permanece válida hasta logout/expiración; un acceso nuevo usa el selector del .env. No se borró la muestra ni se usaron credenciales UPS.
