# TutorIA-Lucero

Plataforma para generar contenidos educativos personalizados a partir de materiales docentes, RAG y perfiles de rendimiento. Proyecto de titulación de Angel Patricio Lucero Loja, vinculado a AdaptIA UPS. Caso principal: Cálculo Diferencial.

Están implementados la base Angular → FastAPI → PostgreSQL/pgvector y el acceso institucional preparado mediante SSO/CAS. El entorno local utiliza usuarios ficticios en modo mock; la conexión real a UPS queda pendiente de los parámetros autorizados por TI. La biblioteca docente permite gestionar documentos PDF/DOCX/TXT propios, extraer su texto, revisar fragmentos con referencias y crear su índice vectorial local. La búsqueda de fuentes RAG está disponible para docentes sobre sus materiales propios; la generación explícita con Gemini ya está conectada sobre la preparación revisada. Consulta el [seguimiento del plan](documentacion/PLAN_DE_TRABAJO.md) antes de iniciar otra etapa.

## Ejecutar en Windows con Docker

La pantalla `/perfiles` permite registrar, listar y consultar observaciones ficticias privadas de rendimiento, sin consumir Gemini. En `/recursos` puedes elegir un perfil propio del mismo tema para ajustar dificultad y apoyo, revisar el motivo y conservar la decisión en el historial. Consulta el [contrato de perfiles](documentacion/api/perfiles.md), la [personalización](documentacion/api/personalizacion.md) y sus evidencias de [hito 8](documentacion/pruebas/hito_08_perfiles.md) y [hito 9](documentacion/pruebas/hito_09_personalizacion.md).

Requisitos: Docker Desktop iniciado con contenedores Linux y Docker Compose. Desde esta carpeta, preparar una sola vez la configuración local:

```powershell
./infraestructura/scripts/initialize-local.ps1
```

Este script crea `.env` con valores aleatorios para desarrollo, sin sobrescribir archivos existentes. No requiere claves de IA. Después, un único comando construye y levanta el entorno, aplica las migraciones y espera a los chequeos de salud:

```powershell
docker compose up -d --build --wait
```

- Interfaz: http://localhost:4200
- API: http://localhost:8000/api/v1/health
- Swagger: http://localhost:8000/api/v1/docs
- OpenAPI: http://localhost:8000/api/v1/openapi.json

Abrir `/login` y pulsar “Iniciar sesión con cuenta UPS”. En `AUTH_MODE=mock` el backend crea una sesión ficticia y muestra el aviso de demostración. La pantalla de inicio debe indicar API, base de datos y motor vectorial disponibles. HTTP 503 significa que la API está viva, pero PostgreSQL o pgvector no están disponibles. PostgreSQL no publica puertos hacia el equipo; API e interfaz se exponen solamente en loopback.

```powershell
docker compose ps
docker compose logs --tail 50 backend migrate
docker compose stop
```

`stop` conserva el volumen de datos. No eliminar volúmenes para resolver un problema de conexión. Cambiar `DB_PASSWORD` después de crear el volumen no cambia automáticamente la contraseña almacenada en PostgreSQL.

## Desarrollo y pruebas

Frontend con Node 24.15 o compatible con Angular 22:

```powershell
cd frontend
npm ci
npm start
npm test -- --watch=false
npm run build
```

`npm start` usa un proxy hacia la API local en el puerto 8000. Si Docker ya ocupa el puerto 4200, usar `npm start -- --port 4201` y ajustar las tres URLs AUTH de backend al mismo origen y puerto antes de reiniciarlo.

Backend local, desde la raíz:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements/dev.txt
cd backend
../.venv/Scripts/python.exe -m pytest
../.venv/Scripts/ruff.exe check .
```

La prueba de integración requiere PostgreSQL y migraciones; se ejecuta en el entorno Docker con `docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --rm test-backend`. Las unitarias no necesitan base de datos. Para ejecutar FastAPI fuera de Docker hay que configurar `backend/.env` con una base PostgreSQL alcanzable y ejecutar `alembic upgrade head` antes de `uvicorn app.main:app --reload --no-access-log`. No se crea una segunda base implícitamente.

## Autenticación institucional

La interfaz no solicita contraseñas. Las rutas son GET `/api/v1/auth/login`, GET `/api/v1/auth/callback`, GET `/api/v1/auth/me` y POST `/api/v1/auth/logout`. FastAPI valida el ticket y aprovisiona al usuario local; el navegador conserva una cookie HttpOnly y SameSite=Lax. No se guardan tokens en localStorage ni contraseñas en PostgreSQL.

La plantilla `.env.example` incluye `AUTH_MODE=mock`, usuario ficticio estudiante y URLs locales. `AUTH_MOCK_USER=teacher` permite ensayar el rol docente con una identidad ficticia. Para CAS se requieren URLs HTTPS, `AUTH_COOKIE_SECURE=true`, parámetros y atributos confirmados por TI. Los endpoints CAS están vacíos deliberadamente; el arranque rechaza una configuración institucional incompleta. `est.ups.edu.ec` está habilitado; `ups.edu.ec` se habilita expresamente mediante `AUTH_ALLOWED_DOMAINS` cuando corresponda.

El modo mock solo funciona en desarrollo y loopback. El callback y la interfaz deben compartir origen. Consulta la [decisión SSO](documentacion/decisiones_tecnicas/0002-sso-ups.md) antes de configurar CAS.

## Biblioteca docente

La ruta `/documentos` permite cargar, listar, consultar detalles y eliminar materiales propios con rol teacher/admin. Para la demostración local, cambiar `AUTH_MOCK_USER=teacher` en `.env`, ejecutar `docker compose up -d --wait` y salir/volver a entrar. La identidad docente es ficticia; el cliente no selecciona permisos. Máximo 10 MiB por archivo, título hasta 160 caracteres. El servidor comprueba extensión, MIME y contenido antes de guardar. Los estudiantes no gestionan documentos.

Los archivos permanecen privados en el volumen `document_data`; PostgreSQL conserva metadatos y SHA-256. Después de cargar, abrir Detalles → Procesar documento para extraer y segmentar. La muestra `datos/ejemplos/derivadas_sinteticas.txt` puede usarse para probar el flujo. Los fragmentos se muestran paginados con referencias; procesado todavía no significa indexado. No se envían documentos a proveedores externos ni se invoca un LLM.

Para preparar el modelo local una sola vez, con internet para descargar sus pesos públicos fijados por revisión/SHA-256:

```powershell
docker compose --profile embeddings run --no-deps --rm prepare-embeddings
```

Después, Detalles → Preparar índice vectorial genera embeddings E5 multilingües de 384 dimensiones en CPU y los guarda en pgvector. Los pesos quedan en el volumen embedding_data, fuera de Git. La inferencia funciona sin internet; la preparación repetida verifica/reutiliza los archivos. Reconstruir índice es una acción explícita que conserva fragmentos/texto y reemplaza vectores de forma atómica. El detalle conserva modelo, revisión y fecha. En Buscar fuentes (`/busqueda`) puedes consultar el corpus propio indexado, limitar top-k y revisar citas con sus referencias. La similitud mide cercanía, no certeza; aún no se genera contenido con un LLM. Consulta el [contrato RAG](documentacion/api/rag.md).

La extracción admite PDF con capa de texto, párrafos DOCX y TXT UTF-8. PDF escaneados requieren OCR, aún pendiente. OfficeMath y ciertos estilos matemáticos heredados se rechazan para evitar alterar fórmulas. El docente debe cotejar la extracción con el original. Límites: 200 páginas PDF, 500 000 caracteres y 1000 fragmentos, además del máximo de carga. Variables: `DOCUMENT_CHUNK_CHARS=1000`, `DOCUMENT_CHUNK_OVERLAP=150`, `EXTRACTION_TIMEOUT_SECONDS=15`; el detalle conserva la configuración usada. Consultar el [contrato de documentos](documentacion/api/documentos.md), la [decisión de extracción](documentacion/decisiones_tecnicas/0004-extraccion-trazable.md) y la [decisión de corpus y estilo UPS](documentacion/decisiones_tecnicas/0003-corpus-y-estilo-ups.md).

## Organización

`backend/` contiene configuración, API versionada, núcleo, repositorios y módulos. `frontend/` contiene núcleo, componentes compartidos y módulos Angular. `infraestructura/` aloja Docker, nginx y scripts. `documentacion/` conserva arquitectura, decisiones, API, plan y evidencia. `datos/` contendrá ejemplos autorizados y perfiles sintéticos. `licencias/` registra dependencias y avisos. `secretos_locales/` está excluido de Git.

Las carpetas de módulos futuros son reservas de estructura, no funcionalidades terminadas. No se publican endpoints vacíos ni respuestas simuladas de IA.

## Proveedores de IA preparados

Gemini es el primer proveedor elegido por el autor. Interfaz LLMProvider, fábrica, adaptador REST y coordinador educativo implementados; OpenAI/Claude pendientes, sin fallback. gemini-3.1-flash-lite comprobado con material sintético. Presupuesto USD 0 y proyecto Free Tier confirmado mediante captura del autor, sin cambios de facturación.

La plantilla mantiene LLM_ENABLED=false y LLM_FREE_TIER_CONFIRMED=false; el entorno local autorizado los tiene en true. Configuración privada exclusivamente en .env, nunca en Angular/Git. La ruta de generación reserva cinco intentos globales/día UTC en PostgreSQL, incluidos fallos, con una petición simultánea y un minuto entre inicios. Sin reintentos automáticos. Este cupo no alcanza scripts manuales u otros clientes de la clave ni verifica facturación en Google. Ver [límites](documentacion/api/limites_gemini.md) y [evidencia API/UI](documentacion/pruebas/hito_07_generacion_ui.md).

## Preparación y generación de recursos educativos

Contratos para explicación, ejercicio, quiz y feedback; prompts versionados y validación estructural/citas. Docentes/admin preparan en /recursos tema, objetivo, tipo y dificultad manual. Quiz admite 1–5 preguntas; feedback requiere respuesta de prueba. Preparar y revisar fuentes guarda la solicitud y recupera hasta tres fragmentos propios sin IA. El botón posterior envía únicamente su identificador a POST /api/v1/content/{id}/generate; backend reserva el intento antes de una llamada y guarda el recurso validado o fallo seguro.

Una preparación se envía una sola vez. La interfaz muestra carga, citas y errores, sin renderizar HTML activo ni guardar contenido en localStorage. Roles/propiedad/CSRF y no-store se conservan. Migraciones 0006/0007 mantienen snapshots y estados prepared/generating/succeeded/failed; consumo/costo desconocidos null. Mis recursos permite reabrir preparaciones, resultados y fuentes tras recargar mediante historial privado paginado, sin consumir Gemini. Adaptación por rendimiento pendiente. La validación de formato/citas no certifica exactitud matemática. Ver [contratos](documentacion/api/contenidos.md), [decisión 0008](documentacion/decisiones_tecnicas/0008-recursos-y-trazabilidad.md) y [continuidad](documentacion/CONTINUIDAD.md). Hito 7 sigue en curso.

## Reglas de trabajo

Carpetas de dominio en español sin tildes; clases, métodos, servicios y endpoints en inglés. Interfaz en español. HTML, SCSS, TS y pruebas en archivos separados. Toda modificación del esquema usa Alembic. Ninguna clave de proveedor llega al navegador.

Ramas: `main`, `develop`, `feature/*`, `fix/*`, `refactor/*`, `docs/*`. Commits descriptivos con prefijos `feat`, `fix`, `docs`, `test`, `refactor`. No fusionar si fallan Docker, contratos o pruebas.

El repositorio se inicia localmente; la publicación en GitHub requiere elegir la cuenta y visibilidad. No hay remoto configurado por defecto.

## Documentación

- [Plan y requisitos](documentacion/PLAN_DE_TRABAJO.md)
- [Navegación superior y experiencia de uso](documentacion/arquitectura/navegacion.md)
- [Arquitectura](documentacion/arquitectura/arquitectura.md)
- [Decisiones iniciales](documentacion/decisiones_tecnicas/0001-base-tecnica.md)
- [Continuidad y próximo paso](documentacion/CONTINUIDAD.md)
- [Autenticación SSO](documentacion/api/autenticacion.md)
- [Evidencia de corpus y estilo](documentacion/pruebas/hito_03.md)
- [Evidencia de extracción y segmentación](documentacion/pruebas/hito_04_extraccion.md)
- [Evidencia de búsqueda RAG](documentacion/pruebas/hito_05.md)
- [Evidencia de embeddings e indexación](documentacion/pruebas/hito_04_indice.md)
- [Evidencia de autenticación](documentacion/pruebas/hito_02.md)
- [Contrato de salud](documentacion/api/health.md)
- [Base de datos](documentacion/base_datos/modelo_inicial.md)
- [Evidencia del primer bloque](documentacion/pruebas/hito_01.md)

La licencia de distribución del código propio queda pendiente de decisión del autor y de las condiciones institucionales. No se ha concedido una licencia abierta automáticamente.
