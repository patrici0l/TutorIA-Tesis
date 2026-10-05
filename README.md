# TutorIA-Lucero

Plataforma para generar contenidos educativos personalizados a partir de materiales docentes, RAG y perfiles de rendimiento. Proyecto de titulación de Angel Patricio Lucero Loja, vinculado a AdaptIA UPS. Caso principal: Cálculo Diferencial.

El primer bloque implementa Angular → FastAPI → PostgreSQL/pgvector. Los módulos de autenticación, documentos, RAG y generación se desarrollarán en ese orden. Consulta el [seguimiento del plan](documentacion/PLAN_DE_TRABAJO.md) antes de iniciar otra etapa.

## Ejecutar en Windows con Docker

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

La pantalla de inicio debe indicar API, base de datos y motor vectorial disponibles. HTTP 503 significa que la API está viva, pero PostgreSQL o pgvector no están disponibles. PostgreSQL no publica puertos hacia el equipo; API e interfaz se exponen solamente en loopback.

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

`npm start` usa un proxy hacia la API local en el puerto 8000. Si Docker ya ocupa el puerto 4200, usar `npm start -- --port 4201`.

Backend local, desde la raíz:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements/dev.txt
cd backend
../.venv/Scripts/python.exe -m pytest
../.venv/Scripts/ruff.exe check .
```

La prueba de integración requiere PostgreSQL y migraciones; se ejecuta en el entorno Docker con `docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --rm test-backend`. Las unitarias no necesitan base de datos. Para ejecutar FastAPI fuera de Docker hay que configurar `backend/.env` con una base PostgreSQL alcanzable y ejecutar `alembic upgrade head` antes de `uvicorn app.main:app --reload`. No se crea una segunda base implícitamente.

## Organización

`backend/` contiene configuración, API versionada, núcleo, repositorios y módulos. `frontend/` contiene núcleo, componentes compartidos y módulos Angular. `infraestructura/` aloja Docker, nginx y scripts. `documentacion/` conserva arquitectura, decisiones, API, plan y evidencia. `datos/` contendrá ejemplos autorizados y perfiles sintéticos. `licencias/` registra dependencias y avisos. `secretos_locales/` está excluido de Git.

Las carpetas de módulos futuros son reservas de estructura, no funcionalidades terminadas. No se publican endpoints vacíos ni respuestas simuladas de IA.

## Reglas de trabajo

Carpetas de dominio en español sin tildes; clases, métodos, servicios y endpoints en inglés. Interfaz en español. HTML, SCSS, TS y pruebas en archivos separados. Toda modificación del esquema usa Alembic. Ninguna clave de proveedor llega al navegador.

Ramas: `main`, `develop`, `feature/*`, `fix/*`, `refactor/*`, `docs/*`. Commits descriptivos con prefijos `feat`, `fix`, `docs`, `test`, `refactor`. No fusionar si fallan Docker, contratos o pruebas.

El repositorio se inicia localmente; la publicación en GitHub requiere elegir la cuenta y visibilidad. No hay remoto configurado por defecto.

## Documentación

- [Plan y requisitos](documentacion/PLAN_DE_TRABAJO.md)
- [Arquitectura](documentacion/arquitectura/arquitectura.md)
- [Decisiones iniciales](documentacion/decisiones_tecnicas/0001-base-tecnica.md)
- [Contrato de salud](documentacion/api/health.md)
- [Base de datos](documentacion/base_datos/modelo_inicial.md)
- [Evidencia del primer bloque](documentacion/pruebas/hito_01.md)

La licencia de distribución del código propio queda pendiente de decisión del autor y de las condiciones institucionales. No se ha concedido una licencia abierta automáticamente.
