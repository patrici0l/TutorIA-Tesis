# Hito 8: recepción y consulta de perfiles sintéticos

7 de octubre de 2026, sesión nocturna local (8 de octubre UTC). Alcance técnico: API, persistencia y pantalla de perfiles ficticios privados. Integración con el módulo institucional externo y validación académica pendientes.

## Verificación automática

- Suite Docker Python 3.12/PostgreSQL: 275 pruebas aprobadas en 27,01 s. Dos advertencias conocidas de Starlette/HTTPX y pypdf.
- Angular: 54 pruebas aprobadas en 14 archivos. Validación, confirmación ficticia, bloqueo de doble envío pendiente, consulta segura y ausencia de reintentos automáticos.
- Ruff check y format: 143 archivos limpios. Build Angular de producción sin advertencias: 305,72 kB inicial y 15,91 kB módulo perfiles.
- `docker compose up -d --build --wait`: migración 0008 aplicada; backend, frontend y PostgreSQL saludables. Volúmenes/modelos conservados.

Pruebas nuevas: 26 casos de validación (incluidos booleanos/strings numéricos, límites, NaN/infinito, controles, duplicados y propietario falsificado) y dos recorridos de integración. Creación 201, consulta persistida, paginación, observaciones sucesivas sin sobrescritura, propiedad estricta incluso para admin, rechazo de estudiantes, CSRF, no-store, cuerpo excesivo 413 y limitador antes de persistir. Nivel informado permanece independiente del porcentaje. Todas las suites sin servicios de IA externos.

## Recorrido en navegador y SQL

Sesión docente ficticia existente. Se guardó SYN-001 / Derivadas / desempeño 42 / cuatro intentos / regla_potencia / dominio low / apoyo reinforcement / 120 segundos / tendencia improving. Checkbox de datos ficticios explícito.

UUID: `5bb5b546-d9bb-49b6-ada5-f26528952c01`. Fecha PostgreSQL: `2026-10-08 02:55:44.997548+00`. Payload y versión `performance-profile-v1` comprobados con consulta SQL. Tras recargar, Actualizar lista y Abrir perfil recuperan todos los campos desde backend. El formulario reinicia sus valores y la observación guardada permanece.

Capturas: [escritorio](hito_08_perfiles_desktop.png) y [móvil](hito_08_perfiles_mobile.png). Móvil solicitado 390×844, ancho DOM útil y scrollWidth iguales a 375 px; sin desbordamiento horizontal. Se restauró el viewport. Se mantuvieron colores UPS, navegación superior y estados de formulario/lista/detalle.

Ninguna llamada Gemini en este bloque. Guardar perfiles no genera recursos ni modifica el cupo de generación. No se afirma conexión con estudiantes reales, personalización ya implementada ni resultado académico.
