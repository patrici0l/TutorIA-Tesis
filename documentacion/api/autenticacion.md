# API de autenticación institucional

Todas las rutas utilizan /api/v1/auth. Los errores no contienen tickets ni cookies. OpenAPI se genera desde FastAPI.

| Método y ruta | Comportamiento |
|---|---|
| GET /login | 302 al proveedor configurado o al callback mock; cookie temporal de state |
| GET /callback | Comprueba state/cookie, consume el intento, valida CAS y aprovisiona usuario; 303 al inicio y cookie de sesión |
| GET /me | 200 con user y auth_mode; 401 sin sesión, con sesión vencida o usuario inactivo |
| POST /logout | Requiere X-TutorIA-Client: web; 204, invalida sesión y borra cookies; 403 sin cabecera |

El callback recibe state y el ticket bajo el nombre configurado en CAS_TICKET_PARAMETER. La ausencia o formato incorrecto de state produce 422. Un intento vencido/reutilizado, ticket rechazado, dominio no permitido o cuenta inactiva vuelve a la pantalla de login con un error genérico. El navegador no recibe tokens en JSON ni puede elegir correo/rol mediante query.

GET /me devuelve:

```json
{
  "auth_mode": "mock",
  "user": {
    "id": "UUID",
    "institutional_email": "estudiante.demo@example.org",
    "institutional_id": "mock:student-001",
    "nombre": "Estudiante",
    "apellido": "Demostración",
    "rol": "student",
    "activo": true,
    "created_at": "fecha ISO 8601",
    "last_login": "fecha ISO 8601"
  }
}
```

No existen POST /login, /register ni /refresh. No se aceptan contraseñas. El botón Angular inicia una navegación del navegador, no un formulario de credenciales ni una petición que siga redirecciones mediante XHR.
