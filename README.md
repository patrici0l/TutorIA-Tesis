# Generación de contenidos educativos

Avance local de [v0.3: ejemplos, pistas y fuentes externas](versionesDM/Version-0.3.md).
La conexión con Wikipedia se abre desde **Documentos → Buscar fuentes externas**;
requiere la migración `0018_external_sources` y reconstruir la aplicación local.
El estudiante ya puede **Solicitar contenido**. Requiere la migración
`0019_student_content`. El profesor habilita primero la asignatura en
**Explorar → Acceso de estudiantes**, indicando el correo de una cuenta que ya haya
iniciado sesión. Se comparten únicamente los materiales habilitados de ese profesor
y esa materia, incluidos los que habilite después; no se publican documentos por dar acceso.

El estudiante elige asignatura y profesor, tipo de ayuda, tema y objetivo. **Buscar apoyo
en mis materiales** guarda una preparación con fuentes sin llamar al LLM. **Generar
contenido** realiza el envío explícito si está habilitado y hay cupo. **Mis solicitudes**
permite reabrir preparaciones y resultados. Para feedback debe escribir su respuesta;
para una pista debe incluir el enunciado. Los ejercicios y cuestionarios solicitados
son de autoestudio y permiten consultar soluciones, no son exámenes con claves ocultas.

Retirar el acceso bloquea nuevas preparaciones y el envío de las pendientes; conserva
el historial anterior. Retirar un documento también invalida preparaciones que lo usan.
Los permisos se verifican en servidor, no solo en la pantalla. El cupo de IA sigue
siendo compartido. No hay adaptación automática al perfil del estudiante ni matrícula
institucional: esas integraciones siguen pendientes.

En modo demo las cuentas se comparten por rol. El correo del estudiante se muestra en
**Solicitar contenido** (por defecto `estudiante.demo@example.org`); su historial también
es compartido entre quienes usen ese rol. Login institucional y despliegue continúan
pendientes con el tutor.

 Generación, consulta y trazabilidad de recursos mediante IA y RAG.

## Componentes

| Área | Tecnología | Responsabilidad |
|---|---|---|
| Interfaz | Angular, TypeScript, SCSS y KaTeX | Materiales, solicitudes, resultados e historial. |
| API | FastAPI y Pydantic | Contratos, autorización y coordinación de servicios. |
| Persistencia | PostgreSQL, pgvector, SQLAlchemy y Alembic | Metadatos, vectores, trazas y migraciones. |
| Recuperación | E5 multilingüe y ONNX Runtime | Embeddings y búsqueda local. |
| Generación | Adaptadores HTTP de proveedores | Modelo seleccionado, límites y errores. |
| Operación | Docker Compose y nginx | Entorno reproducible y proxy. |

## Ejecución

```powershell
./infraestructura/scripts/initialize-local.ps1
docker compose --env-file licencias/secure_data.env build
docker compose --env-file licencias/secure_data.env --profile embeddings run --rm --no-deps prepare-embeddings
docker compose --env-file licencias/secure_data.env up -d --build --wait
```

Interfaz: http://localhost:4200. API: http://localhost:8000/api/v1/docs.
Configuración Docker y claves: `licencias/secure_data.env`. Ejecución directa del backend: `licencias/backend.env`. Ambos archivos son privados y están excluidos de Git y Docker. Las dos configuraciones se conservan para no sobrescribir ajustes locales distintos.

Docker Desktop debe estar iniciado y usar contenedores Linux. La preparación de embeddings
verifica los artefactos existentes y descarga únicamente los que falten o no sean válidos.
Los datos se conservan en los volúmenes de Compose; no uses `down -v` para actualizar.
Comprueba el arranque con `docker compose --env-file licencias/secure_data.env ps` y `./infraestructura/scripts/check-health.ps1`.

## Iniciar sin Docker (Windows)

En este equipo ya están preparados Python, las dependencias, el modelo y PostgreSQL
18 con pgvector. La base nativa `tutoria_localdev` usa el puerto 5432 y está migrada
a `0019_student_content`. Es independiente de la base de Docker: los documentos y
recursos de un entorno no aparecen automáticamente en el otro.

Abre PowerShell en `C:\C_PROJECTS\TESIS COMPUTACION\TutorIA-Lucero`.
Si Docker está ejecutando el proyecto, detén sus contenedores para liberar los puertos
(esto conserva los datos):

```powershell
docker compose --env-file licencias/secure_data.env stop
```

PostgreSQL de Windows debe estar activo. Compruébalo con
`Get-Service postgresql-x64-18`; si está detenido, inicia ese servicio desde Servicios
de Windows o con `Start-Service postgresql-x64-18` en PowerShell como administrador.
Después inicia el servidor en una terminal:

```powershell
./infraestructura/scripts/start-backend-local.ps1
```

Y la interfaz en otra terminal, desde la misma carpeta:

```powershell
./infraestructura/scripts/start-frontend-local.ps1
```

Abre http://localhost:4200. Mantén ambas terminales abiertas y usa `Ctrl+C` en cada
una para detenerlas. La API está en http://localhost:8000/api/v1/docs.
Puedes comprobar la conexión con `./infraestructura/scripts/check-health.ps1`.
Estos dos scripts no usan Docker ni cambian la configuración privada.

### Preparación y actualizaciones del entorno nativo

Solo si faltan las dependencias, crea `.venv` con `py -3.12 -m venv .venv` y ejecuta:

```powershell
./.venv/Scripts/python.exe -m pip install -e './backend[dev]'
Push-Location frontend
npm ci
Pop-Location
```

En otro equipo también necesitas PostgreSQL con pgvector y una base propia. Copia
`.env.example` a `licencias/backend.env` **solo si ese archivo no existe** y configura
`DB_HOST=localhost`, `DB_PORT=5432`, el nombre de base, usuario y contraseña.
Si `DATABASE_URL` tiene un valor, este prevalece sobre los campos `DB_*`.
No copies los valores de conexión internos de Docker. Conserva las rutas locales
de documentos y del modelo; no uses las rutas `/app/...` del contenedor.

Cuando existan nuevas migraciones, respalda primero la base nativa y, con el servidor
detenido, ejecuta desde la raíz:

```powershell
Push-Location backend
../.venv/Scripts/python.exe -m alembic upgrade head
../.venv/Scripts/python.exe -m app.modulos.rag.servicios.prepare_model
Pop-Location
```

La preparación del modelo verifica los archivos y descarga los que falten. Internet
también se necesita para Wikipedia y para el proveedor de IA que hayas configurado.
El login sigue siendo el de demostración; el login institucional y el despliegue
se revisarán con el tutor.

Para volver a Docker, detén las dos terminales y ejecuta:

```powershell
docker compose --env-file licencias/secure_data.env up -d --build --wait
```

## Prueba remota con el tutor

Desde PowerShell, con Docker Desktop iniciado y el modelo de embeddings preparado:

```powershell
./infraestructura/scripts/start-remote-demo.ps1
```

El script reconstruye la aplicación, verifica el modelo y publica la interfaz y la API
mediante un túnel HTTPS. Comprueba el acceso público antes de mostrar el enlace y lo
guarda en `infraestructura/herramientas/demo-remota/enlace.txt`. El tutor puede abrirlo
y elegir **Profesor**; también puede probar **Estudiante**. Son perfiles de demostración
compartidos por rol, sin contraseña: cualquier persona con el enlace puede acceder a
sus datos. Comparte únicamente para la revisión y usa materiales destinados a la demo.

Se necesita el ejecutable oficial Windows x64 de cloudflared en
`infraestructura/herramientas/cloudflared.exe` ([descargas oficiales](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/)).
Las claves permanecen en el backend y la configuración local se conserva. La generación
de IA mantiene el proveedor y los límites definidos en `licencias/secure_data.env`.

El equipo, Docker e Internet deben permanecer activos y Windows no debe suspenderse.
Cloudflare proporciona un [enlace temporal](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)
que cambia al iniciar otro túnel; el proyecto sigue ejecutándose en este equipo.
Para finalizar la revisión y recuperar el acceso local:

```powershell
./infraestructura/scripts/stop-remote-demo.ps1
```

No ejecutar `docker compose up` con solo la configuración base durante la demo:
restauraría las redirecciones de autenticación a localhost. Para volver a construir y
publicar cambios, cerrar la demo e iniciarla de nuevo; compartir el nuevo enlace.

### Swagger y reglas de adaptación

La documentación interactiva está en `/api/v1/docs` y el contrato JSON en
`/api/v1/openapi.json`. Para probar operaciones protegidas, abrir `/login` en otra
pestaña del mismo navegador e iniciar sesión como Profesor; Swagger utiliza esa cookie.
Las escrituras protegidas requieren además `x-prototipo-client: web`.

`GET /api/v1/adaptation/rules` consulta la política local vigente sin generar contenido
ni consumir cuota. Requiere docente o administrador. Admite `version` (actualmente
`profile-adaptation-v2`) y `mastery_level` (`low`, `medium`, `high`). Sin filtros devuelve
las tres reglas con dificultad, orientación, tipos sugeridos y motivo. Una versión no
disponible devuelve 404; un filtro inválido, 422. El dominio lo informa el docente:
este catálogo no calcula el perfil ni sustituye el contrato del motor de ADAPTIA.

## Compatibilidad

Se conservan identificadores existentes de base de datos, proyecto Compose y respaldos para mantener acceso a los datos. No representan el nombre del producto. Las cookies y la cabecera del cliente usan el identificador neutro `prototipo`; las sesiones anteriores requieren iniciar sesión otra vez.

## Validación

Backend: pytest y Ruff. Frontend: `npm test -- --watch=false` y `npm run build`.
Sin commits automáticos. Las evidencias de pruebas anteriores se conservan como registros históricos.

La [revisión de UI/UX del 19 de noviembre de 2026](docs/qa/ui-ux-2026-11-19/informe-ui-ux.md)
explica los 10 hallazgos corregidos, su valor agregado y sus comprobaciones funcionales.
El [PDF adjunto](docs/qa/ui-ux-2026-11-19/informe-ui-ux-2026-11-19.pdf) contiene las
12 comparativas antes/después con las capturas incrustadas.

## Respaldo y recuperación

Los volúmenes postgres_data, document_data y embedding_data conservan base de datos, documentos y modelo. No cambiar sus identificadores ni borrarlos para reparar el arranque.

Antes de respaldar, esperar que terminen las operaciones y detener frontend/backend. Con PostgreSQL activo, ejecutar `./infraestructura/scripts/backup-local.ps1`; después reiniciar backend/frontend con el comando Compose anterior. Los respaldos completos están en documentacion-local/respaldos y contienen dump, documentos y manifiesto. La configuración privada se conserva por separado.

Comprobar una copia con `./infraestructura/scripts/verify-local-backup.ps1 -BackupDirectory <ruta>`: usa un contenedor temporal y no sustituye la base activa. Conservar el informe de verificación junto a la copia. Una copia en el mismo disco no cubre su pérdida.

## Desarrollo

Frontend: [instrucciones](frontend/README.md). Para backend directo, ejecutar desde backend con sus dependencias instaladas; carga licencias/backend.env mediante una ruta independiente del directorio actual. Docker recibe la configuración de licencias/secure_data.env. La única plantilla es `.env.example`, sin claves reales. Para backend directo, copiarla a `licencias/backend.env`, cambiar `DB_HOST=localhost` y configurar una base accesible desde el equipo: PostgreSQL de Compose está disponible en `127.0.0.1:5433` (`DB_PORT=5433` para el backend directo). No sobrescribir archivos privados existentes.


## Versión 0.2

La búsqueda y preparación de recursos requieren asignatura y materiales habilitados. Después de procesar, indexar y revisar una versión, usar **Habilitar como fuente** en sus detalles. **Retirar de recursos** conserva el original y evita nuevas recuperaciones; las preparaciones pendientes con esa fuente deben rehacerse. Los materiales anteriores a esta actualización necesitan habilitación explícita.

Claude utiliza el adaptador existente y requiere modelo, clave y confirmación de presupuesto mediante `LLM_PAID_USAGE_CONFIRMED=true`, además de `LLM_ENABLED=true` y `LLM_DEFAULT_PROVIDER=claude`. La plantilla mantiene los envíos deshabilitados. No se asigna un costo cero a Claude.

Alcance, API, pruebas, archivos nuevos y pendientes de aceptación: [versión 0.2](versionesDM/Version-0.2.md).
