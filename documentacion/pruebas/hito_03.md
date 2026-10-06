# Evidencia del hito 3 y estilo UPS

Fecha: 6 de octubre de 2026, America/Guayaquil.

| Verificación | Resultado real |
|---|---|
| pytest local | 54 aprobadas; 3 integraciones omitidas sin RUN_DB_TESTS |
| pytest Docker/PostgreSQL | 57 aprobadas; ninguna omitida |
| Ruff check / format | Sin errores |
| Angular unitarias | 19 aprobadas, 7 archivos |
| Angular producción | Compilación correcta; bundle inicial local 283.64 kB |
| Docker | 3 servicios saludables; migración 0003 aplicada |
| Navegador | Docente mock carga TXT sintético; biblioteca y detalle muestran metadatos reales |
| Persistencia | Documento visible tras recarga y recreación de backend; volumen privado conservado |
| Diseño | Azul/amarillo aplicado a inicio, login y biblioteca; captura desktop del estado real |

Los casos nuevos cubren PDF y DOCX válidos, falsificación de formato/MIME, cifrado, scripts PDF, TXT binario/vacío, nombre con ruta, macros DOCX, referencias externas, expansión ZIP, tamaño del archivo y multipart (incluido flujo sin Content-Length), paginación, título inválido, rol estudiante, acceso anónimo, documentos ajenos, CSRF, eliminación y limpieza si falla el commit. La integración PostgreSQL comprueba el ciclo de guardado/lista/detalle/eliminación con transacción externa que se revierte. Angular comprueba rol estudiante sin consultar el corpus, carga multipart/detalle, recuperación tras error y selección previa al borrado.

## Reproducir

```powershell
docker compose up -d --build --wait
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --build --rm test-backend
```

En frontend ejecutar `npm test -- --watch=false`. AUTH_MOCK_USER=teacher selecciona una cuenta ficticia al iniciar una nueva sesión; necesita recrear backend. Abrir /documentos y cargar datos/ejemplos/derivadas_sinteticas.txt. Se dejó esa muestra en la biblioteca local. No se realizaron cargas institucionales reales.

Capturas: hito_03_inicio_ups.png y hito_03_documentos_ups.png. La eliminación física se comprobó mediante pruebas automatizadas con archivos temporales; no se borró la muestra desde el navegador. La prueba de sesión docente utilizó una variable de proceso temporal; la configuración original de backend fue restaurada.

## Alcance

Se cierra gestión de documentos propios; el estado uploaded no significa indexado. No hay extracción ni embeddings todavía. CAS real, corpus autorizado, administración global y despliegue institucional siguen pendientes. Las comprobaciones no son un antivirus; las restricciones actuales de contenido se documentan en decisión 0003.

Advertencias observadas: Starlette/TestClient sobre HTTPX y pypdf add_js (utilizado solo para construir un PDF malicioso de prueba). Ninguna impide los resultados; atenderlas al actualizar el entorno.
