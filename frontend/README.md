# Frontend

Interfaz Angular de carga documental, preparación/generación de recursos, consulta y actividades por rol. La existencia de una pantalla no acredita aceptación académica.

## Ejecución local

Desde `TutorIA-Lucero/frontend`, ejecutar `npm ci` y `npm start`. El backend debe estar disponible en localhost:8000; el proxy dirige /api al backend. Para Docker consultar [el README raíz](../README.md).

## Verificación

- `npm test -- --watch=false`: pruebas.
- `npm run build`: compilación; salida en dist/prototipo.

## Organización

Código en src/app; componentes con archivos TS, HTML, SCSS y spec separados. Rutas standalone, servicios HTTP y entorno público en src/environments. No introducir claves, tokens privados o contraseñas en el frontend.

## Uso

Acceder con el rol de demostración disponible en login. Docente: cargar material, procesar e indexar, preparar un recurso, cotejar fuentes y generar. Generar puede consumir una API externa; consultar lo guardado no debe regenerarlo. Estudiante: consultar las actividades habilitadas para su identidad. El modo local no valida una identidad universitaria.

Las funciones y contratos definitivos siguen sujetos al plan aprobado y acuerdos pendientes. No repetir en este archivo el plan de tesis ni las bitácoras privadas.

## Responsabilidades

- `nucleo/`: sesión, guardia, interceptor, salud y selección de vistas por rol para `/inicio` y `/actividades`.
- `compartido/`: navegación, directiva matemática y estilos reutilizables.
- `modulos/docente/`: inicio, documentos, recursos, actividades, búsqueda, perfiles y métricas.
- `modulos/estudiante/`: inicio, actividades, resolución y práctica libre.
- `modulos/autenticacion/`: acceso.
- `modulos/actividades/`: contrato, HTTP, estado de listados y tarjeta común de actividades.
- `modulos/practica/`: bancos, contratos y acceso HTTP de práctica, reutilizados desde asignaciones.
- `modulos/contenidos/`: contratos, servicio y visualización de recursos compartidos por los dos roles; las herramientas de creación y auditoría están en docente.

Las rutas externas y los contratos HTTP no cambian. Las vistas por rol organizan la presentación; la autorización efectiva permanece en FastAPI.
