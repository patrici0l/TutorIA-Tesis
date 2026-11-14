# Versión 0.2 — fuentes habilitadas y generación por asignatura

Actualizado: 12/11/2026. Responsable: Patricio Lucero.

## Qué cambia

El docente puede revisar una versión documental y habilitarla como fuente. La búsqueda semántica y la preparación de recursos consultan únicamente los materiales propios habilitados de la asignatura indicada. Retirar una fuente conserva su original y sus fragmentos, pero impide recuperarla para nuevas preparaciones y enviar preparaciones que todavía dependan de ella.

Esta es la implementación local de publicación Gold: una decisión explícita sobre la versión procesada e indexada. No duplica los documentos en otro almacén ni crea infraestructura adicional. La habilitación registra la fecha; el propietario ya identifica al docente responsable. El permiso sigue siendo una declaración que debe contrastarse con su evidencia.

La base técnica avanza; el cierre académico sigue pendiente del corpus autorizado, de la revisión docente y de una ejecución real con el modelo acordado. También sigue pendiente la aceptación con material real de v0.1. No se certifica una versión por tener sus pantallas o sus pruebas sintéticas terminadas.

## Requisitos de v0.2

| Requisito del plan | Resultado | Límite pendiente |
|---|---|---|
| G1: publicación y retirada | API y controles en detalles del documento; habilitación explícita, privada y por versión | Tutor/docentes deben aceptar esta política local antes del cierre académico |
| G1: asignatura y permisos en RAG | Filtros antes de ordenar por similitud: propietario, asignatura, permiso, publicación, estados e índice compatible | El nombre local de asignatura todavía no es un identificador ADAPTIA |
| Embeddings y recuperación semántica | Se reutilizan E5, pgvector, revisión fijada y búsqueda coseno exacta; no se introduce otro modelo | El corpus real debe probar la utilidad de los fragmentos y sus fórmulas |
| G2: explicación y ejemplo personalizado | Se reutiliza EXPLANATION con pasos y ejemplo resuelto, objetivo y adaptación por perfil sintético; la asignatura llega al prompt | Falta revisión pedagógica y ejecución real representativa; el ejemplo no es un tipo independiente |
| G2: primer LLM y dirección Claude | Gemini mantiene su confirmación gratuita; Claude puede habilitarse con confirmación de gasto, modelo y clave del operador | No se eligió un modelo institucional ni se realizaron llamadas externas en esta sesión |
| G2: trazabilidad y fallos | Solicitud con asignatura, perfil, fuentes con versión/procedencia/publicación, prompt versionado, modelo, parámetros, tokens y fallos | Registrar una cita válida no demuestra por sí solo fidelidad matemática |
| Fuentes retiradas o modificadas | Se vuelven a comprobar al reservar el envío; una republicación también exige preparar de nuevo | Una retirada no puede cancelar una llamada que ya comenzó ni borrar el texto previamente enviado |

Los acuerdos A1–A4 de integración siguen en el plan y la tabla de decisiones. No se inventaron rutas, tokens, contratos del motor ni permisos institucionales.

## Cómo usarlo

1. Cargar el documento con asignatura, procedencia y permiso. Procesar el texto y preparar su índice local.
2. Revisar los fragmentos frente al original. En detalles, pulsar **Habilitar como fuente** cuando esa versión sea apta para el uso previsto.
3. Indicar la asignatura al buscar fuentes o preparar un recurso. Una asignatura sin materiales habilitados no toma fuentes de otra materia.
4. Preparar la explicación y, si corresponde, elegir un perfil sintético. Revisar las fuentes antes de solicitar generación.
5. Para dejar de usar una versión, pulsar **Retirar de recursos**. El original y el historial se conservan. Las preparaciones pendientes que la usan deben rehacerse.

Cada versión se habilita y retira por separado. Cargar una sucesora no revoca automáticamente la anterior: si ambas siguen siendo aptas pueden coexistir. Para sustituir la anterior, retirarla expresamente. Reconstruir un índice retira su habilitación; después de revisar el resultado hay que habilitarlo de nuevo.

## Contrato local y compatibilidad

- `POST /api/v1/documents/{id}/publish`: habilita una versión propia con permiso, texto procesado e índice completo y compatible. Repetirlo mantiene la fecha de publicación.
- `POST /api/v1/documents/{id}/withdraw`: retira la habilitación sin eliminar el documento. Repetirlo mantiene el estado retirado.
- Ambas operaciones requieren sesión docente/administrador y protección de escritura. Un documento ajeno devuelve 404; una publicación incompleta devuelve 409.
- `POST /api/v1/rag/search` requiere ahora `course`, además de `query`; conserva `top_k` y `min_similarity`. La asignatura se normaliza como en el catálogo.
- `POST /api/v1/content/prepare` también requiere `course`. El modelo y el propietario siguen determinados por el servidor.
- El envío devuelve 422 antes de reservar cuota si una fuente ya no está habilitada o cambió el texto, su procesamiento, su índice o su publicación. Las preparaciones antiguas sin asignatura deben rehacerse.
- La migración `0017_document_publication`, posterior a `0016_document_catalog`, añade una fecha nullable. No habilita materiales antiguos ni elimina datos. La reversión se rechaza mientras existan publicaciones.
- El historial anterior continúa siendo legible: los metadatos nuevos de fuente admiten ausencia. No se reescriben sus prompts ni se les atribuye una publicación retrospectiva.

Ejemplo del cuerpo de búsqueda:

```json
{"course":"Cálculo Diferencial","query":"tasa de cambio instantánea","top_k":3}
```

Para Claude, configurar el modelo exacto acordado y la clave privada, `LLM_DEFAULT_PROVIDER=claude`, `LLM_ENABLED=true` y `LLM_PAID_USAGE_CONFIRMED=true`. La plantilla deja esta confirmación en `false`. Confirmar la capa gratuita de Gemini no habilita gasto en Claude. La cuota informa el mismo estado que usa el envío. El costo de Claude permanece desconocido; no se registra como cero sin una tarifa verificada. No se modificaron archivos privados de configuración.

Los prompts nuevos son `educational-rag-v2` y `educational-rag-profile-v5`. Respetan la asignatura de la solicitud y piden un español claro, cercano y sin elogios automáticos. La revisión humana del resultado sigue siendo necesaria.

## Archivos nuevos: inventario completo

Solo se añaden dos archivos al repositorio:

| Archivo | Por qué es necesario |
|---|---|
| `backend/alembic/versions/0017_document_publication.py` | Evoluciona el esquema sin modificar migraciones ya aplicadas |
| `versionesDM/Version-0.2.md` | Documenta esta versión, su uso, los cambios y la evidencia, como en v0.1 |

El código y las pruebas se ampliaron en sus archivos existentes. No se crearon paquetes vacíos, servicios duplicados, copias de documentos ni informes por cada prueba. La compilación utiliza las carpetas temporales habituales, excluidas de Git.

Archivos existentes modificados, agrupados por responsabilidad:

- Configuración: `.env.example`, `docker-compose.yml` y `backend/app/configuracion/settings.py`.
- Documentos: `models.py`, `schemas.py`, `router.py` y `repositorios/document_repository.py`, dentro de `backend/app/modulos/documentos`.
- RAG: `schemas.py`, `repositorios/search_repository.py`, `repositorios/index_repository.py`, `servicios/search_service.py` y `prompts/educational_prompt.py`.
- Contenidos: `schemas.py`, `adaptation_schemas.py`, `router.py`, `repositorios/generation_claim_repository.py` y los servicios `prepare_content_service.py`, `preparation_service.py` y `generate_preparation_service.py`.
- Interfaz: modelos de documento, búsqueda y preparación; servicios de documentos y búsqueda; pantallas de documentos, búsqueda y preparación con sus pruebas.
- Pruebas backend: fixture de contenido; contratos, adaptación, documentos, búsqueda y generación; integración de catálogo, reserva de generación y recuperación semántica.
- Documentación existente: README de arranque, plan operativo, manual local y bitácora única.

## Verificación

- Backend: 550 pruebas unitarias aprobadas; dos avisos de deprecación de dependencias.
- PostgreSQL/pgvector: 22 pruebas aprobadas de catálogo y reserva de generación. Incluyen aislamiento, publicación, retirada, republicación, índices incompatibles y rechazo de texto cambiado antes de consumir cuota.
- Frontend: 118 pruebas aprobadas en 26 archivos.
- Recuperación con E5 real: una integración adicional aprobada, incluyendo consulta API, fuentes elegibles y retirada.
- Docker: compilación de producción completada; frontend, backend y PostgreSQL saludables. Proxy nginx→FastAPI→PostgreSQL/pgvector verificado y Alembic en `0017_document_publication (head)`.
- Ruff y `git diff --check` aprobados. Las 42 pruebas enfocadas de contratos, preparación y generación también pasaron tras el último ajuste de validación.
- No se realizó revisión visual manual del navegador en esta sesión.
- Las pruebas usan datos sintéticos y rollback; no acreditan aceptación del corpus real.
- No se realizaron llamadas a un LLM externo, integración ADAPTIA ni evaluación pedagógica en esta sesión.

## Qué falta para cerrar

Patricio y los docentes deben recorrer ambas asignaturas con material específicamente autorizado y cotejar las fórmulas y los fragmentos. Después corresponde ejecutar el modelo acordado, conservar su traza y revisar corrección, fuentes, objetivo y apoyo al perfil. El modelo exacto y el presupuesto de Claude deben quedar confirmados antes de activarlo. El contrato de integración se mantiene pendiente de Jefferson y Hernán.

La continuación se conserva en el mismo repositorio. Esta sesión no crea commit, etiqueta ni push.
