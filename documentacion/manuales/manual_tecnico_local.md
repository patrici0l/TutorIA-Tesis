# Manual técnico del entorno local

10 de octubre de 2026. Operación del MVP con Docker Desktop en Windows y datos
sintéticos. No certifica despliegue de producción ni cierre de la evaluación académica.

## Ubicación y servicios

Raíz actual: `C:\C_PROJECTS\TESIS COMPUTACION\TutorIA-Lucero`.
Ejecutar los comandos de este manual desde esa carpeta en PowerShell.

| Servicio | Función | Acceso |
|---|---|---|
| frontend | Angular compilado y nginx; proxy de API | http://localhost:4200 |
| backend | FastAPI, permisos, procesamiento y generación | http://localhost:8000/api/v1/docs |
| postgres | PostgreSQL 17 y pgvector | Consola dentro de Docker; sin puerto en Windows |
| migrate | Alembic; ejecuta migraciones antes del backend | Terminar con código 0 es normal |
| prepare-embeddings | Descarga/verifica pesos locales, bajo perfil embeddings | Ejecución manual única cuando falten pesos |

API e interfaz se publican en loopback: otro equipo no puede acceder por estas URLs.
Swagger describe la API; no es una consola de DB. Para acciones autenticadas se recomienda
la interfaz, que comparte origen con el callback y conserva sesión/CSRF.

## Primer arranque y uso diario

Iniciar Docker Desktop con contenedores Linux. Solo si no existe configuración local:

```powershell
./infraestructura/scripts/initialize-local.ps1
docker compose up -d --build --wait
```

El inicializador conserva un .env existente. La plantilla nueva deja Gemini deshabilitado.
No necesita una clave de IA para login mock, documentos, búsqueda, perfiles o historial.
Para indexar, preparar los pesos con internet una vez:

```powershell
docker compose --profile embeddings run --no-deps --rm prepare-embeddings
```

Después se reutiliza embedding_data y la inferencia de embeddings funciona localmente.
En días posteriores, para iniciar y comprobar:

```powershell
docker compose up -d --wait
./infraestructura/scripts/check-health.ps1
docker compose ps --all
```

Backend/frontend/postgres deben indicar healthy; migrate puede figurar Exited (0).
check-health verifica nginx → FastAPI → PostgreSQL/pgvector. No llama a Gemini.
Tras modificar código, usar `docker compose up -d --build --wait`.

## Sesión docente de demostración

Abrir http://localhost:4200/login y pulsar Iniciar sesión con cuenta UPS. Es una identidad
ficticia controlada por backend; no pide contraseña institucional ni conecta con UPS.
Para docente, ajustar únicamente `AUTH_MOCK_USER=teacher` en el .env de la raíz y ejecutar:

```powershell
docker compose up -d --wait
```

Cerrar sesión y volver a entrar. Cambiar el selector no transforma una sesión ya abierta.
Para estudiante usar `AUTH_MOCK_USER=student` y repetir el procedimiento.
El [recorrido docente](guia_docente_mvp.md) explica carga, procesamiento, índice y recursos.
No habilitar CAS real en esta etapa.

## Backend, logs y consola de base de datos

Swagger: http://localhost:8000/api/v1/docs.
Salud directa: http://localhost:8000/api/v1/health.
Salud a través de nginx: http://localhost:4200/api/v1/health.

```powershell
docker compose logs --tail 50 backend migrate
docker compose logs --tail 30 frontend
docker compose exec postgres psql -U tutoria -d tutoria
```

El comando psql corresponde al usuario/nombre estándar de este entorno; si se cambiaron,
usar sus nombres configurados. Dentro de psql:

```sql
\dt
\d generaciones_contenido
SELECT version_num FROM alembic_version;
SELECT extversion FROM pg_extension WHERE extname = 'vector';
SELECT status, count(*) FROM generaciones_contenido GROUP BY status;
\q
```

Estos comandos consultan estructura, versiones y conteos. Evitar editar reservas,
permisos o estados a mano; hacerlo podría invalidar experimentos y límites de generación.
No imprimir .env, cookies, tickets ni configuración completa con secretos para diagnóstico.

## Dónde permanecen los datos

| Volumen Docker actual | Contenido |
|---|---|
| tutoria-lucero_postgres_data | Usuarios, sesiones, perfiles, fragmentos/vectores, preparaciones/resultados y reservas |
| tutoria-lucero_document_data | Archivos originales privados |
| tutoria-lucero_embedding_data | Pesos E5 locales verificables/reutilizables |

Docker Desktop administra estos volúmenes. No existe un archivo .db en la raíz de Windows.
Git conserva código/evidencia permitida; no respalda DB, archivos privados, pesos ni .env.
Eliminar un documento tampoco elimina automáticamente fuentes guardadas en recursos.

## Crear un respaldo consistente

El respaldo incluye DB en formato custom de PostgreSQL, documentos y manifiesto SHA-256.
Su carpeta `respaldos_locales` está excluida de Git. Contiene datos privados de aplicación;
conservarla en almacenamiento con acceso restringido. Los secretos y pesos no se copian.

Antes de pausar, terminar cualquier procesamiento/generación y comprobar que no haya
generaciones activas:

```powershell
docker compose exec postgres psql -U tutoria -d tutoria -c "SELECT count(*) FROM generaciones_contenido WHERE status='generating';"
```

Si hay actividad, esperar y revisar historial antes de continuar. Evitar otros clientes
SQL/escritores mientras se respalda. Con PostgreSQL activo y aplicación inactiva:

```powershell
try {
    docker compose stop frontend backend
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo pausar la aplicación' }
    ./infraestructura/scripts/backup-local.ps1
} finally {
    docker compose up -d --wait backend frontend
}
./infraestructura/scripts/check-health.ps1
```

El script rechaza frontend/backend/migrador/preparador de embeddings activos; no los
detiene por su cuenta. Crea una carpeta nueva y muestra su ruta. Usa docker cp para el
dump binario, evitando corrupción por redirección de PowerShell. El archivo manifest.json
solo se genera al completar ambos archivos; una carpeta sin manifiesto no es una copia
completa. Copiar la carpeta terminada a otro almacenamiento para cubrir fallo del disco
local; una copia en el mismo equipo no cubre ese fallo.

Conservar por separado configuración privada y referencia del código utilizado para
una recuperación en otro equipo. No agregarlas a este respaldo ni publicarlas en Git.
Los pesos se vuelven a preparar mediante el comando embeddings y su especificación fijada.

## Comprobar recuperación sin tocar los datos activos

Sustituir el marcador por la carpeta mostrada al respaldar:

```powershell
./infraestructura/scripts/verify-local-backup.ps1 -BackupDirectory "./respaldos_locales/IDENTIFICADOR_DE_LA_COPIA"
```

No necesita pausar la aplicación. Comprueba tamaño/hash de ambos archivos y restaura
PostgreSQL en un contenedor temporal sin red, puertos ni volúmenes del proyecto.
Lee y verifica cada documento del archivo contra el manifiesto sin escribir en document_data.
Finalmente retira el contenedor temporal y guarda un informe nuevo junto a la copia.
El manifiesto original permanece intacto; el informe separado registra la comprobación.

La DB temporal dispone de 512 MiB: adecuada para esta muestra local, sin validación de
escala productiva. El script restaura sin propietarios/ACL originales en una identidad de
prueba; no ensaya políticas de usuarios PostgreSQL de producción. Nunca sustituye la DB activa.

Para una recuperación real, crear primero un entorno destino separado compatible con
PostgreSQL/pgvector, importar el dump con pg_restore y recuperar los documentos allí;
validar vínculos, permisos y salud antes de sustituir un entorno. La sustitución real del
entorno y su automatización siguen pendientes; este manual no prescribe sobrescribir
la base activa ni borrar volúmenes para ensayar.

## Fallos habituales y apagado

| Síntoma | Acción |
|---|---|
| No conecta Docker | Iniciar Docker Desktop y comprobar contenedores Linux. |
| Interfaz detenida, nginx: host not found in upstream backend | Confirmar backend healthy; ejecutar docker compose up -d --wait frontend y volver a comprobar salud. |
| API 503 | Revisar estado de postgres y migrate; conservar volúmenes. |
| Fallo de migración | Revisar logs de migrate antes de iniciar operaciones; no crear tablas a mano. |
| Documentos no encuentran fuentes | Comprobar propiedad, extracción e índice: cargar no equivale a indexar. |
| Se perdió respuesta de generación | Consultar historial; no reenviar preparaciones reservadas. |
| Cupo agotado | Esperar renovación UTC y comprobarlo; reiniciar Docker no reinicia reservas. |
| Cambio de DB_PASSWORD no permite conectar | Cambiar .env no cambia la contraseña ya almacenada en el volumen; revisar credenciales sin resetear datos. |

Para terminar conservando datos:

```powershell
docker compose stop
```

No usar down -v, reset de fábrica o eliminación de volúmenes como arreglo de conexión.

## Verificación y alcance

Creación y restauración aislada comprobadas el 10 de octubre:
[evidencia de respaldo](../pruebas/respaldo_local_20261010.md).
Manual cotejado con Compose/scripts actuales; no prueba instalación en un segundo equipo
ni despliegue público. Gemini, benchmark y revisión pedagógica mantienen sus pendientes.
