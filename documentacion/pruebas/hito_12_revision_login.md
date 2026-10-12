# Revisión de acceso local — 11 de octubre de 2026

Corregidos tres errores backend: state/cookie Unicode producía TypeError al comparar
el retorno del login; puertos inválidos de autenticación no se rechazaban; el nombre
CAS_TICKET_PARAMETER=state podía colisionar con el control del callback. Ahora se rechazan
esas entradas/configuraciones. Se conservan sesiones HttpOnly, rotación, revocación y CSRF.

GET /api/v1/auth/config publica solamente auth_mode, sin cookies, identidad ni parámetros
institucionales. Angular consulta sesión al abrir login: redirige a inicio si es válida;
si no existe, muestra el acceso correspondiente al modo del servidor. En mock el botón
es “Entrar a la demostración”, sin correo ni contraseña. Los fallos de conexión muestran
reintento en lugar de ofrecer un enlace de acceso a un backend no disponible.

Nginx utiliza resolución dinámica del backend con DNS de Docker y zona compartida;
evita fijar una IP durante toda la vida del proceso. Sintaxis validada en contenedor
desplegado y también con --network none, sin que exista el nombre backend al validar.
Referencia: [resolve de Nginx](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#resolve).
No se forzó un cambio de IP para simular otra recreación durante la comprobación.

## Verificación real

- 47 pruebas backend de configuración/auth/CAS simulado/salud aprobadas; advertencia
  conocida Starlette/HTTPX, sin fallos.
- 13 pruebas Angular en cuatro archivos aprobadas: login, servicio, guard e interceptor.
- Construcción Docker backend/frontend completada; compose up -d --wait satisfactorio.
- PostgreSQL, backend y frontend saludables. Nginx -t correcto; auth/config devuelve mock.
- Navegador: entrada como Docente Demostración, inicio con API/DB/vector disponibles,
  apertura de /login con sesión vuelve a /inicio, logout vuelve a login, /documentos
  sin sesión devuelve a login. Captura: [login mock](hito_12_login_mock.png).
- Base conservada: 21 generaciones, migración 0011_execution_configuration. No purgas,
  migraciones nuevas, llamadas IA ni conexión al CAS real. Login/logout sí crean/revocan
  sesiones de demostración según el flujo normal.

Se desplegó el árbol actual, incluidos adaptadores internos y revisión offline previamente
pendientes de commit. OpenAI/Claude continúan bloqueados para envíos API; configuración
secreta y selector del usuario mock sin cambios. No implica auditoría exhaustiva ni cierre
del proyecto. Quedan evaluación académica y recorrido experimental con proveedores simulados.
