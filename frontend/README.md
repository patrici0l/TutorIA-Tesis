# Frontend TutorIA-Lucero

Angular con rutas standalone, servicios HTTP y componentes con TS, HTML, SCSS y spec separados. La pantalla /inicio consulta el estado real del backend.

Desde esta carpeta: npm ci, npm start, npm test -- --watch=false y npm run build. El proxy local dirige /api a localhost:8000. No colocar secretos en src/environments ni en variables de compilación.

La guía completa de Docker y el plan por hitos están en el README de la raíz.

## Nombres de componentes

Usar un nombre corto y la extensión, sin el sufijo `.component`: `login.ts`,
`login.html`, `login.scss` y `login.spec.ts`. Cada componente conserva sus cuatro
archivos separados. El generador Angular está configurado para seguir este formato.
Las clases y selectores Angular conservan sus nombres para evitar cambios de contrato.
Servicios, modelos, directivas y guardias mantienen sus sufijos de tipo.

Los nombres que repetían el contexto de su carpeta se simplificaron:

| Nombre anterior | Nombre actual (TS, HTML, SCSS y spec) |
| --- | --- |
| navigation.component | nav |
| assignment-practice.component | resolve |
| document-chunks.component | chunks |
| preparation.component | prepare |
| resource-view.component | view |
| resource-history.component | history |
| resource-audit.component | audit |
| resource-export.component | export |
| generation-quota.component | quota |

El resto conserva su nombre base (`app`, `login`, `inicio`, `practice`, `assignments`,
`profiles`, `metrics`, `search` y `documentos`), eliminando únicamente `.component`.

El recorrido de interfaz está descrito en [flujo docente](../documentacion/manuales/flujo_docente.md): documentos, recursos y actividades asignadas; perfiles y búsqueda son apoyos opcionales.
