# Manual visual de la integración con Moodle

[Abrir el manual completo en PDF](manual-moodle-tutoria.pdf).

**20 páginas**, **11 capturas originales de Playwright** incrustadas, indicaciones
numeradas y diagramas de casos de uso, componentes, despliegue, secuencia, estados y
datos. El PDF se comparte como un solo archivo, sin imágenes externas.

El valor añadido es el recorrido docente dentro de Moodle: validación nativa,
persistencia por docente/curso, conexión con ADAPTIA y TutorIA, correlación,
protección ante envíos duplicados y errores conservados en el historial. Utiliza
las APIs de Moodle y el contrato de ocho campos de [la guía de ADAPTIA](adaptia.md).

| Contenido | Páginas |
| --- | --- |
| Casos de uso, componentes, despliegue y secuencia | [2-5](manual-moodle-tutoria.pdf#page=2) |
| Curso, formulario y ejemplo numerado | [6-8](manual-moodle-tutoria.pdf#page=6) |
| Validación, fallo real, historial y estados | [9-11](manual-moodle-tutoria.pdf#page=9) |
| Permisos, privacidad, salida controlada y móvil | [12-14](manual-moodle-tutoria.pdf#page=12) |
| Swagger y datos | [15-16](manual-moodle-tutoria.pdf#page=15) |
| Clave, modelo, configuración, fork y despliegue | [17-18](manual-moodle-tutoria.pdf#page=17) |
| Pruebas, comandos y diagnóstico | [19-20](manual-moodle-tutoria.pdf#page=19) |

Evidencia al **19/11/2026, 22:13, America/Guayaquil**: 39 casos de regresión ADAPTIA
aprobados en base aislada, 11 comprobaciones E2E base y 12 del recorrido documental.
Son grupos parcialmente solapados, no un porcentaje de cobertura.

El **503 provino de TutorIA real con la IA apagada**. La salida exitosa fotografiada
es un **fixture explícito de interfaz**, no una generación de Gemini. Las cuentas
ficticias se limpiaron al terminar. Modelo preparado: `gemini-3.1-flash-lite`, cinco
intentos diarios; clave vacía y habilitación/confirmaciones en `false`. Falta la
primera generación externa con clave y cuota verificadas.

El formulario usa perfil ficticio e historial de rendimiento vacío. Publicación de
contenido real, RAG del POST externo y evaluación pedagógica quedan pendientes. No
se ejecutaron PHPUnit, PHPCS, carga ni auditoría WCAG completa. Privacy API borra
registros locales; no se implementó el borrado de trazas remotas de TutorIA.

Rama de esta entrega de TutorIA: `feat/api-adaptia`. El PDF conserva el corte de
captura del 19/11/2026 y el estado Git previo a esta publicación; no describe el
historial posterior. Moodle continúa en `moodle-worker`, rama `integracion/tutoria`
del fork `jAndresSagbay95/moodle`, con cambios locales independientes.
El PDF es idéntico al de `moodle-worker/ambiente-local/docs/tutoria/`, que también
tiene índice de revisión.

Los originales y el generador quedan en el área local ignorada
`documentacion-local/adaptia-api/manual/`. La continuidad está en
`documentacion-local/API-ADAPTIA-CONTINUIDAD.md` y `CONTEXTO-API-ADAPTIA.md` de la
carpeta de Patricio. No se agregan PNG sueltos al conjunto versionable.

SHA256: `410aa0af12e6b595cae277834965b3a2185339cf4a25e9422f8040d627ea3a02`.
