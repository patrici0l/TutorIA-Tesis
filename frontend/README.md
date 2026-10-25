# Frontend TutorIA-Lucero

Angular con rutas standalone, servicios HTTP y componentes con TS, HTML, SCSS y spec separados. El inicio docente consulta la disponibilidad del backend.

Desde esta carpeta: npm ci, npm start, npm test -- --watch=false y npm run build. El proxy local dirige /api a localhost:8000. No colocar secretos en src/environments ni en variables de compilación.

La guía completa de Docker y el plan por hitos están en el README de la raíz.

## Nombres de componentes

Usar un nombre corto y la extensión, sin el sufijo `.component`: `login.ts`,
`login.html`, `login.scss` y `login.spec.ts`. Cada componente conserva sus cuatro
archivos separados. El generador Angular está configurado para seguir este formato.
Las clases y selectores Angular conservan sus nombres para evitar cambios de contrato.
Servicios, modelos, directivas y guardias mantienen sus sufijos de tipo.

El recorrido de interfaz está descrito en [flujo docente](../documentacion/manuales/flujo_docente.md): documentos, recursos y actividades asignadas; perfiles y búsqueda son apoyos opcionales.
