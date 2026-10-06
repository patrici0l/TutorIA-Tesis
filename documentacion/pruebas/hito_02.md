# Evidencia de autenticación institucional preparada

Cierre del bloque: 6 de octubre de 2026, America/Guayaquil. Alcance: flujo mock completo y adaptador CAS configurable. No se contactó ningún servidor institucional.

## Resultados comprobados

| Verificación | Resultado |
|---|---|
| Backend local, pytest backend/tests -q | 35 aprobadas; 2 de PostgreSQL omitidas explícitamente sin RUN_DB_TESTS |
| Backend en Docker con PostgreSQL | 37 aprobadas; ninguna omitida |
| Ruff check y format --check backend | Sin errores; 54 archivos formateados |
| Angular, npm test -- --watch=false | 15 aprobadas, 6 archivos en la verificación de este bloque |
| Angular producción en Docker | Compilación correcta, bundle inicial 253.33 kB |
| Docker Compose | PostgreSQL, backend y frontend saludables; migración termina con éxito |
| Alembic / esquema real | 0002 aplicada; usuarios sin password/password_hash, sesiones persistidas |
| Navegador | Botón UPS → cuenta ficticia → dashboard; recarga mantiene sesión |
| Navegador, logout / guard | Logout retorna a login; acceso directo a /inicio vuelve a /login |
| Git | .env, backend/.env y secretos_locales ignorados; diff --check correcto |

Las pruebas comprueban expiración, revocación, estado ligado al navegador y de un solo uso, aprovisionamiento sin duplicados, rotación de sesión, cuentas desactivadas, separación mock/cas y rechazo de identidad/rol enviados por el cliente. El adaptador CAS se prueba con XML válido/inválido, dominios falsificados, docente deshabilitado/habilitado, entidades externas, atributos duplicados y transporte HTTP simulado sin redirecciones. El caso callback CAS confirma el service exacto y cookie Secure mediante validador simulado.

Las dos pruebas de integración usan PostgreSQL real: health/vector/Alembic y persistencia/rotación/logout con aislamiento transaccional. No introducen usuarios de prueba permanentes.

## Reproducción

Desde la raíz:

```powershell
docker compose up -d --build --wait
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --build --rm test-backend
```

Desde frontend: `npm test -- --watch=false`. Abrir http://localhost:4200/login con AUTH_MODE=mock y pulsar el botón UPS; no se ingresan credenciales. Capturas: hito_02_login.png y hito_02_dashboard.png.

## Límites y pendientes

La validación real CAS requiere endpoints autorizados, callback y atributos confirmados por TI. El acceso mock se permite solo en desarrollo y loopback; en HTTP local Secure está desactivado y en CAS es obligatorio. La administración de permisos no tiene interfaz todavía. El límite de intentos actual es por proceso y debe adaptarse antes de un despliegue distribuido.

TestClient emite una advertencia de deprecación Starlette/HTTPX; las pruebas pasan. Estas verificaciones no constituyen evaluación pedagógica ni certificación de producción.
