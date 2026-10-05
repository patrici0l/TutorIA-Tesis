# Evidencia del primer hito

Fecha: 4 de octubre de 2026, America/Guayaquil. Alcance: bloque inicial de la sección 21 del plan. No incluye autenticación, ingesta ni generación IA.

## Verificaciones realizadas

| Verificación | Resultado observado |
|---|---|
| Angular producción, npm run build | Correcto; bundle inicial aproximado de 248 kB |
| Angular, npm test -- --watch=false | 5 pruebas aprobadas, 2 archivos |
| Backend local, pytest | 6 aprobadas; 1 integración omitida expresamente sin RUN_DB_TESTS |
| Ruff | Sin errores |
| pip check | Sin dependencias incompatibles |
| npm install --package-lock-only --ignore-scripts | Auditoría reportó 0 vulnerabilidades en 277 paquetes |
| docker compose config --quiet | Configuración válida |
| docker compose up -d --build --wait | Arranque correcto; frontend, backend y PostgreSQL saludables |
| Alembic | 0001_enable_vector en head |
| HTTP a través de nginx | 200 con status, api, database y pgvector en ok |
| Navegador real | /inicio muestra los tres servicios disponibles; botón reintenta correctamente |
| Git | .env y secretos_locales ignorados; revisión del contenido a versionar |

La captura `hito_01_interfaz.png` documenta el estado observado. Las pruebas Angular verifican carga, éxito, degradación parcial, fallo de red, reintento y respuesta fuera de contrato. Las unitarias backend verifican éxito, extensión ausente, BD caída sin exponer detalles sensibles, OpenAPI y contraseñas con caracteres especiales.

La ejecución local utilizó Node 24.15.0 y Python 3.14.4. La imagen backend utiliza Python 3.12.15. Las versiones de dependencias están fijadas en los archivos de requisitos y el lockfile npm.

## Integración en contenedor

Comando reproducible desde la raíz:

```powershell
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --build --rm test-backend
```

Esta ejecución activa RUN_DB_TESTS y comprueba una consulta vectorial real, la revisión de Alembic y la respuesta de FastAPI contra PostgreSQL. Resultado: pendiente de finalizar la ejecución inicial.

## Límites de esta evidencia

No se afirma validación de seguridad de producción ni evaluación pedagógica. La integración institucional, GitHub y los proveedores IA no se han conectado. Las pruebas con TestClient emiten una advertencia de deprecación de Starlette sobre HTTPX; no impide los resultados, pero deberá atenderse al actualizar el entorno de pruebas.
