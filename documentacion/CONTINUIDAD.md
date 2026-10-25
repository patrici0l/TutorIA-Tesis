# Continuidad de TutorIA-Lucero

## 25 de octubre — acceso sin navegación redundante

Solicitud del autor a partir de captura: retirar Explorar en el acceso, donde solo
repetía Entrar. App crea la navegación únicamente con usuario de sesión; al cerrar
o perder sesión se retira la barra completa. Eliminado destino /login del menú sin
sesión. Conservados destinos de docente/estudiante, diálogo y acceso por perfiles.
Guía de navegación actualizada. Sin cambios de autenticación, backend o datos.

Validación: siete pruebas aprobadas en app.spec.ts y nav.spec.ts; cubren ausencia
sin sesión, presencia por ambos roles, retirada al perder sesión y comportamiento
del diálogo/destinos. TypeScript app/spec sin errores; Prettier aplicado a los tres
TS afectados y git diff --check correcto. Ejecución inicial de tests detenida tras
espera del entorno; repetición con configuración temporal de dos workers y threads
aprobada (32,67 s); configuración retirada. Sin nueva revisión visual en navegador.
Rama feature/resource-preparation, anterior commit humano 06b848b verificado.
Revisión solicitada por el autor completada: siete pruebas aprobadas nuevamente, TypeScript app/spec sin errores y git diff --check correcto. Commit autorizado expresamente con mensaje `ocultar explorador antes de iniciar sesión`.
Próximo: revisión visual móvil/escritorio del acceso y flujo por roles. El problema
previo de push por modelo grande permanece fuera del alcance de este cambio; no
se reescribió el historial de Git.

## 25 de octubre — plan consolidado y comentarios de código

Solicitud del autor: PDF con todas las fases, estados, evidencias y próximos pasos,
y comentarios profesionales breves en el código. Inicio desde commit humano
`0c27a91`, rama `feature/resource-preparation`, árbol limpio verificado.

Creado PLAN_ACTUAL.md como fotografía editable: 16 etapas originales, correspondencia
con 12 hitos, ampliaciones del MVP, 25 referencias E01-E25 y seis bloques N1-N6
propuestos. Diferencia cumplimiento técnico, datos sintéticos, pilotos, validación
académica, exclusiones y condicionales. No inventa porcentajes, fechas de ejecución,
aprobación ni resultados nuevos. Ajustados seguimiento histórico, arquitectura y
README para retirar contradicciones sobre proveedores, rutas y generación vigente.
PDF de diez páginas en output/pdf/plan_trabajo_tutoria_2026-10-25.pdf, fuente editable
y exportador reproducible infraestructura/scripts/export-work-plan.py (ReportLab).

Comentarios añadidos/ajustados en 95 archivos: 60 Python y 35 TypeScript. Describen
responsabilidad y reglas no obvias, con pocas notas locales de seguridad, cuota,
idempotencia y ciclo del interceptor. Sin cambios de lógica. Equivalencia comprobada
con AST Python en 138 módulos y representación TypeScript sin comentarios en 69
archivos. El primer comparador léxico TS detectó solo normalización CRLF dentro de
plantillas; sustituido por comparación mediante el parser/impresor TypeScript.
Ruff backend y exportador aprobados. No se repitieron suites funcionales por
comentarios/documentación; los resultados de tests del PDF son históricos por bloque.

Verificación documental: 48 referencias locales presentes; 16 etapas y catálogo
E01-E25 completos. PDF renderizado con Poppler y revisado visualmente en todas sus
páginas; corregidos desborde final y anchuras de columnas. Numeración 1-10 y límites
de texto comprobados por extracción. Sin llamadas IA, CAS ni cambios de servicios.
Pendiente de revisión y commit humano de este bloque, incluido el PDF. Mensaje:
`docs: consolidar plan con evidencias y comentar reglas del código`.
Próximo: N1 revisión visual del MVP cuando el navegador esté disponible, acordar N3
protocolo académico y delimitar N2 seguimiento como ampliación antes de implementarla.

## 25 de octubre — continuación de limpieza

Rama `feature/resource-preparation`. Ampliadas exclusiones en los contextos Docker
propios del backend (producción y pruebas): logs, cobertura, uploads y modelos
locales. El contexto raíz del frontend también excluye backend/models, 487 351 240
bytes que no forman parte de sus COPY. Modelo y tokenizer permanecen en disco;
Compose conserva el volumen embedding_data. README corregido para reflejar los
accesos Profesor/Estudiante y el resumen de disponibilidad vigente.

Verificación estática de entradas COPY en los tres Dockerfiles: presentes y no
excluidas; git diff --check correcto. No se construyeron imágenes ni se ejecutaron
suites: cambios limitados a documentación y exclusiones de archivos no copiados.
Limpieza previa conservada. Pendiente de revisión y commit humano:
`chore: limpiar archivos vacíos y documentación redundante`.
Próximo: revisión visual del flujo docente cuando el navegador esté habilitado.

## 24 de octubre — limpieza del repositorio

Commit humano anterior verificado: `2094121`. Rama `feature/resource-preparation`.
Retirados 37 .gitkeep redundantes o de carpetas frontend sin implementación; seis
carpetas frontend vacías retiradas. Cinco directorios generados enviados a Papelera:
.pytest_cache y .ruff_cache de raíz/backend, y frontend/dist (4 333 400 bytes).
La aprobación automática rechazó el borrado masivo inicial; la limpieza de directorios
se completó de forma recuperable. Dependencias, caché Angular del servidor activo,
logs activos, modelos, secretos, respaldos y evidencias académicas conservados.

Guía de navegación reducida a la implementación vigente, con referencia al historial
Git; retirada tabla de renombres ya concluidos del README frontend. Docker excluye
cachés de pruebas, metadatos regenerables, informes y logs del contexto de construcción.
Verificación: 170 referencias locales sin faltantes y git diff --check correcto;
las 37 eliminaciones versionadas son únicamente archivos vacíos. Sin cambios de
código ejecutable ni nuevas suites/build para no regenerar los residuos limpiados.
Pendiente de commit humano: `chore: limpiar archivos vacíos y documentación redundante`.
Próximo: revisión visual del flujo docente cuando el navegador esté habilitado.


## 24 de octubre — coherencia del recorrido docente

Rama `feature/resource-preparation`. Portada docente organizada en materiales,
recursos y asignación/seguimiento, con un único acceso a actividades. Menú con el
mismo orden; perfiles quedan como personalización opcional y las métricas se
identifican como Uso de generación, diferenciadas del seguimiento estudiantil.

Documentos explica extracción y preparación para buscar fuentes, enlaza a Recursos
al estar indexado y pliega reconstrucción/modelo bajo mantenimiento. Recursos coloca
el formulario básico antes de personalización, las fuentes antes de Generar y el
historial después del resultado; retira el botón de generación al terminar. Se
conservan fuentes, citas, trazabilidad, exportación y controles de cupo/errores.
Actividades distingue ejercicios autocorregidos de materiales con soluciones,
identifica el recurso seleccionado y oculta su resumen al cambiar a un banco fijo.
Retirado el desvío docente a práctica libre desde el estado vacío. Los materiales
no registran lectura ni respuestas; esto se explica sin presentar métricas ficticias.
Guía vigente: manuales/flujo_docente.md. Conservados nombres cortos y logo del autor.

Validación: build producción aprobado, inicial 327.08 kB sin advertencias; TypeScript
app y spec aprobados. Suite de 23 archivos: 100/101 iniciales; corregida la nueva
prueba para cambiar el select mediante su evento real y verificados 6/6 casos del
archivo de actividades. 101 casos distintos aprobados en conjunto. La otra prueba
nueva comprueba fuentes antes de generar y ausencia de reenvío al abrir un recurso
finalizado. Para sortear demoras de instrumentación local se usó WALLABY_ENTRY=1
y configuración temporal Vitest con dos workers, sin paralelismo de archivos y pool
threads; retirada al terminar. No se alteraron extensiones ni ajustes del equipo.

Revisión visual pendiente: el navegador local está deshabilitado en Work. No se
consumió IA ni se escribieron datos reales; backend y DB sin cambios. Pendiente de
commit humano. Revisar frontend del recorrido docente y su documentación; mensaje
sugerido: `feat(ui): ordenar el flujo docente de materiales a actividades`.
Próximo: revisión visual del recorrido en navegador cuando esté disponible y
continuar seguimiento por tema/filtros según el plan.


## 24 de octubre — nombres cortos en componentes frontend

Solicitud del autor: nombres como `login.html`, sin `.component`, y limpieza de
restos de elementos retirados. Renombrados los 72 archivos de 18 componentes,
incluidos TS/HTML/SCSS/spec; nueve nombres compuestos/largos reducidos a nav,
resolve, chunks, prepare, view, history, audit, export y quota. Actualizados imports,
rutas lazy, arranque, referencias a plantillas/estilos y pruebas. Clases, selectores
y URLs conservados. Generador Angular configurado sin sufijo de componente; criterio
y equivalencias en frontend/README.md.

Limpieza: estilos huérfanos tag/mock-notice/notice-dot, quick-links y domain, y
metadatos icon que ya no usa el menú. Conservados logo UPS y cambios visuales del
autor. El estado inicial ya compilaba y pasaba 99 pruebas; no se detectaron errores
de componentes ausentes ni se restauraron elementos eliminados.

Verificación final: build producción sin advertencias, 99/99 pruebas en 23 archivos,
TypeScript sin imports/parámetros locales sin uso; comprobadas 134 referencias
relativas y 36 plantillas/estilos sin archivos faltantes. Generador revisado en
simulación sin crear archivos. Sin cambios backend, base de datos ni llamadas IA.
Rama feature/resource-preparation, pendiente de commit humano. Revisar renombres,
limpieza y documentación; mensaje sugerido:
`refactor(frontend): acortar archivos de componentes y limpiar estilos huérfanos`.
Próximo: continuar la revisión funcional de UI según el plan.


## 24 de octubre — menú lateral y renderizado matemático

Rama `feature/resource-preparation`. Solicitud UI/UX implementada: Explorar abre
un menú lateral modal nativo, sin carrusel ni segunda lista de destinos. Cierre
por botón, fondo, Escape y navegación; foco restaurado, fondo inerte, desplazamiento
del fondo bloqueado y movimiento reducido respetado. Portada sin enlaces secundarios
redundantes; se conservan cambios previos del autor en cabecera y pie.

Conceptos separados: Actividades asignadas (ejercicios/materiales del docente) y
Práctica libre (repaso voluntario e historial personal). Rutas y persistencia intactas.
KaTeX y CSS/fuentes empaquetados localmente; importación estática antes de crear las
vistas matemáticas. Directiva síncrona para texto de recursos y ejercicios, incluidos
quiz, soluciones y revisión; actualiza al cambiar entradas. Admite $, $$, \( y \[;
texto como textContent, trust=false y errores tolerados, sin habilitar HTML externo.

Pruebas: 34/34 iniciales en siete archivos; tras nueva prueba de quiz y orden de
menú, 11/11 en los tres archivos afectados (35 casos distintos en total). Build
producción aprobado, inicial 327.05 kB sin advertencias. Navegador local: acceso
docente, menú abierto, Escape/foco y navegación Inicio comprobados visualmente.
No había recursos guardados en la base local; fórmulas verificadas con fixtures,
sin consumir IA. No se ejecutó una matriz completa de tamaños/dispositivos.

Pendiente de commit humano. Revisar frontend y documentación de este bloque sin
incluir LICENSE, modelos ni cambios previos ajenos. Mensaje sugerido:
`feat(ui): simplificar navegación y renderizar fórmulas con KaTeX`.
Próximo: revisar visualmente un recurso real cuando exista en la base local;
continuar seguimiento por tema y filtros de actividades según el plan.


## 24 de octubre — ejecución local sin contenedores

PostgreSQL 18 de Windows reutilizado con base y rol dedicados `tutoria_localdev`;
pgvector disponible y migraciones aplicadas hasta 0015. Credenciales únicamente en
`backend/.env`, fuera de Git. Bases preexistentes conservadas. Angular arrancado con
proxy local y FastAPI con recarga; health directo y por proxy: API/DB/pgvector OK.
Modelo E5 descargado y verificado en `backend/models/e5-small`. Sesiones mock docente
y estudiante verificadas por HTTP local. Rama `feature/resource-preparation`.
Próximo: continuar desarrollo local; los datos Docker no se importaron.


## 24 de octubre — generación, asignación y mensajes

Solicitud del autor: corregir recursos de integrales y su asignación; limpiar avisos de
prueba y mostrar disponibilidad, con ajustes básicos de interfaz. Rama
`feature/resource-preparation`; cambios anteriores de demo remota conservados.

Causas comprobadas: el quiz de integrales terminó en `llm_incomplete` con máximo de
512 tokens y 508 tokens de salida; Gemini usa ese código para `MAX_TOKENS`. Además,
la asignación solo aceptaba bancos fijos de derivadas y no tenía vínculo con recursos.

Implementado: migración 0015 con resource_id nullable y FK/check; asignación de recursos
propios succeeded como material de estudio con fuentes/soluciones, sin calificación;
se mantienen los bancos autocorregidos. El detalle del alumno no expone prompts,
perfiles, consumo ni historial privado. Preparar → generar → asignar conectado por enlace.
Avisos de demostración/cuenta de prueba retirados; confirmaciones y errores conservados.
Personalización opcional plegable y pasos visibles. Cupo diario compartido con solicitudes
restantes, porcentaje consumido, reinicio y máximo de salida; actualización tras generar.
No inventa tokens restantes del proveedor ni porcentaje de una generación en curso.
Rechazos previos de cupo/configuración permiten reintentar la misma preparación.

Configuración: máximo de salida predeterminado 4096 (dentro del rango existente) y ajuste
puntual de esa variable en .env local; cupo 5/día y timeout 30 s conservados. No se
imprime ni versiona .env. Históricos guardan sus límites originales.

Pruebas finales: 97 Angular y 91 backend/PostgreSQL aprobadas; una omitida en contenedor
por fuentes Angular ausentes, comprobada localmente (14/14). Build y Ruff correctos.

Prueba real local por HTTP: mismo quiz de integrales de cinco preguntas generado,
validado y persistido; 1789 tokens entrada, 637 salida, total 2426. Asignado y abierto
con sesión estudiante, contenido/fuentes iguales; CSRF, permisos, idempotencia y logout
comprobados. Cupo real pasó de 4 a 3 restantes de 5 (una nueva llamada Gemini).
Migración aplicada y servicios reconstruidos/actualizados sin borrar datos.

Limitaciones: material generado compartido para consulta, sin evaluación dinámica ni
seguimiento de lectura; saldo del proveedor no disponible. Navegador verificó login,
inicio y recursos sin el banner; después Work deshabilitó el uso del navegador y no
se pudo cerrar revisión visual del último ajuste. Ver evidencia y comandos en
pruebas/revision_integrales_asignaciones.md. Pendiente revisión y commit humano;
no se ejecutó git commit. Alcance sugerido: generación/cupo, asignación de recursos,
interfaz, migración y pruebas/documentación de este bloque. Mensaje sugerido:
`fix: corrige generacion y asignacion de recursos y muestra cupo disponible`.

## 23 de octubre — demo pública sin correos

Instrucción vigente del autor: cualquiera con el enlace puede entrar por los botones
Profesor/Estudiante, sin correo ni PIN. Reemplaza la propuesta anterior protegida por
correo. Scripts de inicio y cierre ajustados; enlace actual guardado únicamente en
secretos_locales/demo-remota/enlace.txt. Manual y decisión SSO actualizados.

Verificación real: túnel HTTPS público creado; salud, login de ambos roles, sesiones,
CSRF (rechazo sin cabecera), logout y rechazo tras logout comprobados por HTTP remoto.
Navegador: pantalla de acceso sin correo y botón Profesor condujo al espacio docente;
recarga en Documentos conservó sesión. Cierre real del túnel y restauración del login
local comprobados. Se vuelve a iniciar para entregar enlace activo al autor.
Las 58 pruebas backend del bloque previo se conservan; no se modificó el backend en
este ajuste de scripts y documentación. Sin nuevas llamadas IA ni cambios de límites.

Limitaciones: equipo encendido/sin suspensión, dominio temporal, perfiles y datos
compartidos por rol, cualquier visitante puede usar las funciones de ambos perfiles.
No se habilita CAS ni cuentas institucionales; no equivale a evaluación académica.
Rama feature/resource-preparation. Pendiente revisión y commit humano de configuración,
pruebas, scripts y documentación de demo. Mensaje sugerido:
`feat: habilita demo publica temporal con perfiles de prueba`.
Próximo: compartir enlace con profesor y recoger observaciones; cerrar al terminar.

## 12 de octubre — Explorador privado del código

Creado HTML privado estilo editor en guia_personal/explorador.html: árbol de carpetas,
pestañas, búsqueda por contenido/símbolos, código numerado y explicación junto al archivo.
Incluye 305 archivos y 869 estructuras del inventario; campos, parámetros, herencia,
llamadas y pasos extraídos enlazan con el código. Prueba DOM recorrió todos los archivos
 y estructuras, búsqueda y enlaces a líneas: aprobada. No se realizó revisión visual
 del HTML en navegador. Lectura estática orientativa, sin secretos ni dependencias copiadas.
Enlaces incorporados en ambas guías anteriores; carpeta ignorada por Git/Docker.
Sin cambios de aplicación, DB ni despliegue. Rama feature/resource-preparation.
Pendiente commit humano solo del seguimiento público de este bloque; cambios previos
conservados. Mensaje sugerido: docs: registra explorador privado del proyecto.
Próximo trabajo funcional: ampliar actividades y vínculo docente-estudiante.


## Estado vigente — 12 de octubre, intentos de práctica persistentes

Implementados guardado explícito al completar `/practica` e historial paginado propio,
total y mejor resultado. Backend calcula aciertos del banco derivadas-v1; no admite
score/propietario del cliente. Migración0012 crea intentos_practica; reintentos idénticos
no duplican y cambios del mismo ID responden409. [Contrato y pruebas](api/practica.md).

13 unitarias locales aprobadas; Docker/PostgreSQL 13 aprobadas/1 omitida (concordancia
Angular comprobada localmente), 13 Angular enfocadas. Ruff limpio. Prueba DB revierte
datos sintéticos, migración aplicada conservando esquema anterior. Sin IA ni secretos.
Guía personal regenerada: 162 clases y 270 métodos, checks DOM aprobados, permanece ignorada. Frontend/backend/DB saludables; Alembic0012 head. Flujo navegador guardado y recarga aprobado: un intento ficticio 3/3 permanece en la cuenta docente de demostración.

Pendiente commit humano: backend estudiantes/migración0012/registro API/límite de cuerpo,
servicio y pantalla Angular/pruebas/documentación. Mensaje:
`feat: guarda intentos de practica y muestra progreso privado`.
Cambios anteriores pendientes conservados; rama feature/resource-preparation.
Siguiente: ampliar actividades y vínculo docente-estudiante; no declarar seguimiento
académico ni personalización de estos ejercicios fijos.

## Estado vigente — 12 de octubre, ampliación de guía privada por clase

El autor pidió explicar todas las clases para comprender el código. Ampliada únicamente
la guía privada: `guia_personal/clases.html`, enlazada desde index.html, con 155 clases y
259 métodos/constructores, propósito, ubicación, herencia, campos/dependencias, entradas,
retornos, errores y lectura estática de instrucciones con código. Incluye clases de tests.
Cobertura cotejada contra AST Python e inventario TypeScript: 155/155, sin omisiones.
Checks DOM locales aprobados: filtros, campos, pasos, expandir/contraer y ausencia de
dependencias remotas. Sin prueba visual del HTML ni ejecución de las ramas documentadas.

Se conserva el plan estudiantil: siguiente bloque funcional, intentos y progreso persistente
con acceso por estudiante y corrección en servidor. Este bloque no implementa persistencia.
Sin cambios de aplicación, DB, secretos, inferencias ni despliegue. Cambios anteriores sin
commit preservados; rama feature/resource-preparation. La guía permanece excluida de Git
y Docker; no forzar su incorporación. Revisar/commitear solo seguimiento público de este
bloque con `docs: registra ampliacion de guia privada de clases` si se separa del anterior.

## Estado vigente — 11 de octubre, interfaz y primera práctica estudiantil

El autor priorizó ejercicios con retroalimentación y solicitó una guía privada del código.
Inicio renovado por rol: acciones docentes y entrada a práctica para estudiantes; retirados
hitos/diagnósticos técnicos de la portada y mensajes repetidos sobre consumo en consultas.
Nueva ruta autenticada `/practica`: tres ejercicios fijos de derivadas, pistas, feedback
por alternativa, resumen y reinicio. No usa IA ni guarda progreso; docente puede revisarla.

14 pruebas Angular enfocadas aprobadas; después del ajuste de progreso, las tres de práctica
volvieron a pasar. Build producción correcto y frontend desplegado. Navegador comprobó
retroalimentación de error con sesión docente; variante de inicio estudiante verificada
en pruebas, sin cambiar la identidad configurada. No se modificaron backend, DB ni secretos.

Guía privada en `guia_personal/index.html`, excluida de Git y Docker: arquitectura, operación,
roles, DB, rutas, catálogo de código propio y símbolos. Verificación DOM local de búsqueda,
selección, vínculos/líneas y ausencia de dependencias remotas; sin render visual del HTML.
No copiar sus contenidos al repositorio. Scripts privados permiten regenerarla.

Pendiente de commit humano: interfaz/estudiantes, pruebas, exclusiones y seguimiento.
Mensaje: `feat: mejora inicio por rol y agrega practica estudiantil con feedback`.
Los cambios del bloque experimental anterior siguen pendientes y se conservaron.
Próximo según prioridad del autor: diseño de intentos/progreso persistente y vínculo con
actividades docentes. No confundir esta práctica fija con personalización o notas reales.

## Estado vigente — 11 de octubre, recorrido experimental simulado

Commit humano anterior verificado: `78b761b`; árbol limpio al comenzar. Rama
`feature/resource-preparation`. Implementada CLI de simulación de pares con transporte
HTTP ficticio OpenAI/Claude, controles del manifiesto, registro y plantilla humana.
Sin lectura de configuración local ni red real; fallos/abstenciones conservados y
latencias desconocidas. [Evidencia y uso](pruebas/hito_11_simulacion_pares.md).

143 pruebas enfocadas aprobadas, Ruff limpio y ejemplo CLI ejecutado; sin despliegue,
DB ni Gemini. Pendiente de commit humano: módulo, 24 pruebas nuevas, ejemplos y docs.
Mensaje: `feat: conecta recorrido experimental con proveedores simulados`.
Próximo bloque técnico: consolidación de resultados offline para comparación con cobertura
y fallos explícitos. Benchmark real y revisión académica requieren diseño/modelos/corpus/
repeticiones/presupuesto y evaluaciones efectivas; no declararlos completados.

## Estado vigente — 11 de octubre, acceso local revisado y desplegado

Corregidos state Unicode/500, puertos inválidos y colisión CAS ticket/state. Nuevo auth/config
público solo modo; login distingue mock/CAS, restaura sesión existente y permite reintento
ante conexión fallida. Nginx resuelve backend dinámicamente. 47 pruebas backend y 13 Angular
aprobadas; builds y despliegue healthy. Navegador verificó entrada docente, restauración,
logout y protección de /documentos. DB: 21 generaciones, migración0011, sin IA ni secretos
modificados. [Evidencia](pruebas/hito_12_revision_login.md).

Rama feature/resource-preparation; cambios anteriores conservados y desplegados, sin commits
automáticos. Nuevo bloque para revisión/commit: auth/config/login/validaciones/Nginx/tests/docs.
Mensaje sugerido: `fix: corrige acceso local y configuracion de autenticacion`.
Próximo del plan: recorrido experimental manifiesto→proveedor simulado→registro; autorización
real de proveedores y evaluación académica siguen pendientes, Gemini continúa aplazado.

## Estado vigente — 11 de octubre, adaptadores OpenAI/Claude

Implementados adaptadores REST Responses/Messages, transporte común acotado sin retry,
fábrica y claves SecretStr/plantilla vacía/Compose. Gemini conserva contrato y valida que
el proveedor seleccionado coincida. GeneratePreparationService bloquea no-Gemini antes
de proveedor/reserva: autorización gratuita existente no se transfiere a otros servicios.
107 pruebas enfocadas aprobadas en 1,65 s (incluye Gemini/config/API); Ruff limpio,
advertencia Starlette/HTTPX conocida. Sin IA real, claves nuevas ni .env modificado.
Docker detenido: no se construyó/desplegó. Instalado pgvector==0.5.0 en .venv según
requirements existente para ejecutar la ruta API; sin cambios de dependencias declaradas.
[Evidencia, límites y fuentes oficiales](pruebas/hito_11_adaptadores_openai_claude.md).

Preservados cambios pendientes de paired_assessment del bloque anterior. Nuevo bloque:
adaptadores/transporte/fábrica/Settings, bloqueo API, .env.example/Compose, tests y docs.
Rama feature/resource-preparation; sin commits automáticos. Commit sugerido:
`feat: implementa adaptadores OpenAI y Claude con pruebas simuladas`.
Próximo: recorrido experimental manifiesto→proveedor simulado→registro; autorización real,
presupuesto/modelos y benchmark quedan pendientes. Gemini continúa fuera del avance activo.

## Estado vigente — 11 de octubre, revisión humana de pares

Commit humano b3b0e68 verificado; árbol limpio al iniciar. Implementado paired_assessment
CLI prepare/apply: plantilla pendiente ligada al reporte reconstruido desde manifiesto/lote,
contexto inmutable y juicios con evidencia, revisor/fecha. Referencias de revisión comunes
para ambos modos, sin exigir citas generadas al directo. Fallos/abstenciones conservados
y no calificables semánticamente. Cobertura pending/partial/available_content_reviewed,
sin atribuir calidad aprobada, identidad autenticada ni benchmark completo.
81 pruebas enfocadas aprobadas en 2,08 s; Ruff limpio. Sin IA/DB/config/despliegue.
[Uso y evidencia](pruebas/hito_11_revision_humana_pares.md).

Rama feature/resource-preparation. Nuevo módulo, pruebas y documentación pendientes
de revisión/commit humano: `feat: valida revisiones humanas de pares experimentales`.
No se ejecutó git commit. Próximo activo: adaptadores OpenAI/Claude con transporte simulado;
sin credenciales ni llamadas reales hasta concretar su uso. Gemini sigue aplazado.

## Estado vigente — 11 de octubre, registro de respuestas de pares

paired_review CLI implementado: valida manifiesto y vínculos por modo/prompt/modelo,
conserva cada intento como recurso válido, abstención, salida inválida o fallo de proveedor.
Lotes declaran procedencia sintética/proveedor; no autentica llamadas ni exhaustividad.
Fuentes comunes y bloques para revisión pendiente; citas vacías directas aceptadas.
Resumen por brazo con cobertura de tokens y total null cuando falta información.
111 pruebas locales aprobadas en 0,99 s; Ruff limpio; CLI probada sin sobrescritura.
Sin IA/DB/configuración/despliegue, solo fixtures. Ver
[evidencia y uso](pruebas/hito_11_registro_pares.md).

Rama feature/resource-preparation; preservados pendientes del bloque de preparación anterior.
Nuevo bloque revisable: paired_review, pruebas y documentación. Commit humano sugerido:
`feat: registra respuestas experimentales por modo sin inferencia`. Sin commits automáticos.
Próximo: contrato de revisión humana de pares con evidencia; después adaptadores restantes.
Gemini fuera del avance activo; benchmark y aprobaciones académicas continúan pendientes.

## Estado vigente — 10 de octubre, pares A offline

Implementado paired_preparation CLI prepare/validate con instrucciones comunes, perfil
experimental sintético medium/dificultad intermedia y controles compartidos. Política nueva
experiment-a-medium-v1; no equivalencia con perfiles/pilotos anteriores. Versiones propias
por brazo; contexto/citas/abstención/esquema diferentes y declarados. Snapshot aportado,
sin búsqueda ni autenticación de documentos; manifiesto reproducible y reconstrucción
para validar integridad interna, sin firma/autenticación de procedencia.

94 pruebas enfocadas aprobadas en 0,65 s; Ruff/formato limpios; CLI prepare/validate
comprobadas con entrada/manifiesto sintéticos versionados. Sin IA/DB/UI/config/despliegue.
[Evidencia y comandos](pruebas/hito_11_pares_offline.md). Orden/repeticiones/presupuesto/
aprobación y resultados pendientes, no inventados. Gemini continúa fuera del avance activo.

Rama feature/resource-preparation, sin commits automáticos. Revisar módulo, pruebas,
ejemplo JSON y documentación; commit humano sugerido:
`feat: prepara pares experimentales directo y RAG offline`.
Próximo: registro/revisión offline de respuestas por brazo contra manifiesto, con fallos
y abstenciones, sin exigir HistoryDetail RAG al modo directo. Benchmark sigue pendiente.

## Estado vigente — 10 de octubre, preparación directa interna

Implementados direct_schemas, PrepareDirectContentService y DirectResourceValidationService.
Cuatro recursos, dificultad manual, mode=direct, educational-direct-v1, hash canónico;
citas obligatorias vacías. Sin dependencia de búsqueda, DB, configuración ni proveedores.
Abstención interna unable_to_answer; validación estructural sin aprobación matemática.
No se alteraron contratos/prompts RAG ni se integró el modo directo en API/UI/historial.
74 pruebas locales aprobadas en 0,32 s con regresión RAG; Ruff/formato verificados.
Código local, sin reconstrucción/despliegue ni inferencias. Detalles y reproducción:
[evidencia](pruebas/hito_11_preparacion_directa.md).

Rama feature/resource-preparation. Cambios de este bloque: tres módulos internos, pruebas,
README/plan/continuidad/evidencia. Pendiente de revisión y commit humano:
`feat: prepara y valida recursos directos sin recuperacion`. Cero commits automáticos.
Próximo activo: preparador offline de pares A con controles compartidos/manifiesto;
resolver adaptación comparable con perfil antes de atribuir equivalencia experimental.
Gemini/piloto aplazados por el autor; no consultar cuota para continuar este trabajo.

## Estado vigente — 10 de octubre, matriz de evaluación A/B/C

Continuación autorizada sin proveedor/cuota. Matriz experimental MD/JSON propuesta,
sección26 del plan, ocho hashes de evidencias/capacidades locales registrados y cotejados.
A: directo vsRAG sin pares reales; preparación actual siempre recupera fuentes, falta
contrato/modo directo sin citas fabricadas. B: v3 tres recursos/7365 tokens conocidos,
v4 un éxito/dos fallos/2476 subtotal, total desconocido; no mezclar políticas/prompts.
C: fábrica solo Gemini, OpenAI/Claude sin adaptadores. D condicional, segunda materia null.
Modelos/repeticiones/rúbrica/presupuesto/revisores/orden pendientes, no aprobación inferida.

Documentación/evidencia actualizadas; sin IA, DB, migraciones, configuración o suites por
documentación. Matriz no cierra benchmark ni revisión humana. Rama feature/resource-preparation,
cero commits automáticos. Bloque listo para revisión/commit humano:
`docs: define matriz experimental y evidencia disponible`. Preservar bloques previos.
Próximo activo: preparación directa interna con contrato/modo y pruebas locales, sin
endpoint de envío/llamadas ni citas falsas. Gemini/piloto continúan aplazados por el autor.

## Estado vigente — 10 de octubre, registro de evaluación humana

Continuación autorizada sin depender de Gemini; no consultar cuota. human_review CLI
prepare/apply revalida historiales terminales mediante trial_review, crea plantilla y
guarda revisión separada vinculada por SHA. Exige evidencia y revisor/fecha declarados;
rechaza contexto/IDs/hashes alterados, alias ajenos, decisiones sin recurso y sobrescritura.
Preserva fallos/controles desconocidos. Identidad declarada no autenticada; validar archivo
no aprueba calidad ni genera notas. Estados pending_human/partial/available_content_reviewed.

41 pruebas offline enfocadas aprobadas0.45s; Ruff/formato limpios. Plantilla v4 pública
hito_11_revision_humana_v4_plantilla.json creada, validada pendiente en archivo privado:
0 decisiones,5 dimensiones/6 bloques disponibles medium; low/high fallidos preservados.
No revisión humana real ni cambios de DB/configuración/IA. Evidencia hito_11_revision_humana.md.

Backend reconstruido/CLI help comprobada en contenedor. PostgreSQL observado inactivo
durante comprobación provocó503; iniciado con volumen existente, sin causa atribuida.
Frontend reanudado, check-health aprobado,21 generaciones y huella previa conservadas.
No migraciones. El manifiesto de código anterior es histórico: nueva imagen incluye módulo.

Rama feature/resource-preparation; cero commits automáticos. Bloque listo para revisión
y commit humano: `feat: valida revisiones humanas de resultados guardados`.
Conservar otros bloques separados. Próximo activo: matriz experimental A/B/C con evidencia
guardada y requisitos pendientes, luego endurecimiento local; Gemini sigue aplazado.

## Estado vigente — 10 de octubre, avance sin depender de Gemini

El autor ordenó explícitamente saltar lo de Gemini y continuar el plan. Piloto salida1024
queda pendiente; no revisar quota en cada turno ni bloquear tareas independientes.
No interpretar como aumento de límites, reemplazo de proveedor o cierre del experimento.

Descarga del historial implementada en Angular con ResourceExportService/componente
separado y botón al restaurar un registro. Exporta HistoryDetail ya autorizado en JSON
UTF-8, sin HTTP/IA, conserva cero/null/fallos/snapshots. UUID en nombre, enlace temporal
retirado y URL revocada; error recuperable. No descarga automática ni nuevo endpoint.
No exporta prompt crudo/respuesta original FEEDBACK/secretos ni sustituye backup completo.

18 pruebas enfocadas Docker sin red aprobadas1.24s, build306.23kB inicial/preparación37.98kB.
Primer test FileReader quedó bloqueado por reloj ficticio general; acotado a timeout y
corregido. Frontend reconstruido/desplegado; servicios healthy, check-health correcto,
21 registros y huella original conservados. Sin backend/migraciones/configuración/Gemini.
Prueba del clic DOM simulada, sin afirmar descarga manual real. Evidencia:
pruebas/hito_10_exportacion_historial.md. README/guía docente/plan actualizados.

Rama feature/resource-preparation; cero commits automáticos. Bloque listo para revisión
y commit humano: `feat: descarga recursos del historial con trazabilidad`.
Conservar bloques anteriores separados. Próximo activo: evaluación de resultados
guardados/matriz experimental sin inferencias y tareas locales de endurecimiento/cierre.
Evaluación humana, benchmark real y piloto siguen pendientes; no declarar tesis terminada.

## Estado vigente — 10 de octubre, revisión del código desplegado

Continuación autorizada. Preflight17:25 UTC: tres casos íntegros, 3/5 usadas, cero activas;
512/teacher intactos. Piloto pendiente de tres cupos y configuración temporal1024.
Revisión técnica del flujo reserva/límites/proveedor/historial sin hallazgos nuevos en
ese alcance. No certifica calidad pedagógica ni inferencia real con1024.

127 archivos de fuentes/configuración backend comparados workspace/contenedor idénticos.
ManifiestoSHA66591b104e15043970db4fc3a0c41d43fb68aff145209f2fb6d63f5c85c70c15,
imagen sha256:197c7b1de4e7615a48c00c343f0a9d7286b3ecbe107b0c794719137478ae82b5.
HEAD7dcc36d4d780a7ace4247d8a577366a299c85bd9 verificado; cambios pendientes humanos
obligan conservar hashes/imagen además del commit. Evidencia/notas en
pruebas/hito_09_revision_codigo_previa.md y su JSON. No repite suites anteriores sin
cambio de lógica. No Gemini, cambios de configuración, migraciones ni datos.

Rama feature/resource-preparation. Cero commits automáticos. Bloque documental listo
para revisión/commit humano: `docs: registra revision e identidad del backend previo al piloto`.
Conservar separados los bloques anteriores. Próximo principal: cupo suficiente, renovar
preflight e identificación del código si cambia, temporal1024, tres envíos por API según
protocolo sin reintentos, restaurar512/selector previo y revisar resultados.

## Estado vigente — 10 de octubre, preflight reproducible

Continuación del plan autorizada. check-pilot-readiness.py consulta configuración segura
del contenedor, quota UTC y seis casos/documentos en transacción READ ONLY/REPEATABLE
READ. SHA de manifiesto e IDs fijados; comparación canónica de instructions+prompt,
adaptación/fuentes/hashes/propiedad. Informe sin contenidos/secretos ni inferencias.
No reserva cuota ni valida sesión; API permanece autoridad al enviar. Sin cambios de DB.

Informe final 17:13 UTC /12:13 Guayaquil: tres casos íntegros sin reserva; 3/5 usadas,
cero activas/recientes. Pendientes cupo de tres y límite temporal1024; actual512/teacher
preservados. Renovación a las19:00 locales10, requiere nueva comprobación. Primera salida
de desarrollo con SHA solo prompt produjo falsos negativos; corregida con hash canónico,
archivos conservados y explicación en pruebas/hito_09_preflight_reproducible.md.

15 pruebas enfocadas aprobadas; Ruff/formato limpios, check-health aprobado, 21 registros
con huella previa conservada. Sin suites repetidas de API/Angular ni Gemini/migraciones.
Rama feature/resource-preparation; cero commits automáticos. Bloque pendiente de revisión
y commit humano: `feat: verifica condiciones del piloto sin consumir IA`.
Conservar bloques anteriores sin mezclar. Próximo principal: piloto salida1024 con cupo,
configuración y revisión del código/evidencias; luego evaluación humana y benchmark.

## Estado vigente — 10 de octubre, revisión terminal reproducible

Nueva continuación autorizada. Consulta 17:01 UTC (12:01 Guayaquil): 3/5 reservas,
cero activas; lote salida1024 aún pendiente. trial_review implementado para tres
historiales terminales low/medium/high, incluidos fallos. Lee archivos, no DB/Settings/
proveedores; no admite FEEDBACK sin la respuesta privada necesaria. Herramienta anterior
de tres éxitos conservada. Códigos seguros compartidos movidos a contenidos/errors.py.

Reporte hito_09_revision_terminal_v4.json generado con los tres archivos originales:
hashes cotejados, un éxito/dos llm_incomplete, seis bloques, 2476 subtotal conocido,
total del lote desconocido. Configuración histórica sin registro (0/3), comparabilidad
incompleta, decisiones humanas null. No altera paquete asistido ni fuentes/manifiesto.
CLI no sobrescribe entrada/destino y revalidación reproduce exactamente el informe.

58 pruebas backend enfocadas en Docker/PostgreSQL aprobadas en 1.00 s; Ruff/formato
limpios. Backend reconstruido, servicios healthy y check-health aprobado; 21 registros
de generaciones conservan huella de campos previos. Cero IA/migraciones/cambios Angular.
No repetir suites frontend por herramienta offline. Evidencia: pruebas/hito_09_revision_terminal.md.

Rama feature/resource-preparation. Bloque listo para revisión/commit humano:
`feat: revisa pilotos completos con fallos y limites desconocidos`.
Cero commits automáticos; los bloques anteriores de respaldo y límites siguen pendientes,
conservarlos para revisión separada. Próximo: salida1024 según protocolo con cuota e
integridad/configuración verificadas, luego revisión de resultados y evaluación humana.

## Estado vigente — 10 de octubre, límites persistidos por ejecución

Continuación del plan autorizada. Cupo comprobado: 3/5 UTC 10, cero activas; no ejecutar
lote salida1024 con solo dos libres. Avance en trazabilidad de etapas 12–13: nueva
execution_configuration generation-config-v1 (entrada/salida/timeout) guardada con la
reserva por API, antes de proveedor; historial/UI leen snapshot, nunca Settings actuales.
0011_execution_configuration aplicada; 21 filas previas conservadas sin backfill ni
alteraciones de campos originales (huella de control idéntica antes/después y al cierre).
Preparaciones pendientes siguen null hasta envío. Coordinador interno legado sigue null.

66 pruebas backend enfocadas aprobadas en 1.93 s, con adaptador real/MockTransport y
confirmación de límite enviado versus persistido y cambio posterior de Settings. Ruff
limpio. Cinco Angular aprobadas en Docker sin red en 1.98 s; intento Windows no ejecutó
pruebas por timeout de worker. Builds local/Docker aprobadas (306.23 kB inicial, 35.91 kB
preparación); servicios healthy. Lectura HTTP real con mock del low salida1024: prepared,
sin reserva y configuración null; sesión cerrada. Cero Gemini y configuración activa intacta.
Evidencia: pruebas/hito_10_configuracion_ejecucion.md. Contrato/modelo DB/README actualizados.

Contexto Docker excluye respaldos_locales/seguimiento_privado. Cambios del bloque previo
de respaldo/manual técnico siguen pendientes de commit humano; no mezclarlos ni descartarlos.
Bloque nuevo listo para revisión/commit: `feat: conserva limites configurados por ejecucion`.
Rama feature/resource-preparation, cero commits automáticos. No cierra evaluación académica.
Próximo: ejecutar protocolo salida1024 con nueva verificación de cuota/configuración/
integridad y registrar revisión de código usada, sin cambiar el manifiesto/prompts.

## Avance auxiliar — 10 de octubre, respaldo comprobado y manual técnico

Commit humano previo 7dcc36d verificado (revisión v4/integridad salida1024). Sin commits
automáticos. Añadidos backup-local.ps1 y verify-local-backup.ps1, exclusión Git de
respaldos_locales, manual técnico de servicios/DB/recuperación y evidencia de operación.
Modelo de DB aclara estado 0010 sin cambiar esquema. README enlaza el manual.

Respaldo real DB+documentos creado con aplicación pausada y PostgreSQL activo; cero
generaciones activas antes de pausa. Dump binario por docker cp; archivos y hashes
guardados solo en carpeta privada excluida. Restauración de DB en contenedor sin red,
puertos ni volúmenes del proyecto: ocho tablas, pgvector 0.8.2, migración 0010_cost_basis,
2 documentos/2 fragmentos/21 generaciones/9 perfiles/2 usuarios; conteos activos iguales
al cotejo posterior. Dos documentos del archivo con hashes individuales correctos.
Contenedor temporal retirado y aplicación reanudada healthy; check-health pasó.

Pruebas proporcionales: parser PowerShell para ambos scripts, rechazo de respaldo con
servicios activos, rechazo de fixture corrupta antes de restauración, copia/restauración
reales, exclusión Git, enlaces locales y diff. No suites completas ni llamadas Gemini.
La recuperación real en otro equipo/producción, copias externas y políticas de retención
siguen pendientes. Tarea auxiliar de operación; no cierra hito 12 ni evaluación académica.

Bloque listo para revisión/commit humano: `feat: agrega respaldo local verificado y manual tecnico`.
Rama feature/resource-preparation. Próximo paso principal preservado: protocolo salida1024
con nueva comprobación de cupo/configuración/integridad; revisión humana y benchmark pendientes.

## Estado vigente — 10 de octubre, revisión v4 y disponibilidad salida1024

Continuación autorizada por el autor. Cuota comprobada a 15:42 UTC (10:42 Guayaquil):
3/5 reservas y cero activas; no iniciar lote de tres con solo dos cupos. No se hicieron
inferencias ni cambios de configuración. Selector activo observado teacher; preservado.
Salida activa 512, no 1024. Nueva renovación UTC a las 19:00 locales del 10; volver a
comprobar al retomar, sin ejecución automática ni garantías de cupo futuro.

Tres IDs salida1024 siguen prepared sin reserva. Hash del manifiesto igual al preflight;
prompts/adaptación iguales, documentos disponibles. Primer cotejo DB/API de fuentes false
por campo interno text_sha256; evidencia inicial conservada. Cotejo posterior confirma
proyección pública igual, snapshots crudos iguales a v4 y hashes de texto correctos.
Evidencia: pruebas/hito_09_salida1024_disponibilidad_20261010.json e integridad_20261010.json.

Paquete público pruebas/hito_09_revision_v4.json y explicación .md: tres casos originales,
dos fallos sin contenido/consumo reconstruido, un éxito y seis bloques citados cotejados.
Contratos HistoryDetail y ResourceValidationService revalidados; hashes de entrada
conservados. Observaciones Codex separadas de decisiones humanas null. Diferenciación
entre tres niveles no evaluable. Sin suites repetidas por documentación ni cierre académico.

Rama feature/resource-preparation. Bloque listo para revisión/commit humano:
`docs: prepara revision del piloto v4 y verifica integridad de salida1024`.
Sin commits automáticos. Conservar los cambios previos de README/guía docente/HTML,
que corresponden a otro bloque. Próximo: ejecutar únicamente los IDs preparados según
protocolo salida1024 con cupo y configuración verificados, luego cotejar resultados.

## Avance paralelo — 10 de octubre, guía docente

Commit humano 4d37560 de las preparaciones verificado. Cupo UTC 10 consultado a 11:10:
3/5 reservas, cero activas; lote salida1024 aún sin enviar. No cambios de configuración.
Guía práctica creada en manuales/guia_docente_mvp.md, enlazada desde README, cotejada
con rutas/plantillas y contratos actuales. Describe roles, ingesta, índice, perfiles,
preparación/generación, historial/métricas y fallos. Es borrador operativo: validación
de usabilidad y cierre de manuales pendientes, sin saltar la evaluación de etapas 11–13.
Corregido texto obsoleto de Documentos sobre disponibilidad de búsqueda. Build Angular
de producción aprobado, diff sin errores; sin nuevas pruebas de lógica ni llamadas IA.
Commit humano sugerido: `docs: agrega guia docente del MVP y aclara indexacion`.
Próximo paso principal sigue siendo ejecutar lote salida1024 con cupo suficiente y
verificación de configuración previa, usando sus IDs ya guardados.

## Estado actual — 10 de octubre, comparación de capacidad preparada

Commit humano 1610020 verificado para metadatos seguros. Nuevo protocolo fijado:
pruebas/hito_09_protocolo_salida1024.md y .json. SHA manifiesto
48be7fc1d89f61c4946043f545d91bc1623df34d856c2841edf3ff569857aae6.
Tres registros nuevos prepared por API, reutilizando perfiles v4. Fuentes/adaptación y SHA
del prompt exactamente iguales a sus respectivos v4, comprobados. Preflight en
pruebas/hito_09_salida1024_preparaciones.json; todavía SIN inferencias.
Solo se propone cambiar salida 512→1024 al ejecutar; configuración activa conservada
en 512, no confundir preparación con configuración de envío validada. Cupo consultado:
3/5 UTC 10 y cero activas, insuficiente para tres. No automatización ni aumento de cuota.
Próximo: con tres cupos disponibles, verificar configuración real temporal 1024, preservar
evidencia antes de enviar y ejecutar únicamente los IDs guardados sin reserva previa.
Restaurar 512 y mock student al cerrar. No repetir v4 ni elevar límites después de fallos.
Bloque listo para commit humano: `test: prepara comparacion de capacidad de salida`.

## Estado actual — 10 de octubre, metadatos de truncamiento

Commit humano d68c12d del piloto v4 verificado. Corrección posterior implementada:
MAX_TOKENS conserva solo uso válido y latencia en FailureMetadata; ambos coordinadores
lo propagan y la traza comprueba propietario/estado/modelo antes de persistir. Recurso
sigue null y estado failed; cero condicionado solo con entrada/salida conocidas y base.
Históricos low/high v4 permanecen desconocidos, sin reconstrucción ni reintentos.
80 pruebas enfocadas Docker/PostgreSQL aprobadas (2.79 s), Ruff/diff correctos; sin llamadas
Gemini ni cambios de límite, frontend o esquema. Sesión anterior de pruebas interrumpida,
resultado confirmado en la reanudación. Evidencia: pruebas/hito_10_metadatos_truncamiento.md.
Pendiente de commit humano: `fix: conserva metadatos seguros ante truncamiento de Gemini`.
Próximo: fijar protocolo nuevo para estudiar límite de salida; no repetir el piloto v4.
Etapas 11–13, validación humana y benchmark todavía pendientes.

## Estado actual — 9 de octubre, piloto v4 ejecutado

Commit humano adabe88 verificado; protocolo anterior incorporado. Piloto ejecutado a
20:43–20:45 Guayaquil (UTC 10), tras renovar cupo: tres preparaciones con fuentes iguales
a v3 y versiones verificadas. Low/high failed llm_incomplete (MAX_TOKENS); medium succeeded,
2029/447/2476 tokens, 19667 ms, costo condicionado 0 USD. Fallos con uso/costo desconocidos.
No reintentos ni cambios de límites. Base de costo persistida en los tres casos.
Evidencia en pruebas/hito_09_piloto_v4.md y cuatro JSON (preparaciones y tres detalles).
No permite comparar tres niveles ni cerrar validación pedagógica. Observación técnica
del medio separada de revisión humana pendiente. No correr comparación de tres éxitos.
Selector student restaurado, sesiones de prueba cerradas, salud correcta; 3/5 reservas
UTC 10, cero activas. Próximo: preservar metadatos seguros en errores MAX_TOKENS mediante
pruebas simuladas; definir después protocolo nuevo para investigar límite de salida.
No gastar los dos cupos restantes en reintentos del piloto cerrado.
Commit humano pendiente: `test: conserva resultados completos del piloto v4`.

## Reanudación — 9 de octubre, protocolo prospectivo v4

Trabajo retomado en feature/resource-preparation. Commit humano 6082e6f verificado:
incluye piloto v3, orientación v4 y costo; las menciones pendientes de abajo son históricas.
Sin operaciones de integración/publicación en esta sesión.
Protocolo v4 fijado en pruebas/hito_09_protocolo_v4.md y .json, aún sin ejecutar ni crear
preparaciones. SHA del manifiesto: 42d0d77582b1ef3518dc6c33115d64ea962603852b128190a881fd97fcd1d1a1.
A las 21:09 UTC había 4/5 reservas, cero activas; no enviar lote de tres con un solo cupo.
Configuración no sensible coincide: Gemini 3.1 Flash-Lite, 12000/512, timeout 30 s, mock.
Verificada diferencia de bytes LF/CRLF del corpus complementario; manifiesto distingue
archivo local del original cargado. Reutilizar documentos indexados, no recargarlos.
Revisión offline v3 generada en seguimiento_privado/revision_perfiles_v3.json: tres casos,
cuatro controles mecánicos verdaderos, 7365 tokens; decisiones humanas pendientes.
Próximo: comprobar cuota al retomar, preparar tres casos v4 y conservar preflight antes
de enviar. No programación automática. Evaluación humana/benchmark/manuales pendientes.
Bloque documental pendiente de commit humano: `docs: fija protocolo prospectivo de personalizacion v4`.

## Estado actual — 9 de octubre, costo condicionado versionado

cost_basis guardado antes de inferencia: confirmed-free-tier-v1, proveedor/modelo, USD,
tarifa asumida gratuita confirmada por operador. Importe 0 con entrada/salida conocidas;
consumo parcial e históricos null. No certifica facturación. Migración 0010 aplicada,
15 registros sin backfill. 40 pruebas backend y 3 Angular aprobadas; build y salud correctos.
Cero llamadas Gemini; cuatro reservas UTC 9 al verificar. Sin cambios de acceso/cuota.
Ver pruebas/hito_10_costo_condicionado.md para comandos, evidencia y límites.
Tercer bloque pendiente de commit humano: `feat: registra estimacion condicionada de costo por generacion`.
Dos bloques previos también pendientes; separar por propósito, incluidos fragmentos
compartidos de test_content_adaptation.py y documentación. No ejecutar commits automáticos.

## Avance conservado — piloto v3 y orientación v4

Commit humano verificado: b0eb5c3 contiene el bloque previo de orden y revisión offline.
No hacer commits automáticos. Dos bloques nuevos pendientes de revisión/commit humano:
evidencia/protocolo/corpus del piloto v3 y corrección de orientaciones v4/política v2.

Piloto v3 completado por API autenticada, una llamada por nivel: 2466/2428/2471 tokens,
7365 en total. Tres succeeded; 2643/15589/1988 ms de proveedor. Mismas fuentes y factores
comprobables; pausa de 4 h 14 min 14 s por interrupción, no reintentos. Registro parcial
conservado y resultados completos separados. Informe pruebas/hito_09_piloto_v3.md.
Los tres recursos repiten cuatro pasos parecidos: mejor correspondencia observable con
la función/fundamentos, pero personalización poco diferenciada y sin aprobación académica.
High introduce a=3 por sustitución correcta, no explícita en S2: observación preservada.

Nuevas preparaciones: profile-adaptation-v2 + educational-rag-profile-v4. Low guiado,
medium concentrado, high condiciones/interpretación; no inventar casos para aparentar
complejidad. Historial v1 aceptado; ausente versión sigue v1. No modificar snapshots v2/v3.
58 pruebas enfocadas Docker aprobadas (1.15 s), Ruff limpio, sin nuevas pruebas Angular.
No atribuir al ajuste v4 las generaciones v3. Evaluación real v4 todavía pendiente.

Docker recuperado tras fallo de socket temporal; carpeta run conservada mediante renombrado
reversible, sin reset de fábrica ni borrado de volúmenes. Detalles locales en bitácora privada.
Selector mock restaurado a student; UTC 9 lleva cuatro reservas globales y cero activas al
cerrar piloto. No aumentar cuota ni enviar un caso aislado para aparentar comparación completa.

Próximos puntos: evaluación prospectiva de orientación v4 con corpus fijo y revisión humana;
verificar costo en la próxima ejecución planificada; después etapa 14 (directo/RAG,
perfiles/proveedores según presupuesto USD 0) y etapa 15 (manuales, revisión final y evidencia).
Sistemas universitarios fuera de esta etapa. Retención opcional; reservas independientes
solo antes de purgar. Rama feature/resource-preparation; bitácora privada excluida.

## Antecedente — 9 de octubre, orden del repositorio y revisión offline

Sin commits nuevos: control humano vigente. Cambios del ajuste de alcance todavía
pendientes de commit junto con limpieza documental; separar el bloque de herramienta
de evaluación en otro commit humano. Retirados dos scripts smoke iniciales que llamaban
Gemini fuera de la cuota API. Evidencia histórica conservada y marcada; README y matriz
del plan corregidos para no presentar generación/personalización como no implementadas.
Los apartados de sesiones anteriores son antecedentes, no estados actuales simultáneos.

Nuevo módulo evaluacion/offline_review.py prepara revisión de tres resultados sintéticos
guardados, sin BD/configuración/IA; revalida contrato/citas, compara factores, conserva
desconocidos y extrae bloques para cotejo humano. Salida nueva exclusiva, sin sobrescribir
evidencia. Informe hito_09_revision_offline.json conserva hash de entrada, tres casos,
4577 tokens conocidos y decisiones semánticas pendientes. Rúbrica operativa propuesta
en hito_09_revision_offline.md, sin aprobación académica ni puntuaciones automáticas.
57 pruebas locales enfocadas (revisión, adaptación y contratos) aprobadas en 6.17 s;
Ruff limpio. No se repitieron suites completas ni se generó contenido nuevo con Gemini.

Backend reconstruido y desplegado: backend/frontend/postgres healthy, /health confirma
API/BD/pgvector ok. Los dos smoke no existen en la imagen activa; revisión offline sí.
SHA-256 del informe cotejado con entrada original. Limpieza de tres cachés locales fue
rechazada por revisión automática: se conservaron; siguen excluidas de Git y no son código.

Etapas 11–13 / hitos 9–10: siguiente paso, cotejo humano de afirmaciones v2 y protocolo
v3 fijado antes de inferir, con corpus suficiente, factores y repeticiones definidos dentro
de cuotas. No cerrar etapa 14 ni calidad pedagógica por este informe. Sistemas universitarios
fuera de esta etapa. Costo estimado sigue desconocido. Retención/purga opcional de cierre:
si se implementa, separar reservas antes de eliminar datos; no es un bloqueo para evaluar.
Rama feature/resource-preparation; diario privado excluido. No tocar secretos, dependencias
instaladas, datos persistentes, corpus ni capturas de evidencia como limpieza.

## Instrucción vigente del autor — 9 de octubre, ajuste de alcance y control humano

Cero commits automáticos desde esta actualización; avisar al autor cada bloque listo,
con cambios y mensaje sugerido. No reescribir commits históricos. AGENTS.md y plan
actualizados, pendientes de commit humano. Ningún commit nuevo por esta revisión.
Integración con sistemas universitarios fuera de esta etapa inicial; conservar diseño
de dominio/SSO y entorno mock con identidades ficticias, sin conectar CAS ni datos reales.
Pruebas proporcionales, enfocadas al cambio; sin repetir suites por documentación.
La sección 19 del DOCX adjunto ubica el avance en etapas 11–13, hitos 9–10: implementación
de personalización, trazabilidad e historial/métricas disponible; validación académica y
costo versionado pendientes. Etapas 14–15/hitos 11–12 aún por realizar. Retención/purga
es endurecimiento auxiliar; no imponerla como fase obligatoria antes de evaluar si no se
van a borrar datos. El registro independiente de reservas es previo a cualquier purga.
Los estados antiguos de integración pendiente de TI son históricos, no bloqueos actuales.

## Antecedente de sesión — 9 de octubre, cierre de instrucciones v3

Bloques cerrados: 819e3b0 auditoría por recurso, 9c77e44 comparación real de tres perfiles
(sin aprobación académica), f60f5fa propuesta/diagnóstico de retención estrictamente de
lectura. Instrucciones nuevas educational-rag-profile-v3 subordinan dificultad/apoyo al
objetivo y respaldo explícito de fuentes; política y flujo manual sin cambios, v2 histórico
intacto. 298 backend aprobadas (45.99 s), Ruff limpio. Frontend conserva 61/16 archivos y
build de auditoría, sin nuevos cambios Angular. SQL confirma las tres versiones/hashes v2
conservadas. No nuevas llamadas por este ajuste. Punto técnico cerrado con commit descriptivo; hash registrado en la bitácora privada.

Próximo punto de plan: separar registro persistente de reservas del contenido antes de
implementar retención/purga; probar backfill, cupo tras eliminación, reinicio y concurrencia.
No hay TTL ni purga aprobados; no borrar muestras ni volúmenes. Evaluación real v3 necesita
protocolo propio antes de generar y revisión con corpus suficiente; no repetir/reemplazar
v2 para ocultar sus limitaciones. UTC 9 registra una reserva en esta sesión (alto original).
CAS TI, corpus real autorizado, política de datos/roles, rúbrica y benchmark siguen abiertos.
Documento de continuidad y diario privado guardan pendientes; no inventar porcentaje de
tokens disponibles. Rama feature/resource-preparation, sin remoto, secretos/diario excluidos.

## Antecedente de sesión — 9 de octubre, comparación alta completada

Auditoría cerrada en 819e3b0; métricas en 31d3e6b. Docker Desktop iniciado, volúmenes
conservados y Compose saludable; selector mock restaurado a student tras login docente.
Alta 32960f76-5d6d-43b7-9e9b-8d552c9970ed generada una vez con configuración existente:
succeeded, inicio 2026-10-09 09:08:15.637445 UTC, 1156 entrada/386 salida/1542 total,
18901 ms. Recuperada tras recargar sin inferencia; contador UTC 9 = 1. Proveedor/modelo,
fuentes y protocolo sin cambios; casi diez horas de separación del bajo/medio. Evidencia
pruebas/hito_09_comparacion_completa.md/JSON y capturas, sin identidades/credenciales.

Hallazgo pendiente: ejemplo alto g(x)=3x²+2x es más complejo y su derivada correcta, pero
se aparta del objetivo limitado a x² y usa reglas no explícitas en S1. No afirmar calidad
pedagógica ni fidelidad semántica certificada. Próximo bloque: prioridad objetiva/fuentes
en instrucciones de adaptación con versión nueva y pruebas, sin alterar preparaciones
guardadas ni repetir el experimento. Después retención: propuesta 0012 y diagnóstico SQL
de lectura preparados; todavía no hay purga/TTL institucional aprobado. Antes de purga,
separar reservas del contenido para no reponer cupo ni ignorar ejecuciones activas.
Suites de código vigentes: 296 backend y 61 Angular; no repetidas por evidencia documental.

## Antecedente de sesión — 9 de octubre, auditoría por recurso

El 8 de octubre se implementó y probó el objeto audit del detalle del historial y un
desplegable Angular con fechas, proveedor/modelo, uso parcial, latencia, costo nullable,
código seguro, versión/hash de prompt y metadatos de recuperación. Lectura propia sin
inferencias ni errores crudos. 296 backend (32.44 s), 61 Angular/16 archivos (10.92 s),
Ruff limpio, build inicial 306.23 kB/preparación lazy 34.55 kB. Navegador verificó recurso
intermedio, fallo llm_timeout y alto aún preparado; móvil sin desbordamiento. Evidencia
pruebas/hito_10_auditoria.md y api/auditoria_recursos.md. El 9 se reanudó el cierre documental;
Docker estaba detenido y se inició conservando volúmenes. No repetir suites aprobadas si
solo se añade documentación. Cerrar este punto con commit y registrar en bitácora privada.

Próximo paso: comprobar cuota UTC actual/estado preparado y generar una vez el alto
32960f76-5d6d-43b7-9e9b-8d552c9970ed; actualizar la comparación con separación temporal.
Después retención/purga segura (el cupo depende de trazas: no borrarlas sin conservar
un registro independiente de reservas), estimación de costo versionada y benchmark.
CAS/corpus institucional/evaluación académica siguen pendientes de parámetros/autorización.
La sección de métricas del 8 es antecedente, cerrada en 31d3e6b.

## Antecedente de sesión — continuación del 8 de octubre, métricas

Punto técnico cerrado: GET `/api/v1/metrics` y Angular `/metricas`, navegación docente,
resumen privado de todo el historial propio mediante una sola agregación SQL. Conteos de
estados, reservas y trazas separados; tokens y latencia con cobertura explícita/null;
solo cobertura de estimación de costo, sin tarifas ni verificación de facturación. No hubo
nuevas llamadas Gemini, cambios de cupo, migraciones ni modificación de credenciales.
Backend 295 pruebas aprobadas (29.51 s), Angular 59/15 archivos (54.04 s), Ruff limpio,
build Docker inicial 306.23 kB y métricas lazy 9.51 kB; Compose saludable. Navegador:
12 preparaciones, 4 prepared/0 generating/7 succeeded/1 failed, 8 trazas y 6 reservas,
9985 tokens totales conocidos en 7 trazas/1 sin dato, latencia promedio 4515.14 ms,
8 costos sin estimación. Actualización explícita y móvil sin desbordamiento verificados.
Evidencia `pruebas/hito_10_metricas.md`, contrato `api/metricas.md`, decisión 0011.

La bitácora personal se mantiene en seguimiento_privado/BITACORA.md, excluida y sin archivos
versionados. Cerrar este punto con commit feat descriptivo y registrar hash únicamente en
bitácora privada. Rama feature/resource-preparation, sin remoto.

Próximo paso: cuando se renueve el cupo UTC 9 (8 de octubre 19:00 Guayaquil), recuperar del
historial la preparación alta 32960f76-5d6d-43b7-9e9b-8d552c9970ed, verificar límites/modelo,
enviar una sola vez y completar evidencia de comparación. Sigue sin enviar al cerrar este
bloque anterior a las 19:00. No aumentar cuota ni repetir bajo/medio. Después completar
metadatos de trazabilidad consultables por recurso y política de retención/purga antes de
datos reales. Estimación monetaria necesita precio/moneda/versionado; benchmark/cierre/CAS
TI pendientes. Las secciones históricas siguientes se conservan como antecedentes; esta
sección reemplaza sus referencias a métricas aún no implementadas. No declarar hito 9
académico ni hito 10 completo.

Actualizado: 8 de octubre de 2026, America/Guayaquil. Estado vigente al registrar dos salidas adaptadas reales y bitácora privada. No se dispone de un porcentaje fiable de tokens restantes; no se inventa uno.

## Instrucciones vigentes

El autor pide itinerario personal por día/sesión en seguimiento_privado/BITACORA.md, excluido de Git/GitHub. Actualizar con trabajo, verificación, pendientes y commits; no copiar su contenido privado a documentación pública. Hacer commit al cerrar cada punto verificable, sin declarar hitos incompletos como terminados. Exclusión y regla persistente comprobadas en 05b7cec.

Seguir el plan por etapas. Las instrucciones directas del autor reemplazan autenticación local/Google y registro abierto por SSO/CAS UPS, modos mock/cas y cookie HttpOnly/SameSite. Angular no solicita contraseñas ni almacena tokens. CAS espera parámetros de TI. Conservar Angular, FastAPI, PostgreSQL/pgvector, Alembic y Docker; interfaz española, paleta UPS azul/amarillo/blanco y navegación superior accesible/responsiva.

Gemini elegido. Presupuesto autorizado USD 0: queda descartada la propuesta de USD 1. El autor mostró AI Studio con Nivel gratuito y autorizó usar la API; se acepta esa confirmación, no es verificación programática de facturación. No activar facturación, comprar créditos ni hacer fallback pagado. Clave configurada en .env: nunca imprimirla/copiarla a Git/pedirla por chat. Solo material sintético en pruebas externas; corpus institucional y perfiles reales requieren autorización/política de datos.

## Qué tenemos

- Hito 1: infraestructura modular, Docker, health, Alembic, Angular y pgvector comprobados.
- Hito 2 local: cuatro rutas auth, estado de navegador de un solo uso, sesión opaca persistida por hash, expiración/revocación, alta/actualización automática y conservación del rol. Usuario sin contraseña, CAS configurable pendiente de TI.
- Hito 3: biblioteca privada teacher/admin PDF/DOCX/TXT, validación, carga hasta 10 MiB, paginación, detalle y eliminación propios.
- Hito 4: extracción en worker, segmentos con página/párrafo, offsets Unicode y SHA-256, publicación atómica/reintentos/recuperación. E5 ONNX CPU local, 384 dimensiones, revisión 614241f622f53c4eeff9890bdc4f31cfecc418b3, e5-onnx-v1; pesos privados en volumen, inferencia sin red, sin truncar >512 tokens.
- Hito 5 técnico: búsqueda exacta propia con top-k/fuentes/filtros, pantalla /busqueda. HNSW contrastado contra referencia exacta en muestra sintética; no equivale a benchmark académico.
- Hito 6 parcial: interfaz LLMProvider, fábrica, adaptador Gemini REST, límites y metadata/errores seguros. gemini-3.1-flash-lite comprobado realmente; OpenAI/Claude pendientes, sin fallback.
- Hito 7 en curso: explicación/ejercicio/quiz/feedback, dificultad manual, quiz 1–5 y respuesta sintética requerida para feedback. Prompt educational-rag-v1, preparación propia top-3, snapshots y validación JSON/citas. Coordinador interno probado con cuatro recursos y fallos.
- Generación API/UI conectada: /recursos → preparar/revisar fuentes → botón explícito → POST /api/v1/content/{id}/generate → una llamada → validación → recurso/fallo. Los cuatro contratos mínimos confirmados realmente desde Angular con material sintético, citas y persistencia. Roles/propiedad/CSRF, no-store, cuerpo vacío sin configuración cliente y máximo 16 KiB.
- Trazabilidad: prepared→generating→succeeded/failed, reserva persistida antes de red, cierre condicional, snapshots/modelo/consumo conocido o null. Migraciones 0001–0009 aplicadas, anteriores inmutables. Historial privado HTTP con adaptación implementado; métricas académicas/costo calculado pendientes.
- Hito 8 técnico: POST /profiles, GET /profiles y GET /profiles/{id}; observaciones sintéticas inmutables privadas por creador teacher/admin, campos estrictos y versión performance-profile-v1. Angular /perfiles guarda, lista y abre detalle. Porcentaje/dominio/apoyo informados, sin calcular notas ni vincular usuarios reales; integración externa institucional pendiente. Ver api/perfiles.md y decisión 0009.
- Hito 9 preparación: profile_id propio opcional en /content/prepare, mismo tema requerido; dominio low→basic/pasos, medium→intermediate/práctica y high→advanced/complejidad. Foco en etiquetas de errores sin inferir gravedad. Tipo de recurso elegido por docente, alternativas sugeridas. Snapshot completo y política profile-adaptation-v1, prompt educational-rag-profile-v2; manual v1 compatible. Migración 0009 aplicada. Angular selecciona perfiles paginados, explica ajuste y restaura decisión histórica. No transmite perfil completo/identificadores a Gemini ni calcula notas. Diferencias de salidas reales y evaluación pedagógica pendientes.

## Límites y estado local

.env privado: LLM_ENABLED=true, LLM_FREE_TIER_CONFIRMED=true, LLM_DAILY_REQUEST_LIMIT=5, gemini-3.1-flash-lite, una petición/minuto, entrada 12000 caracteres, salida 512 tokens, timeout 30 s. Plantilla con activación/confirmación false. Secretos excluidos de Git.

La ruta reserva cinco intentos globales por día UTC en PostgreSQL, incluidos fallos; una llamada simultánea y 60 s entre inicios. Reiniciar Docker no restaura el cupo. Preparación de un solo envío; terminal inmutable. Intentos abiertos >90 s se cierran como interrumpidos al reclamar otra preparación, sin reenvío. Documentos deben seguir disponibles para su propietario. Scripts manuales y otros clientes de la clave NO pasan por este cupo API. Limita solicitudes, no verifica facturación ni impone tope monetario en Google.

Docker backend/frontend/postgres saludable; datos/modelos conservados. Navegador /recursos con sesión docente ficticia renovada y preparación adaptada recuperada; selector de nuevos accesos restaurado a student. CAS no conectado. Sin contenido en localStorage; tras recargar se consulta la lista para reabrir recursos o perfiles conservados en PostgreSQL.

## Pruebas y evidencia

Última suite: 292 backend/PostgreSQL aprobadas en 35,36 s, dos advertencias conocidas Starlette/HTTPX y pypdf; 56 Angular en 14 archivos. Ruff check/format limpios, 148 archivos; build sin advertencias, 305,75 kB inicial y 28,93 kB módulo preparación. Tests automáticos sin Gemini. Doce combinaciones recurso/nivel y generación sobre prompt adaptado conservado con proveedor ficticio comprobadas. Preparación 07cc9201-5d1d-4ab5-8bd1-76bf1f3fb225, perfil 5bb5b546-d9bb-49b6-ada5-f26528952c01: advanced→basic, política/motivo/foco restaurados tras recargar. Capturas y SQL en pruebas/hito_09_personalizacion.md; ninguna llamada Gemini en este bloque. Conservar evidencia previa pruebas/hito_08_perfiles.md.

Prueba Angular real sintética: e4fcd956-cdf4-43a1-8487-d82997e096b3, succeeded, gemini-3.1-flash-lite, S1, 1076 input/312 output/1388 total, 2355 ms. Reserva 2026-10-07 22:06:57 UTC y persistencia SQL confirmadas. Una llamada en este bloque; costo desconocido/null, no afirmar cargo medido cero. Evidencia pruebas/hito_07_generacion_ui.md y capturas hito_07_generacion_desktop.png / mobile.png. Móvil 390×844 solicitado, ancho DOM útil/scrollWidth 375 px sin desbordamiento, viewport restaurado.

Pruebas anteriores: conexión 55 tokens en pruebas/hito_06_gemini_real.md; coordinador RAG con timeout registrado y posterior éxito 1403 tokens en pruebas/hito_07_coordinador.md / hito_07_generacion_real.json. 2.5 Flash-Lite recibió 404; sin fallback/reintento automático ni causa inventada.

Evaluación RAG calculo-sintetico-v1: recall@3 base 0,875; alias explícitos mejoraron a 1 y MRR@3=0,9375 en la misma muestra que motivó el ajuste. No es validación independiente ni medición a escala. Reporte pruebas/hito_05_recuperacion.json. Conservar evidencia anterior de extracción, embeddings, permisos, CSRF, idempotencia y publicación tardía.

## Punto exacto siguiente

Hito 7: cuatro recorridos mínimos reales e historial privado comprobados; validación académica pendiente. Hito 8 sintético técnico terminado; hito 9 implementación disponible y comparación real parcial registrada. Próximo bloque: recuperar la preparación alta 32960f76-5d6d-43b7-9e9b-8d552c9970ed desde historial y completar esa comparación cuando el cupo lo permita, sin recrear preparaciones ni reintentar bajo/medio. UTC 8 termina en cinco inicios (tres anteriores + dos actuales). Renovación UTC 9: 8 de octubre a las 19:00 de Guayaquil; no hay ejecución programada. Verificar modelo/límites y documentar separación temporal. Después hito 10: métricas privadas de estados/latencia/tokens con null/desconocido explícito, sin inventar costo ni notas, y retención antes de datos reales. Nunca llamadas externas en suites/healthchecks/arranque.

Comparación actual: c00981b5-8f00-4e76-87fe-c4384ab11d47 (low, succeeded, 1161/381/1542 tokens, 1951 ms) y 39f18cd0-5529-4e25-a025-81f098d56033 (medium, succeeded, 1154/339/1493, 1999 ms), ambas 3.1 Flash-Lite/S1 con fuentes y datos fijos iguales. Dos salidas recuperadas tras recargar sin nuevas llamadas. Limitación: ambas añaden regla general de potencia no expresada en fuente; diferencias pequeñas, sin beneficio académico probado. Preservar protocolo/evidencia en pruebas/hito_09_comparacion_parcial.md y JSON. No cambiar esta muestra retrospectivamente; futuros corpus/rúbricas se documentarán por separado. Cambio UI únicamente informativo, build aprobado; las suites funcionales anteriores siguen siendo 292/56 y no se han repetido en este bloque.

Pendientes: validación académica con corpus/rúbrica autorizados y consultas independientes; integración externa de perfiles, vocabularios, idempotencia y política de datos; evaluación de salidas adaptadas hito 9; métricas/retención/purga e historial completo hito 10; benchmark comparativo/proveedores restantes hito 11; endurecimiento/manuales/informe hito 12; CAS TI, administración global de roles/asignación de corpus estudiantil. PDF escaneados necesitan OCR, fórmulas/columnas requieren cotejo, OfficeMath se rechaza. Producción requiere cola/aislamiento/retención/limpieza de huérfanos. Snapshots conservan texto tras borrar documentos: definir purga antes de datos reales. Licencia y cuenta/visibilidad GitHub pendientes.

## Git y cómo retomar

Repositorio C:/C_PROJECTS/TESIS COMPUTACION/TutorIA-Lucero, rama feature/resource-preparation, sin remoto/publicación. Bloques previos 8f2e735 (historial), 33dc800 (documentación), 2f723ac (cuatro recursos reales) y 2cb6b21 (perfiles); adaptación en commit descriptivo (git log -1). Revisar git status y preservar cambios.

Leer AGENTS.md, README.md, PLAN_DE_TRABAJO.md, decisiones 0002/0004/0005/0006/0007/0008/0009/0010 y api/contenidos.md / perfiles.md / personalizacion.md / limites_gemini.md. Levantar con docker compose up -d --build --wait sin imprimir secretos, sin docker compose config ni eliminar volúmenes. Si faltan pesos: docker compose --profile embeddings run --no-deps --rm prepare-embeddings. No repetir verificaciones cerradas sin cambios/fallos que lo justifiquen.

## Evidencia conservada: contratos de recursos

7 de octubre, sesión nocturna: Docker Desktop se inició tras encontrar el motor detenido; datos/modelos conservados. Sesión docente ficticia renovada, selector de nuevos logins restaurado a student. 50 pruebas Angular aprobadas en 13 archivos, incluidas presentación de ejercicio/quiz/feedback; backend conserva 247 aprobadas (sin cambios backend posteriores).

Ejercicio real 34cbaee3-9dbe-40f6-a41b-65e3568d606b: succeeded, 1115 input/324 output/1439 total, 2088 ms, S1. Quiz real de una pregunta 42289db1-b80a-4290-b7bd-b26d1b03b845: succeeded, 1168 input/222 output/1390 total, 7516 ms, S1, cuatro opciones y respuesta desplegable comprobadas. Feedback 77754fbb-be92-4495-bdae-781db4a6b964 también succeeded: 1080 input/250 output/1330 total, 14146 ms, S1. Tres llamadas nuevas completadas, cupo UTC del 8 de octubre (fecha local 7), anterior llamada UI en día UTC previo. Los tres se recuperaron desde historial sin inferencia. Evidencia pruebas/hito_07_cuatro_recursos.md y recursos_reales.json. Pruebas externas de estos contratos cerradas: no repetirlas automáticamente. No reenvío ni gasto verificado.

## Consulta operativa — 10 de octubre, estado y acceso local

Revisión de solo lectura del código, plan y configuración no secreta activa. API /health:
api/database/pgvector ok; PostgreSQL accesible, ocho tablas y migración 0010_cost_basis.
Frontend inicialmente Exited (1): nginx no resolvió backend durante el arranque.
Recuperado con docker compose up -d --wait frontend; backend/frontend/postgres healthy,
migrate Exited (0), /login HTTP 200. Sin cambios de código/configuración, sin inferencias
ni borrado de datos. No se repitieron suites: comprobación operativa de salud y acceso.
Mock activo student; Gemini habilitado. La validación pedagógica, lote salida1024 y
benchmark conservan sus pendientes y protocolos. Rama feature/resource-preparation.
Registro documental pendiente de revisión/commit humano; no se ejecutó git commit.

## 12 de octubre — Mejora didáctica del explorador privado

Ampliado el explorador con recorrido de aprendizaje, explicación por responsabilidad,
conceptos presentes en cada archivo/operación, claves de configuración y referencias
textuales a estructuras (no equivalen a dependencias resueltas). Añadidos expandir/contraer
carpetas, apertura de ancestros y modo de explicación amplia. Mantiene 305 archivos y
869 estructuras; recorrido DOM completo aprobado. Revisión visual del HTML pendiente.
Sin cambios de aplicación ni datos. Rama feature/resource-preparation; guía ignorada.
Pendiente commit humano del seguimiento público: docs: registra mejora didactica de guia.
Siguiente: ampliar actividades estudiantiles y vínculo docente-estudiante.

## 13 de octubre — Revisión de respuestas guardadas

Historial de práctica ampliado con revisión de cada intento: respuesta elegida, correcta,
feedback por alternativa y conceptos para reforzar. Abrir/cerrar la revisión no modifica
la práctica actual ni guarda nuevos intentos. Versión desconocida, longitud incorrecta o
índice inválido conservan el resumen sin interpretar las respuestas con el banco actual.
Nueve pruebas Angular aprobadas; construcción Docker correcta. Sin cambios de API o DB.
Guía privada regenerada con el comportamiento nuevo. Commit previo verificado: 40cd907.
Rama feature/resource-preparation. Pendiente commit humano de componente, HTML, estilos,
pruebas y seguimiento: feat: permite revisar respuestas de practicas guardadas.
Continúan pendientes banco ampliado y asignaciones docente-estudiante. Sin uso de Gemini.

## 13 de octubre — Acceso estudiantil de demostración

Agregados select-demo-role.ps1 y compose.demo.yml: selección student/teacher en servidor,
validación development/mock sin imprimir configuración sensible, recreación del backend
y espera de salud. No modifica .env ni sesiones existentes; selección compartida por instancia.
Ejecutado student y verificado mode=mock/demo=student; backend saludable. 18 pruebas de
configuración y validación CAS aprobadas; advertencia preexistente Starlette/httpx.
Manual acceso_estudiante documenta cierre/reingreso, reversión docente y requisitos CAS.
Sin conexión UPS, sin Gemini ni cambios de esquema. Rama feature/resource-preparation.
Pendiente commit humano: script, complemento Compose y documentación; mensaje sugerido:
feat: facilita acceso local de demostracion como estudiante.
Siguiente: banco ampliado y asignaciones; acceso CAS real depende de parámetros autorizados.

## 13 de octubre — Selección de perfiles de demostración desde login

Solicitud del autor: distinguir estudiante est.ups.edu.ec y profesor ups.edu.ec sin CAS.
Login muestra ambos perfiles y dominios previstos, pero conserva identidades ficticias
example.org y sus datos separados. Selector permitido únicamente en development/mock;
CAS lo rechaza y admin no es válido. Perfil fijado en service_url del intento persistido,
no leído del query del callback; no cambia roles locales existentes. Sin migración.
34 pruebas backend y 5 Angular aprobadas; prueba de alteración de callback incluida.
Nueva decisión reemplaza la selección exclusiva del perfil mock por configuración backend:
el navegador elige entre dos perfiles ficticios predefinidos, nunca envía correo o identidad.
Pendiente commit humano del acceso, pruebas y documentación. Mensaje sugerido:
feat: permite elegir perfiles de demostracion en el acceso.
Rama feature/resource-preparation. CAS real y cuentas individuales siguen pendientes.

Cierre: imágenes construidas y frontend/backend/PostgreSQL saludables. Ruff aprobado tras ordenar imports del test. Sin revisión visual en navegador en este bloque.

## 14 de octubre — Segundo banco de prácticas

Implementados dos bloques de tres ejercicios: fundamentos (derivadas-v1) y cadena,
producto/cociente (reglas-v1). Selector previo a responder; guarda versión con UUID nuevo
tras reiniciar. Corrección backend según clave versionada; historial etiqueta el banco y
revisión usa preguntas originales aunque esté seleccionado otro bloque. Sin migración.
Mayor número de aciertos global entre ambos bloques no representa dominio ni dificultad.
14 pruebas locales backend aprobadas; 10 Angular; Docker/PostgreSQL 14 aprobadas y 1 omitida
(concordancia Angular ya verificada localmente). Ruff limpio y build Docker aprobado.
Servicios desplegados saludables. Sin revisión visual en navegador en este bloque.
Guía privada regenerada: 309 archivos, 162 clases, 272 operaciones. Sin IA ni conexión UPS.
Rama feature/resource-preparation. Pendiente commit humano de banco, corrección, interfaz,
pruebas y docs: feat: amplia practicas con cadena producto y cociente.
Siguiente: asignaciones del docente al estudiante y seguimiento por actividad.

## 14 de octubre — Asignaciones y seguimiento docente

Implementadas actividades de banco fijo: el docente asigna título, bloque e instrucciones
al correo exacto de una cuenta student activa; el estudiante resuelve y guarda un intento
vinculado. El docente ve cantidad de intentos y mejor resultado de sus asignaciones.
Los intentos libres permanecen privados. API con autorización por propietario, reintentos
idempotentes y límite de cuerpo; migración 0013 valida alumno/banco mediante FK compuesta.

Validación: 24 pruebas Angular aprobadas; 15 backend/PostgreSQL aprobadas y una omitida
(concordancia del banco, verificada localmente entre las 14 pruebas unitarias aprobadas).
Ruff y construcción Docker correctos. Migración aplicada y servicios saludables.
Recorrido real de navegador con cuentas ficticias: asignar reglas-v1, resolver tres preguntas,
guardar 3/3 y volver como docente; muestra un intento y mejor resultado 3/3.
La actividad de demostración permanece en la DB local. Sin llamadas IA ni conexión UPS.
Guía privada regenerada: 324 archivos, 171 clases y 292 operaciones; permanece ignorada.

Rama feature/resource-preparation. Pendiente revisión y commit humano del banco ampliado,
asignaciones, migración, interfaz, pruebas y documentación. Mensaje sugerido:
feat: amplia bancos y permite asignar practicas con seguimiento docente.
Contrato y recorrido: documentacion/api/asignaciones.md. Próximo bloque sugerido:
gestión del ciclo de actividad (cancelación/cierre) y mejora del seguimiento estudiantil.
Grupos, vencimientos, cuentas individuales verificadas y evaluación académica pendientes.

## 15 de octubre — Cierre, cancelación y reactivación de actividades

Commit anterior verificado: 3517a20. Repositorio limpio al inicio; rama
feature/resource-preparation. Implementados open/closed/cancelled y fecha del último cambio,
con migración 0014 aplicada. El docente propietario confirma el cambio en la tarjeta; el
estudiante ve el estado y conserva acceso al resumen/historial. Nuevos intentos cerrados o
cancelados se rechazan; reintentos exactos ya guardados siguen disponibles. La práctica libre
no cambia. Control de estado esperado evita sobrescribir un estado distinto desde un listado
desactualizado; no hay historial completo de transiciones. Bloqueo de fila coordina guardado
y cambio de estado. No modifica ni elimina resultados anteriores.

Pruebas: 18 backend/PostgreSQL aprobadas y una omitida (concordancia Angular, pasada en las
14 unitarias locales). Incluye permisos, CSRF, límites, idempotencia, reapertura y bloqueo
con dos conexiones PostgreSQL. 16 Angular aprobadas en Docker. El intento de ejecutar Angular
en Windows falló al iniciar workers de Vitest por timeout, sin ejecutar casos; el mismo conjunto
pasó en contenedor. Ruff y git diff --check correctos. Build de producción exitoso,
frontend/backend/PostgreSQL saludables; alembic current confirma 0014_assignment_status.
Revisión visual no realizada: control de navegador/computer-use no disponible en esta sesión.
Guía privada regenerada: 325 archivos, 172 clases, 299 operaciones; sigue excluida de Git.
Sin llamadas IA, conexión UPS ni cambios de acceso. Datos aleatorios de pruebas retirados;
la actividad de demostración anterior conserva sus resultados.

Para repetir Angular sin depender del entorno Windows:
docker build --target build -t tutoria-frontend-tests:local -f frontend/Dockerfile .
docker run --rm --network none tutoria-frontend-tests:local npm test -- --watch=false --include='src/app/modulos/estudiantes/**/*.spec.ts'

Pendiente revisión y commit humano de migración, API, interfaz, pruebas y docs:
feat: permite cerrar cancelar y reactivar actividades.
Siguiente: seguimiento por bloque/tema y filtros de actividades. Continúan pendientes grupos,
vencimientos, cuentas personales verificadas y evaluación académica.

## 15 de octubre — Textos y estructura visual

Solicitud del autor: mejorar textos desordenados y distribución general. Commit anterior
verificado 67fb536; árbol limpio al iniciar, rama feature/resource-preparation.
Cambios de presentación en login, inicio, actividades, práctica, documentos, búsqueda,
preparación, perfiles y métricas. Base SCSS compartida para títulos, lectura y paneles;
controles globales con ancho limitado, ajuste de palabras largas y acciones que envuelven.
Actividades separa formulario/listado en escritorio y los apila en ventanas estrechas;
tarjetas distinguen estado, indicaciones, destinatario, fechas y resultados. El correo demo
solo aparece en modo mock. Inicio incorpora acceso destacado a las actividades.
Práctica asignada elimina segundo h1/enlace de inicio; historial separa banco, fecha,
aciertos y revisión. Acceso ofrece dos tarjetas adaptables. Textos docentes más directos,
sin anuncios obsoletos de funciones futuras. Permisos, API y DB sin cambios.

Validación: build de producción sin advertencias de tamaño; 92 pruebas Angular aprobadas
en Docker (21 archivos). Se ajustó únicamente el doble AuthService del test de actividades
para incluir mode. Revisión visual pendiente: Computer Use se detuvo al no poder verificar
la URL de Chrome; no se continuó por otra vía. No se declara comprobación visual móvil.
Frontend local actualizado y saludable; backend/PostgreSQL saludables. Guía privada
regenerada: 326 archivos, 172 clases y 299 operaciones; exclusión Git verificada.
Sin llamadas IA ni conexión UPS. Próximo funcional: progreso por tema y filtros de actividades.
Pendiente commit humano de HTML/SCSS, ajuste del test y seguimiento:
style: mejora textos y distribucion de las pantallas.

## 25 de octubre — modelo local fuera de Git y reparación del push

El autor autorizó retirar los artefactos E5 del historial pendiente tras el rechazo
remoto por model.onnx (448,48 MiB). Se reconstruyeron únicamente los cuatro commits
no publicados, conservando autores, mensajes y cambios restantes; el commit de
navegación 6e87af6 pasa a 214ed6a. Se conserva una rama local de respaldo
backup/model-cleanup-20261025-083437; no debe publicarse porque contiene los pesos.
Los archivos permanecen en backend/models/e5-small y /backend/models/ queda
excluido mediante .gitignore. La descarga reproducible existente continúa en
app.modulos.rag.servicios.prepare_model, con revisión y SHA-256 fijados.

Verificación: árboles anterior y reconstruido idénticos fuera de backend/models;
SHA-256 locales correctos y ausencia de blobs mayores de 100 MiB antes del
push normal de feature/resource-preparation. Los commits publicados no se cambian.
No cambia código de ejecución; las siete pruebas de navegación y TypeScript
app/spec fueron aprobados antes de esta limpieza. Próximo: confirmar publicación
y revisión visual móvil/escritorio del acceso y flujo por roles.
