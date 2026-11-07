# Versión 0.1 — base documental de TutorIA

Actualizado: 05/11/2026. Responsable de implementación: Patricio Lucero.

## 1. Estado y alcance

La base técnica de v0.1 incorpora carga, validación, extracción, fragmentación, procedencia, permiso declarado, versiones y consulta textual por asignatura. Su cierre académico queda pendiente de demostrar el flujo con material real autorizado y revisar el resultado con el tutor. Las pruebas sintéticas no sustituyen esa aceptación.

Asignaturas confirmadas por Patricio: **Cálculo Diferencial** y **Probabilidad y Estadística**. Esto confirma las materias, no la autorización de documentos concretos. La interfaz las sugiere; no inventa códigos institucionales ni inscripciones ADAPTIA.

Fuentes de alcance:

- Diseño aprobado: `../../DOCUMENTACION/Info/Diseño_Trabajo_Titulación_Lucero_Angel_.pdf`, §9.3.2 y alcance de §8.
- Dirección de integración: `../../DOCUMENTACION/Info/REUNION PATRICIO - ADAPTIA (1).pdf` y `ADAPTIA Onboarding Tesistas (1).pdf`.
- Plan operativo único: `../../DOCUMENTACION/Plan de trabajo/01_plan_de_trabajo.md`, actividades B1–B4.

Este archivo describe la versión solicitada expresamente por Patricio. No sustituye el plan ni crea otra bitácora: la continuidad sigue en `../documentacion-local/BITACORA.md`.

## 2. Requisitos y cumplimiento

| Requisito | Implementación y evidencia | Estado / límite |
|---|---|---|
| Cargar PDF con texto, DOCX y TXT | Validación de extensión, contenido, tamaño y restricciones; pruebas de carga y extracción para los tres formatos | Implementado y probado con muestras sintéticas |
| Conservar original, capa Bronze | Archivo privado identificado por UUID, metadatos y SHA-256; descarga autenticada que comprueba integridad | Implementado; nueva versión no sobrescribe la anterior |
| Extraer, normalizar y segmentar, capa Silver | Servicio de ingesta, extracción aislada y fragmentos PostgreSQL con página/párrafo y posiciones | Implementado; no se añade infraestructura de lago de datos |
| Asignatura y privacidad | Campo normalizado, filtro en listado y búsqueda; sesión, rol docente/administrador y propietario | Implementado para biblioteca local; no es matrícula institucional |
| Origen y permiso | Procedencia, nota de quién autoriza/evidencia, confirmación obligatoria, fecha y propietario que registra | Registra una declaración; la legitimidad del permiso la valida el tutor/docente |
| Versiones documentales | Número, vínculo anterior y UUID independiente; cadena sin bifurcaciones | Implementado con validación y restricción única en BD |
| Consulta textual y fuente | Coincidencias literales por asignatura, paginación, fragmento, versión y acceso al original | Implementado; no necesita embeddings ni llamadas IA |
| Interfaz docente | Formulario, biblioteca filtrable, búsqueda, detalle y creación/consulta de versiones | Pruebas automatizadas aprobadas; revisión con docente pendiente |
| Errores y accesos indebidos | Rechazos de archivos, permisos, propietarios, versiones incompatibles e integridad alterada | Pruebas automatizadas; corpus real pendiente |
| Demostración representativa | Recorrido sintético reproducible y dos asignaturas seleccionadas | Pendiente material autorizado y aceptación del tutor |

No se incluye en el cierre v0.1 la generación final con Claude, la comparación de tres LLM, la publicación Gold ni la integración institucional. Hay código adelantado de v0.2/v0.3 que se conserva, pero su existencia no certifica esos hitos.

## 3. Flujo del docente

1. Iniciar sesión con rol docente en el entorno local. La biblioteca no es un espacio de carga del estudiante.
2. Entrar en documentos y seleccionar archivo PDF con texto, DOCX o TXT de hasta 10 MiB.
3. Escribir título y asignatura; registrar procedencia y quién permite usarlo, con referencia de evidencia/licencia. Confirmar el permiso.
4. Guardar: se conserva el original y se crea el registro con versión 1. Todavía no significa que exista texto procesado.
5. Abrir detalles y procesar: el extractor normaliza texto y publica fragmentos. Si falla, la UI informa el estado; no presenta la carga como procesamiento exitoso.
6. Indicar asignatura y una expresión en «Consultar materiales por asignatura». La búsqueda devuelve coincidencias en documentos propios, procesados, no eliminados y con permiso registrado.
7. Abrir una coincidencia para cotejar página/párrafo, procedencia, versión y original descargado.
8. Para actualizar un material, usar «Cargar nueva versión», escoger el archivo y volver a confirmar el permiso. El sistema conserva el original anterior y vincula ambos registros.

La búsqueda textual ignora diferencias de mayúsculas según la base de datos; no realiza búsqueda conceptual, lematización ni equivalencia automática entre palabras con/sin tilde. `%` y `_` se interpretan como texto, no como comodines.

El catálogo guarda la asignatura con normalización Unicode NFC y minúsculas. Conviene usar las sugerencias para evitar nombres escritos de forma distinta. Este catálogo local deberá mapearse a los identificadores ADAPTIA cuando Jefferson confirme el contrato.

La búsqueda puede mostrar diferentes versiones conservadas; cada resultado indica su número. No presume que una versión nueva revoca automáticamente el permiso de todas las anteriores. La política de vigencia/publicación Gold corresponde al siguiente hito.

## 4. Clases y archivos: qué existía y qué cambió

Rutas relativas a `TutorIA-Lucero`. No se crearon clases de dominio redundantes para cada asignatura.

| Archivo / clase | Situación | Responsabilidad y métodos relevantes |
|---|---|---|
| `backend/app/modulos/documentos/models.py` — `Document` | Existente, ampliada | Metadatos privados; añade asignatura, origen, permiso/fecha y cadena de versiones. Conserva propietario, hash y estados de ingesta/índice |
| `backend/app/modulos/documentos/schemas.py` — `DocumentMetadata` | Nueva | Valida límites, campos vacíos/caracteres de control y normalización de asignatura; recibe vínculo anterior opcional |
| Mismo archivo — `TextMatch`, `TextSearchPage` | Nuevas | Contrato de coincidencia documental y página de resultados con total/límite/desplazamiento |
| Mismo archivo — `DocumentResponse` | Ampliada | Expone metadatos de catálogo y versión, sin exponer configuración privada |
| `backend/app/modulos/documentos/repositorios/document_repository.py` — `DocumentRepository` | Ampliada | `list_owned` filtra asignatura; `search_text` limita por propietario/curso/estado/permiso; `has_next_version` detecta sucesores incluso eliminados |
| `backend/app/modulos/documentos/servicios/document_service.py` — `DocumentService` | Ampliada | `upload` valida propietario/curso de versión anterior, conserva archivos y maneja conflictos; `get` y `delete` conservan controles de propiedad |
| `backend/app/modulos/documentos/router.py` | Ampliado; funciones, no clase | Contrato multipart obligatorio, consulta textual y descarga autenticada; mantiene sesión, roles y protección de escritura |
| `backend/alembic/versions/0016_document_catalog.py` | Nueva migración | Añade columnas, índice por asignatura, FK anterior y unicidad de sucesor; conserva documentos anteriores |
| `frontend/src/app/modulos/docente/documentos/modelos/document.model.ts` | Ampliado | Interfaces `CourseDocument`, `DocumentMetadata` y `TextSearchPage` para representar el contrato |
| `frontend/src/app/modulos/docente/documentos/servicios/document.service.ts` — `DocumentService` | Ampliada | Envía multipart con metadatos, filtra listado y consulta `/text-search` |
| `frontend/src/app/modulos/docente/documentos/paginas/documentos/documentos.ts` — `DocumentsComponent` | Ampliada | `metadataReady`, `newVersion`, `openPrevious`, `searchText`, `resetTextSearch`; cancela consultas obsoletas al cambiar filtros |
| `documentos.html` y `documentos.scss`, misma carpeta | Ampliados | Formulario, asignaturas sugeridas, coincidencias, permiso, versiones y descarga de original |
| `backend/app/modulos/documentos/servicios/document_validation_service.py` — `DocumentValidationService` | Reutilizada | Validación del archivo antes de persistirlo; no se reemplazó por validación exclusiva del navegador |
| `backend/app/modulos/rag/servicios/ingest_document_service.py` — `IngestDocumentService` | Reutilizada | Coordina extracción aislada y publicación de fragmentos; diferencia estados y fallos |
| `backend/app/modulos/rag/servicios/document_text_service.py` | Reutilizado | Extracción/normalización del texto y referencias de origen |
| `backend/app/modulos/rag/repositorios/chunk_repository.py` — `ChunkRepository` | Reutilizada | Persistencia y consulta paginada de fragmentos |
| `backend/app/modulos/rag/models.py` — `DocumentChunk` | Reutilizada | Texto Silver, documento, posición, página/párrafo y referencias; embeddings son una capacidad posterior |

Los cambios anteriores de reorganización Docker/configuración permanecen en el árbol de trabajo. No deben confundirse con clases nuevas de v0.1 ni añadirse ciegamente al mismo commit.

## 5. API de esta versión

Prefijo `/api/v1`. Requiere sesión válida; gestión restringida a docente/administrador y al propietario. Las escrituras conservan la protección de cliente/CSRF existente.

| Método y ruta | Entrada / salida |
|---|---|
| `POST /documents/upload` | Multipart: `file`, `title`, `course`, `source_reference`, `permission_note`, `authorization_confirmed=true`; opcional `previous_version_id`. Devuelve 201 y metadatos |
| `GET /documents` | `course` opcional, `limit`, `offset`; devuelve documentos propios no eliminados |
| `GET /documents/{id}` | Detalle privado con origen, permiso, hash, estados y versiones |
| `POST /documents/{id}/process` | Extrae y segmenta el documento; devuelve estado y cantidades |
| `GET /documents/{id}/chunks` | Fragmentos paginados del documento propio |
| `GET /documents/text-search` | `course` y `q` obligatorios; `limit` 1–50, predeterminado 20, `offset >= 0`; devuelve `items`, `total`, `limit`, `offset` |
| `GET /documents/{id}/original` | Descarga adjunta del archivo con SHA-256 verificado; no-store y nosniff |
| `DELETE /documents/{id}` | Retirada explícita ya existente: marca registro eliminado, borra fragmentos y archivo de esa versión |

Errores relevantes: 422 metadatos/confirmación inválidos; 403 rol o protección de escritura; 404 documento ajeno/no disponible; 409 conflicto de versión o integridad del original; 413 tamaño excesivo. Las restricciones específicas del archivo conservan los errores de validación existentes.

Ejemplo de consulta, desde cliente con sesión:

```text
GET /api/v1/documents/text-search?course=C%C3%A1lculo%20Diferencial&q=derivada
```

No se incluyen cookies, tokens ni claves en este documento.

## 6. Datos, versiones y compatibilidad

- Migración anterior: `0015_resource_assignments`. Nueva: `0016_document_catalog`.
- Los documentos anteriores conservan sus IDs y archivos. Quedan sin asignatura/origen/permiso registrado; no se inventa autorización retrospectiva.
- La búsqueda nueva excluye esos documentos hasta que exista una versión clasificada con permiso. Para incorporarlos, descargar el original y cargar una nueva versión con datos reales; no se modifica silenciosamente el historial.
- `version_number` es la versión documental. `processing_version` identifica procesamiento; no son equivalentes.
- Cada padre admite un único sucesor. La BD protege también frente a cargas concurrentes; ante conflicto se revierte la transacción y se limpia el archivo nuevo.
- Retirar una versión no permite reutilizar su número ni abrir otra rama desde el mismo padre. La política futura de restauración/revisión de versiones retiradas necesita acuerdo.
- Crear una versión conserva originales anteriores. El botón eliminar sigue siendo una retirada explícita y elimina el archivo elegido; no es un archivo histórico inmutable ni un respaldo.
- La migración impide una reversión que descartaría metadatos de catálogo existentes. No se ejecutó downgrade ni se eliminaron volúmenes.
- Las claves continúan exclusivamente en `licencias/secure_data.env` para Docker y `licencias/backend.env` para ejecución directa, excluidas de Git e imágenes. `.env.example` sigue siendo una plantilla sin secretos.

## 7. Verificación

Pruebas locales del 05/11/2026:

- Backend: **542 pruebas unitarias aprobadas**. Dos avisos de deprecación de dependencias; no son fallos.
- Frontend: **107 pruebas aprobadas en 23 archivos**, incluida cancelación de búsquedas al cambiar asignatura.
- Compilación TypeScript de aplicación y pruebas sin errores antes del ajuste final de cancelación; ese ajuste también fue compilado por Angular al ejecutar las pruebas.
- Pruebas de catálogo: metadatos obligatorios, confirmación, dos materias de un propietario, aislamiento entre propietarios/roles, coincidencias literales, paginación, versiones, originales y exclusión tras eliminación.
- PDF, DOCX y TXT generados en memoria recorren carga→extracción→búsqueda→descarga. Son muestras sintéticas, no corpus aprobado.
- **Una prueba de integración PostgreSQL aprobada**: `backend/tests/integracion/test_document_catalog.py`, con extracción real, aislamiento y restricción única. Usa transacción exterior con rollback y archivos temporales.
- Docker: backend, frontend y PostgreSQL saludables; nginx→FastAPI→PostgreSQL/pgvector verificado; frontend HTTP 200; Alembic `0016_document_catalog (head)`. Construcción de aplicación completada. No se realizó una revisión visual manual del navegador.

Archivos de regresión principales: `backend/tests/unitarios/test_documents.py`, `backend/tests/integracion/test_document_catalog.py` y `frontend/src/app/modulos/docente/documentos/paginas/documentos/documentos.spec.ts`.

Comandos reproducibles desde la raíz, sin copiar secretos:

```powershell
Set-Location backend
../.venv/Scripts/python.exe -m pytest tests/unitarios -q -p no:cacheprovider
Set-Location ../frontend
npm test -- --watch=false
Set-Location ..
docker compose --env-file licencias/secure_data.env up -d --build --wait
docker compose --env-file licencias/secure_data.env -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --rm --build test-backend pytest tests/integracion/test_document_catalog.py -q -p no:cacheprovider
```

No se hicieron llamadas de pago a LLM ni se conectó CAS/ADAPTIA real para validar v0.1.

La construcción de la imagen de pruebas separada se interrumpió por la descarga lenta de dependencias. La integración se ejecutó correctamente en un contenedor efímero de la imagen backend ya construida, con tests y librerías de pytest locales montados en solo lectura; las dependencias de aplicación fueron las de Linux de la imagen. Comando efectivamente verificado desde esta instalación:

```powershell
docker compose --env-file licencias/secure_data.env run --rm --no-deps -e RUN_DB_TESTS=1 -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -v 'C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero/.venv/Lib/site-packages:/testlibs:ro' -v 'C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero/backend/tests:/app/tests:ro' -v 'C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero/backend/pyproject.toml:/app/pyproject.toml:ro' backend python -c "import sys; sys.path.append('/testlibs'); import pytest; sys.exit(pytest.main(['tests/integracion/test_document_catalog.py','-q','-p','no:cacheprovider']))"
```

## 8. Pendientes para cerrar con material real

| Responsable | Qué debe cumplir | Evidencia de cierre |
|---|---|---|
| Patricio y tutor/docentes | Seleccionar archivos representativos de Cálculo Diferencial y Probabilidad y Estadística, con permiso específico | Relación de archivos, autor/procedencia y evidencia de autorización |
| Patricio | Ejecutar el flujo de carga, proceso, búsqueda y cotejo para ambas materias | Resultados correctos y fuentes reconocibles; sin mezcla de asignaturas |
| Patricio y tutor/docentes | Revisar extracción de fórmulas, símbolos, tablas y expresiones reales | Cotejo con original; errores o formatos no admitidos registrados, no ocultos |
| Tutor/docentes | Revisar la utilidad y fidelidad del material recuperado | Aceptación explícita o correcciones identificadas |
| Patricio | Revisar cambios, excluir privados y preparar commit/release | Pruebas verdes, diff revisado, sin secretos; cierre académico reflejado con honestidad |
| Jefferson | Confirmar identificadores institucionales y política de permisos/contrato para integración | Acuerdo antes de conectar el catálogo local con ADAPTIA; no bloquea prueba local sintética |

Limitaciones actuales: PDF escaneado requiere OCR externo previo; no se implementó OCR. DOCX con OfficeMath y ciertos estilos matemáticos heredados puede rechazarse por el extractor. Las pruebas sintéticas no prueban que todas las fórmulas de las asignaturas se preserven. Si el corpus autorizado usa estos formatos, resolver esa incompatibilidad será necesario antes de aceptar v0.1.

La recuperación semántica adelantada todavía necesita adaptar asignatura, permisos y vigencia en v0.2. La separación demostrada aquí corresponde a la biblioteca y recuperación textual; no se atribuye automáticamente al contexto del LLM.

## 9. GitHub y siguientes versiones

Recomendación: conservar el repositorio actual y su historial. Una vez revisado el cambio, puede publicarse como candidato v0.1; reservar el cierre definitivo para la aceptación con corpus real. Después continuar con v0.2 en el mismo repositorio usando commits, ramas y etiquetas.

Abrir otro repositorio solo para continuar versiones duplicaría mantenimiento e historial. Un repositorio institucional ADAPTIA sí puede tener sentido si Jefferson lo exige como destino del módulo; esa entrega es una decisión distinta y requiere confirmar el contrato.

El árbol actual contiene capacidades adelantadas de v0.2/v0.3. Una etiqueta v0.1 señalaría el hito verificado, no afirmaría que todo el árbol pertenece exclusivamente a esa versión. No se eliminan capacidades adelantadas para fabricar una separación artificial.

No se creó repositorio, commit, etiqueta ni push automáticamente. Revisar el bloque de catálogo/migración/frontend/pruebas y este documento para un commit humano sugerido: `feat: completar base documental de v0.1`. Revisar por separado la reorganización previa de configuración y Docker. No incorporar la bitácora ni archivos privados a Git.
