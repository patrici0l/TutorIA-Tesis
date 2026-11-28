# Versión 0.3 — avance local

19/11/2026. Rama `feature/v0.3-ejemplos-pistas`, basada en `362334c`.
Este avance no declara cerrada la v0.3. Jefferson continuará sus cambios en otras
ramas; antes de unirlos corresponde revisar posibles cruces.

## Actualización local del 25 de noviembre

El docente puede abrir la preparación desde un escenario de G3 o G24. El tema, objetivo,
tipo de recurso y dificultad llegan como propuesta editable. La preparación conserva el
paralelo, escenario y selección de fuentes en el snapshot JSON existente.

El selector permite recuperar materiales propios habilitados de la materia o incluir
también artículos importados de Wikipedia. La comparación prepara el mismo caso sin
documentos, con material docente y con material docente más Wikipedia. Muestra los
fragmentos recuperados por condición. La medición de calidad, costo y tiempo de
respuestas reales continúa pendiente. CORE y la habilitación por correo descritos
en las entradas históricas ya no forman parte del flujo docente de simulación.

## Implementado

- Ejemplo resuelto independiente (`EXAMPLE`): enunciado, pasos y resultado.
- Pista independiente (`HINT`): enunciado y una a tres ayudas, sin campos de solución.
  El problema se indica en el tema y objetivo. El prompt pide no revelar el resultado;
  el validador estructural no certifica que una frase no lo revele: revisar el contenido.
- Selección en preparación docente, presentación con fuentes e identificación en historial.
- Contratos de actividades actualizados para guardar, asignar y consultar ambos tipos.
- Contratos de generación directa y preparación experimental ampliados a seis recursos.
- Prompts versionados: RAG v3, RAG con perfil v6, directo v2 y pares experimentales v2.
  Los recursos y prompts históricos guardados no se reescriben.
- [Guía y JSON para Jefferson](../docs/api/README.md): flujo actual de preparación y
  generación, respuestas simuladas, errores, sesión y prueba local.

Los nuevos tipos de recurso conservan el almacenamiento JSON existente.
La conexión externa añade la migración `0018_external_sources` para guardar procedencia
estructurada; no reclasifica documentos anteriores ni modifica sus permisos.
Los cuatro tipos anteriores conservan su estructura, incluidos los ejemplos dentro
de explicaciones y las pistas dentro de ejercicios.

## Conexión real con Wikipedia en español

Desde **Documentos → Buscar fuentes externas**, el docente busca un tema, revisa una
versión del artículo y confirma su incorporación a una asignatura. Se guarda como TXT
adaptado, con enlace permanente, versión, fecha, licencia y atribución. La captura JSON
original de MediaWiki (HTML y wikitext) se conserva junto al documento y se puede
descargar desde su sección de origen; ambas copias tienen huellas de integridad.

El material llega sin procesar ni habilitar. Se utiliza el flujo existente de proceso,
índice, revisión y habilitación. La búsqueda y preparación conservan su procedencia
externa; la retirada impide nuevas recuperaciones. Los respaldos de la carpeta de
materiales incluyen también las capturas originales. Eliminar expresamente el material
elimina ambos archivos.

La importación vuelve a consultar la revisión elegida y comprueba que el texto coincide
con el revisado. Solo se consulta el host fijo de Wikipedia en español, sin seguir
redirecciones ni aceptar direcciones del navegador. Hay límites de tiempo, tamaño y
consultas por docente. Las fórmulas MathML compatibles se convierten a TeX; una fórmula
no compatible bloquea la importación. Se omiten imágenes, multimedia y bloques de
navegación; la revisión humana de fórmulas, tablas y contenido sigue siendo necesaria.

Cada importación crea un documento independiente; no se actualiza automáticamente ni
se deduplican importaciones repetidas. La revisión fijada y las copias conservadas
permiten identificar qué texto se usó aunque Wikipedia cambie.

## Verificación al 19 de noviembre

- Backend: 590 pruebas unitarias aprobadas y una omitida; dos avisos de deprecación.
- PostgreSQL: 73 pruebas de integración aprobadas y dos omitidas, en una base temporal
  separada con las migraciones aplicadas hasta `0018_external_sources`.
- Frontend: 169 pruebas aprobadas en 30 archivos; compilación Angular y Ruff aprobados.
- Consulta real de los artículos Derivada y Distribución normal, con revisión, licencia
  y texto matemático recuperados.
- Un E2E real aprobado después del ajuste visual final: búsqueda → revisión → importación
  de Derivada → captura original → extracción → índice E5 real → habilitación → RAG →
  preparación → retirada. También comprueba exclusión antes de publicar y tras retirar.
- Capturas revisadas en escritorio y móvil; sin desbordamiento horizontal a 390 px.
- Pruebas negativas: roles, propietario, cabecera, falta de confirmación, texto alterado,
  tamaño excesivo, errores remotos, tiempos de espera y captura original modificada.
- Los JSON de ejemplo para Jefferson siguen siendo simulados, validados contra contratos.

Se consultó Wikipedia realmente; no se hicieron llamadas a modelos generativos. La
prueba utilizó una asignatura de prueba y retiró/eliminó el material al finalizar.
La primera verificación se hizo en servicios temporales. El 19 de noviembre se actualizaron
los contenedores habituales y la base nativa hasta `0018_external_sources`, con respaldo.
No se realizó despliegue público.

## Solicitudes del estudiante y revisión UX del 20 de noviembre

- **C1 implementado y probado técnicamente:** seis recursos solicitables por el estudiante,
  preparación sin llamada LLM, envío explícito, cupo compartido, historial privado por cuenta.
- Nuevo permiso local por docente, estudiante y asignatura (`0019_student_content`).
  El profesor lo concede por correo desde **Acceso de estudiantes**. No se infiere la
  matrícula ni se comparte todo el corpus por coincidir el nombre de una materia.
- Fuentes recuperadas solo del docente concedente y la materia autorizada; la preparación
  pertenece al estudiante. El servidor rechaza cambios de docente, materia o perfil en
  el JSON. Revalida permiso y fuentes al enviar, incluso en preparaciones anteriores.
- Retirar permiso o fuente bloquea nuevas solicitudes; el historial ya guardado se conserva.
  Ejercicios/cuestionarios son de autoestudio: no se promete secreto de sus soluciones.
- **UX de Wikipedia revisada:** pasos de incorporación visibles, mensajes diferentes al
  buscar/revisar/guardar, licencia consultable del artículo real y botones identificables
  por lectores de pantalla. Se conservaron los ajustes visuales existentes del usuario.
- Pantallas de estudiante y acceso docente adaptadas a escritorio/móvil. La cuenta de
  demostración avisa que se comparte por rol y muestra el correo que se necesita para dar acceso.
- **Word actualizado:** filas 2 y 6 como cumplidas técnicamente, fila 1 implementada y
  filas pendientes conservadas. Incluye una tercera página con instrucciones y límites.

Verificación: 590 unitarias backend aprobadas y 1 omitida; 82 de integración PostgreSQL
aprobadas y 2 omitidas; 172 frontend aprobadas. Ruff y compilación Angular correctos.
Dos E2E: Wikipedia real (importar, indexar, publicar, recuperar y retirar) y estudiante
(conceder acceso, preparar con E5 real, reabrir y retirar acceso), sobre una base temporal.
Los seis tipos recorrieron generación y persistencia con un proveedor simulado en tests:
no se consumió cuota de IA ni se acredita calidad pedagógica con esas pruebas.

Instalación habitual actualizada el 20 de noviembre: Docker reconstruido y saludable,
base Docker y base nativa en `0019_student_content`. Respaldo previo completo de Docker
verificado mediante restauración temporal; también se respaldó la base nativa antes
de migrarla. Las claves y la habilitación del proveedor se conservaron. No se publicaron
servicios en Internet ni se concedieron accesos de estudiantes automáticamente.

## CORE y aprobación de materiales y accesos — 23 de noviembre

- [x] Consulta real a CORE: cinco resultados, ficha, autores, año, idioma y resumen.
- [x] Incorporación del original PDF/DOCX/TXT por el profesor, permiso explícito,
  copia de la ficha con hash y procedencia conservada. No se importa el resumen como
  artículo ni se descargan enlaces arbitrarios. El material queda privado e inhabilitado.
- [x] Revisión antes de habilitar: texto, búsqueda y permiso visibles; confirmación
  docente de los fragmentos, fórmulas y adecuación a la materia.
- [x] Gestión de acceso por correo y materia con búsqueda, filtros y confirmación
  de retirada dentro de cada registro. Se aclara el alcance sobre materiales futuros.
- [x] Estudiante: procedencia de fuentes visible, estado de consulta del cupo y
  copia de correo con confirmación solo cuando funciona.
- [x] Word y guía actualizados. Login, despliegue público y rama del tutor sin cambios.
- [ ] Descarga automática de texto completo de CORE. La API pública probada responde
  que no está disponible; esta integración requiere adjuntar el original autorizado.
- [ ] Aceptación pedagógica de las publicaciones para las dos materias y el piloto.

Verificación: 603 pruebas unitarias backend aprobadas (1 omitida), 82 de integración
PostgreSQL (2 omitidas), 181 frontend; Ruff y compilación correctos. Dos E2E aprobados
sobre base temporal: CORE real con original sintético y revisión/publicación explícita;
acceso y solicitud del estudiante con recuperación E5 real y retirada. La muestra
sintética prueba el circuito técnico, no representa ni valida una publicación académica.
Se revisaron capturas de escritorio y móvil. No se hicieron llamadas generativas.

## Pendiente

Login institucional y despliegue se revisarán con el tutor. Continúan pendientes los
acuerdos ADAPTIA, vinculación del perfil del estudiante y matrícula institucional, ejecuciones
comparables de tres modelos, selección y aceptación del corpus externo y piloto de ambas
asignaturas. Falta el selector experimental entre fuentes docentes y docentes más externas;
por ahora RAG usa todas las fuentes propias habilitadas de la materia. OpenAlex y
Wolfram Alpha no están integrados. CORE permite buscar fichas e incorporar el original
adjuntado por el docente; la descarga automática de texto completo no está implementada.
La aceptación docente de v0.2 sigue separada del cierre técnico marcado en Git.

Instalación local del 23 de noviembre: imágenes Docker reconstruidas; interfaz,
API, PostgreSQL y pgvector saludables en localhost:4200. Respaldo previo completo
verificado mediante restauración temporal. No se requirieron migraciones nuevas.
La ejecución nativa de Angular que ocupaba 4200 se detuvo para dejar una sola
interfaz local. Los comandos nativos del README siguen disponibles.
