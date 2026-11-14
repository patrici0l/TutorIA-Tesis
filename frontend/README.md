# Frontend

Interfaz Angular de carga documental, preparación/generación de recursos, consulta y actividades por rol. La existencia de una pantalla no acredita aceptación académica.

## Ejecución local

Desde `TutorIA-Lucero/frontend`, ejecutar `npm ci` y `npm start`. El backend debe estar disponible en localhost:8000; el proxy dirige /api al backend. Para Docker consultar [el README raíz](../README.md).

## Verificación

- `npm test -- --watch=false`: pruebas.
- `npm run build`: compilación; salida en dist/prototipo.

## Organización

La entrada está en `src/app`. Hay cuatro carpetas principales: `inicio`, `profesor`, `estudiante` y `compartido`. Dentro de cada pantalla están juntos su vista, estilos, código, pruebas y servicios. No hace falta entrar en carpetas adicionales de páginas, componentes, modelos o servicios.

```text
src/app/
├── inicio/                 Login, sesión y entrada al inicio según el rol
├── profesor/
│   ├── inicio.*            Pantalla inicial del profesor
│   ├── actividades/       Crear, asignar y gestionar actividades
│   ├── busqueda/          Buscar fuentes por asignatura
│   ├── documentos/        Carga, biblioteca, fragmentos y asignaturas
│   ├── metricas/          Consultar uso de generación
│   ├── perfiles/          Gestionar perfiles de aprendizaje
│   └── recursos/          Preparar, generar, revisar y exportar recursos
├── estudiante/
│   ├── inicio.*            Pantalla inicial del estudiante
│   ├── actividades/       Ver actividades y resolver las asignadas
│   └── practica/          Práctica libre e historial de intentos
├── compartido/
│   ├── actividades/       Tarjeta, datos y servicio usados por ambos roles
│   ├── estilos/           Estilos comunes y animaciones
│   ├── navegacion/        Menú y enlaces por rol
│   ├── practica/          Bancos de preguntas y reglas comunes
│   ├── recursos/          Lectura y tipos de recursos usados por ambos roles
│   ├── salud.*            Comprobación de conexión con la API
│   ├── texto-matematico.* Presentación de fórmulas
│   └── atencion-vista.*   Foco y desplazamiento al mostrar resultados
├── app.routes.ts          Relación entre direcciones y pantallas
├── app.config.ts          Configuración global
└── app.*                  Contenedor principal de la aplicación
```

`inicio.*` y `app.*` representan varios archivos con el mismo nombre base, no carpetas. Por ejemplo, `profesor/inicio.html` y `profesor/inicio.ts` están directamente dentro de `profesor`.

### Dónde cambiar cada cosa

| Si quieres cambiar… | Busca aquí |
|---|---|
| El acceso a la aplicación | `inicio/login.*` |
| La sesión y la protección de rutas | `inicio/sesion.service.ts`, `sesion.guard.ts` y `sesion.interceptor.ts` |
| El inicio del profesor o del estudiante | `profesor/inicio.*` o `estudiante/inicio.*` |
| La pantalla de documentos | `profesor/documentos/documentos.*` |
| El listado de documentos | `profesor/documentos/biblioteca.*` |
| La revisión de fragmentos | `profesor/documentos/fragmentos.*` |
| Las asignaturas disponibles | `profesor/documentos/asignaturas.service.ts` |
| La preparación y generación | `profesor/recursos/preparar.*` |
| Los recursos guardados | `profesor/recursos/historial.*` |
| La lectura de un recurso en ambos roles | `compartido/recursos/recurso.*` |
| Resolver una actividad | `estudiante/actividades/resolver.*` |
| Los enlaces del menú | `compartido/navegacion/enlaces.ts` |

En cada pantalla, `.html` contiene lo que se muestra, `.scss` define su apariencia y `.ts` contiene su comportamiento. Los archivos `.service.ts` realizan las consultas o acciones con la API; `.model.ts` describe los datos; `.spec.ts` comprueba el comportamiento. Los estilos que empiezan por `_` se reutilizan desde otros estilos.

Para añadir una función del profesor, usar la carpeta de su pantalla en `profesor`; aplicar lo mismo en `estudiante`. Poner en `compartido` solo lo reutilizado por varias pantallas o por ambos roles. No crear subcarpetas para separar uno o dos servicios de su pantalla.

El entorno público sigue en `src/environments`. No introducir claves, tokens privados o contraseñas en el frontend.

## Uso

Acceder con el rol de demostración disponible en login. Docente: cargar material, procesar e indexar, preparar un recurso, cotejar fuentes y generar. Generar puede consumir una API externa; consultar lo guardado no debe regenerarlo. Estudiante: consultar las actividades habilitadas para su identidad. El modo local no valida una identidad universitaria.

Las funciones y contratos definitivos siguen sujetos al plan aprobado y acuerdos pendientes. No repetir en este archivo el plan de tesis ni las bitácoras privadas.

Las direcciones de navegación se conservan: `/login`, `/inicio`, `/documentos`, `/recursos`, `/actividades`, etc. `inicio/inicio.ts` elige el inicio del rol y `compartido/actividades/actividades.ts` elige su vista de actividades. Las carpetas organizan el código; la autorización efectiva permanece en FastAPI.
