# Autenticación institucional UPS

Decisión del autor del 5 de octubre de 2026. Sustituye el registro abierto y la autenticación local del plan original. No se utilizan Google OAuth, contraseñas locales ni JWT en el navegador.

## Flujo común

Angular presenta un único botón hacia GET /api/v1/auth/login. FastAPI crea un intento temporal con state aleatorio y una cookie HttpOnly para vincularlo al navegador. En modo cas redirige al login institucional configurado; en modo mock redirige directamente al callback con una identidad ficticia definida exclusivamente en backend. Angular no elige el usuario ni envía un correo para autenticarse.

El callback comprueba que state coincida con la cookie y consume el intento de forma atómica en la base de datos. En CAS, FastAPI valida el ticket por HTTPS contra CAS_VALIDATE_URL, usando exactamente el service que se envió al login. Solo una respuesta XML CAS de éxito, con correo válido y dominio permitido, puede producir una identidad. No hay fallback a mock cuando falla CAS.

La validación usa el protocolo XML CAS 2/3 como adaptador inicial. Se rechazan DTD, entidades externas, respuestas ambiguas, redirecciones HTTP y respuestas mayores de 1 MiB. El timeout es de ocho segundos. Los atributos y nombres de parámetros son configurables; esto no equivale a haber confirmado la implementación de la UPS. Referencia del adaptador: [especificación oficial de Apereo CAS](https://apereo.github.io/cas/development/protocol/CAS-Protocol-Specification.html).

## Identidad local

usuarios almacena únicamente id, institutional_email, institutional_id opcional, nombre, apellido, rol, activo, created_at y last_login. Nunca password ni password_hash. Se busca por identificador institucional o correo validado; se rechazan colisiones entre ambos. Se actualizan nombres y last_login sin duplicar usuarios, elevar permisos locales ni reactivar cuentas deshabilitadas.

Por defecto solo est.ups.edu.ec está permitido y se asigna student. ups.edu.ec puede habilitarse explícitamente para teacher. Ningún atributo remoto concede admin. La gestión administrativa detallada de roles queda para una política institucional confirmada; el esquema reserva ese valor.

El mock utiliza estudiante.demo@example.org o docente.demo@example.org, con identificadores mock:student-001 y mock:teacher-001. Son identidades ficticias sin contraseñas, definidas mediante AUTH_MOCK_USER. No pertenecen a la UPS. El modo mock solo arranca con APP_ENV=development y redirecciones a loopback. Las sesiones mock no sirven en modo cas, y los usuarios ficticios no se vinculan automáticamente a identidades CAS.

## Sesión TutorIA

La cookie tutoria_session contiene un token aleatorio opaco de 48 bytes; la base de datos guarda solo su SHA-256, usuario, modo y vencimiento. HttpOnly evita su lectura por Angular. SameSite=Lax permite el retorno GET desde CAS. En CAS, Secure y URLs HTTPS son obligatorias. En mock HTTP local, AUTH_COOKIE_SECURE=false permite la demostración en localhost. No se usan localStorage ni sessionStorage para autenticación.

Duración absoluta de ocho horas, configurable entre una y 24. Al expirar se vuelve a iniciar acceso UPS; el SSO puede conservar su propia sesión. No existe endpoint de refresh. El logout invalida la sesión en la base de datos y elimina cookies; solo cierra TutorIA, no toda la sesión universitaria. Las escrituras requieren X-TutorIA-Client: web y no se habilita CORS abierto.

Las respuestas auth llevan Cache-Control: no-store y Referrer-Policy: no-referrer. Nginx no registra las URLs de auth, Uvicorn se ejecuta sin access log y HTTPX no registra URLs a nivel INFO. El límite de inicios es 30/minuto por cliente y proceso; el despliegue local usa un worker. Antes de escalar deberá definirse limitación compartida y configuración de proxies confiables.

## Configuración y confirmación con TI

CAS_LOGIN_URL y CAS_VALIDATE_URL quedan vacías. AUTH_CALLBACK_URL, AUTH_FRONTEND_URL y AUTH_LOGIN_URL deben tener el mismo origen; CAS exige HTTPS. Los nombres service/ticket y los atributos email/uid/givenName/sn son valores del adaptador, no confirmaciones de TI. También es configurable usar cas:user como fuente de un atributo mediante el valor user, únicamente si TI confirma esa semántica.

Antes de habilitar CAS real necesitamos:

1. URLs autorizadas de login y validación, protocolo/versión y ambiente de pruebas.
2. Callback registrado, incluyendo la política sobre el parámetro state dinámico dentro de service.
3. Nombres, cardinalidad y significado de correo, identificador estable, nombre y apellido.
4. Dominios habilitados y política de autorización de estudiantes/docentes.
5. TLS, certificados, conectividad, límites y condiciones de despliegue.
6. Política de cierre global/single logout, si se exige después del cierre local de TutorIA.

No se realizaron solicitudes a endpoints de la UPS. Los tests CAS usan direcciones reservadas example.org y transporte simulado.
