# TutorIA-Lucero | Plan de trabajo y estado verificable

Fecha de corte: 25 de octubre de 2026. Zona: America/Guayaquil.
Proyecto de titulación de Angel Patricio Lucero Loja. Caso principal: Cálculo Diferencial.

## 1. Dónde estamos

Existe un MVP técnico que permite al docente gestionar documentos, recuperar fuentes, preparar y generar recursos con Gemini, consultar su historial y asignar actividades. El estudiante puede consultar materiales asignados y resolver bancos fijos de ejercicios con corrección en servidor. La personalización funciona mediante perfiles sintéticos; su calidad pedagógica sigue pendiente de evaluación.

| Área | Estado al corte | Qué permite afirmar |
|---|---|---|
| Base funcional, etapas 0-7 | Cumplido técnico en entorno local/sintético | Aplicación, persistencia, acceso mock, documentos e índice RAG implementados y probados. |
| IA y recursos, etapas 8-10 | Implementado con alcance delimitado | Gemini real y cuatro recursos; OpenAI/Claude simulados; perfiles sintéticos privados. |
| Personalización, etapa 11 | Parcial | Política, prompts y pilotos existen; falta demostrar diferenciación y calidad mediante revisión humana. |
| Auditoría e historial, etapas 12-13 | Implementado técnicamente | Fuentes, snapshots, uso y fallos consultables; tarifas generales y algunos datos históricos siguen desconocidos. |
| Evaluación y cierre, etapas 14-15 | Pendiente / en curso | Herramientas offline y mejoras de UX listas; benchmark real, validación académica y cierre integral pendientes. |

Estados: Cumplido técnico = implementación y evidencia delimitadas; Parcial = hay trabajo útil y requisitos abiertos; Pendiente = falta ejecutar/cerrar; Fuera del alcance actual = decisión vigente del autor; Condicional = solo si se acuerda su inclusión. Un piloto o una prueba de formato no certifica calidad pedagógica.

Base de revisión: fuente original, sección 19 (etapas 0-15), seguimiento por hitos, continuidad, código y documentos de pruebas [E01-E25]. Revisión iniciada desde el commit humano 0c27a91, rama feature/resource-preparation, con árbol de trabajo limpio. Las cifras de pruebas son registros históricos por bloque; no se suman ni equivalen a una suite completa ejecutada hoy.

<!-- page -->

## 2. Plan completo | Etapas 0-3: base técnica

| Etapa / hito | Estado | Trabajo realizado | Evidencia de cumplimiento | Qué falta o criterio de cierre |
|---|---|---|---|---|
| 0. Preparación / H1 | Cumplido técnico | Repositorio, estructura modular, exclusión de secretos, plantilla de configuración, README y Docker. Limpieza de archivos vacíos y residuos de construcción. | .gitignore, .env.example, docker-compose.yml; E02 y E24. Git registra el bloque de limpieza en 0c27a91. | Revisar licencia, cuenta y visibilidad antes de publicar. La limpieza no sustituye revisión final de entrega. |
| 1. Backend base / H1 | Cumplido técnico | FastAPI, configuración, registro seguro, errores, API /api/v1 y health con respuestas de disponibilidad. | backend/app/main.py y api/v1/health_router.py; E02: health 200/503 y consulta real de PostgreSQL documentados. | Mantener contratos y pruebas al cambiar servicios. Validación final del entorno de entrega en etapa 15. |
| 2. Base de datos / H1 | Cumplido técnico | PostgreSQL/pgvector, SQLAlchemy, Alembic y persistencia de sesiones, documentos, vectores, generaciones, perfiles, intentos y asignaciones. Migraciones hasta 0015. | backend/alembic/versions; E05 y E21. E21 documenta 0015 aplicada y pruebas de asignación contra PostgreSQL. | Revalidar migración desde entorno limpio y restauración del respaldo elegido para cierre; conservar volúmenes. |
| 3. Frontend base / H1 | Cumplido técnico; revisión visual final pendiente | Angular standalone, rutas, shell, SCSS y movimiento reducido. Menú lateral Explorar, nombres cortos sin .component y KaTeX local antes de las vistas matemáticas. | frontend/src/app, angular.json; E24. Último bloque UX: build 327,08 kB sin advertencias y 101 casos distintos aprobados en conjunto tras corregir una prueba. | Revisar escritorio/móvil, teclado, menú y fórmulas con el navegador habilitado. No hay captura final de los últimos cambios. |

Correspondencia: estas cuatro etapas se agrupan en el hito 1. Su cierre técnico no da por terminadas las etapas académicas.

<!-- page -->

## 3. Plan completo | Etapas 4-7: acceso, corpus y RAG

| Etapa / hito | Estado | Trabajo realizado | Evidencia de cumplimiento | Qué falta o criterio de cierre |
|---|---|---|---|---|
| 4. Autenticación / H2 | Mock cumplido; CAS real fuera del alcance actual | Sesiones opacas HttpOnly, roles, logout, guards, interceptor y CSRF. Adaptador CAS preparado; demo con Profesor/Estudiante. Sustituye login/JWT del plan original. | E03: 37 pruebas backend/PostgreSQL y 15 Angular en su bloque. E23 documenta revisión remota HTTPS y sesiones. backend/app/modulos/autenticacion. | Mantener identidades ficticias compartidas en demo. CAS real requiere parámetros y autorización de TI, solo si se reincorpora al alcance. |
| 5. Documentos / H3 | Cumplido técnico | Carga PDF/DOCX/TXT, validación de extensión/MIME/tamaño, propiedad, listado, detalle y eliminación. Almacenamiento privado con hash. | E04: 57 pruebas backend/PostgreSQL y 19 Angular en su fecha. backend/app/modulos/documentos; /documentos. | Corpus docente autorizado y cotejo de contenido para evaluación. OCR no implementado; PDF escaneado queda fuera del soporte actual. |
| 6. Ingesta RAG / H4 | Cumplido técnico con material sintético | Extracción aislada, normalización, fragmentos con referencias, embeddings E5 local ONNX de 384 dimensiones e índice pgvector. Reconstrucción explícita. | E05: extracción 105 pruebas backend; índice 119 backend/PostgreSQL y 35 Angular. Reproducción con modelo real y tolerancia 1e-6 documentada. | Revisar fidelidad de fórmulas con corpus autorizado. OfficeMath y ciertos estilos heredados se rechazan; no asumir conversión matemática completa. |
| 7. Recuperación / H5 | Cumplido técnico; evaluación independiente pendiente | Búsqueda semántica top-k del corpus propio, compatibilidad de modelo/estado, fuentes y referencias. Recuperación sin LLM previa a generar. | E06: 138 backend/PostgreSQL y 38 Angular; reporte sintético y contraste recuperación exacta/HNSW. backend/app/modulos/rag. | Seleccionar consultas y juicios de relevancia independientes. La similitud no demuestra certeza ni pertinencia académica general. |

Decisión vigente: no conectar sistemas universitarios en esta etapa inicial. La evidencia local/sintética permite avanzar al MVP y preparar evaluación sin atribuir integración institucional.

<!-- page -->

## 4. Plan completo | Etapas 8-11: generación y personalización

| Etapa / hito | Estado | Trabajo realizado | Evidencia de cumplimiento | Qué falta o criterio de cierre |
|---|---|---|---|---|
| 8. Proveedores LLM / H6 | Parcial global; Gemini real implementado | Contrato común, fábrica y adaptador Gemini. OpenAI/Claude implementados y probados con transporte simulado. Reservas persistentes y límites antes de red. | E07: conexión real Gemini. E16: 107 pruebas enfocadas de adaptadores/config/API. llm_factory.py y proveedores_ia. | Autorizar modelos, presupuesto y envíos API/UI de otros proveedores si se requiere experimento C. Los adaptadores simulados no prueban acceso real. |
| 9. Generación educativa / H7 | Cumplido técnico mínimo; validación académica pendiente | Explicación, ejercicio, quiz y feedback con fuentes, validación estructural/citas, persistencia, estados y errores seguros. Preparación revisable antes de una llamada. | E08: cuatro recorridos mínimos reales. E21: quiz de cinco preguntas de integrales, 2426 tokens reportados, persistido y compartido; 97 Angular y 91 backend aprobadas, una omitida y comprobada localmente. | Revisar corrección matemática, respaldo de afirmaciones y calidad pedagógica. Ampliar escenarios largos y fallos; ejemplos/pistas/retos como tipos adicionales no están cerrados. |
| 10. Perfil académico / H8 | Cumplido técnico sintético; integración externa fuera del alcance actual | API/UI privada de perfiles ficticios, validación de observaciones, tema, nivel y propiedad. Observaciones sucesivas persistidas. | E09: 275 backend/PostgreSQL y 54 Angular. modulos/perfiles; /perfiles; migración de perfiles. Guardar no llama IA. | Acordar datos/criterios para evaluación. Vinculación con rendimiento institucional requiere una fase autorizada posterior. No hay estudiantes reales validados. |
| 11. Personalización / H9 | Parcial; núcleo de tesis por validar | Adaptación explicable de dificultad/apoyo, snapshot del perfil y prompts versionados. Piloto v3 con tres niveles. Política v2 e instrucciones v4 para nuevas preparaciones. | E10: 292 backend y 56 Angular. E11: tres respuestas reales y 7365 tokens conocidos; diferenciación limitada. E12: 58 pruebas de orientación v4 sin nuevas inferencias. | Evaluación prospectiva v4 con casos completos y rúbrica humana. Comprobar diferencias justificadas conservando objetivo/fuentes. No se ha demostrado mejora del aprendizaje. |

Control de generación documentado: cinco inicios globales por día UTC, uno simultáneo y un minuto entre inicios, incluidos fallos reservados. Presupuesto local autorizado USD 0 bajo nivel gratuito confirmado históricamente. Este informe no consulta ni verifica tarifas o facturación actuales.

<!-- page -->

## 5. Plan completo | Etapas 12-15: evidencia y cierre

| Etapa / hito | Estado | Trabajo realizado | Evidencia de cumplimiento | Qué falta o criterio de cierre |
|---|---|---|---|---|
| 12. Trazabilidad / H10 | Implementado técnicamente; cobertura delimitada | Snapshots de petición, prompt/hash/versiones, fuentes, perfil, modelo, límites, estados, consumo y latencia. Fallos seguros y datos desconocidos conservados. | E13: auditoría, 296 backend y 61 Angular en su bloque. E15: base de costo gratuito condicionada versionada; 40 backend y 3 Angular enfocadas. | Tarifas generales y datos históricos no registrados siguen pendientes/desconocidos. La estimación no certifica factura. Purga opcional; separar reservas antes de implementarla. |
| 13. Historial y métricas / H10 | Cumplido técnico del alcance actual | Historial privado paginado, reapertura sin IA, auditoría, exportación JSON y métricas de estados/tokens/latencia con cobertura explícita. Cupo diario visible. | E14: métricas con 295 backend y 59 Angular. E15 y E21: exportación/configuración y cuota. /recursos, /metricas y GET /content/quota. | Consolidar las medidas necesarias para el experimento; mantener desconocidos explícitos. Seguimiento de aprendizaje es distinto de métricas de uso de IA. |
| 14. Evaluación / H11 | Parcial instrumental; benchmark real pendiente | Diseño A/B/C, preparación directa/RAG, manifiestos, registro offline, plantillas de revisión humana y recorrido simulado OpenAI/Claude. | E17-E18: CLI reproducibles; simulación con 143 pruebas enfocadas. E11 es piloto, no benchmark. modulos/evaluacion. | Acordar diseño, corpus, rúbrica, modelos, orden, repeticiones y presupuesto; ejecutar, revisar y analizar resultados reales, incluidos fallos y abstenciones. |
| 15. Endurecimiento / H12 | En curso; cierre integral pendiente | Pruebas por bloque, seguridad, manuales, scripts de respaldo/demo, mejoras UX, fórmulas y limpieza. Comentarios concisos y plan consolidado en este bloque. | E19-E25, README, contratos API, continuidad y pruebas de cada hito. Código y reportes permiten reconstruir el avance. | Regresión final proporcional, recorrido visual docente/alumno, revisión de accesibilidad, restauración verificable, manuales finales, resultados e informe de tesis. Aprobación académica pendiente. |

Ubicación actual: consolidación del MVP y etapas 11-13, con herramientas preparatorias de etapa 14 y tareas transversales de etapa 15. La evaluación formal y el cierre no se consideran terminados por tener carpetas, scripts o pilotos.

<!-- page -->

## 6. Trabajo añadido al itinerario original

Estas mejoras apoyan el MVP y su uso. Se registran como ampliaciones transversales, sin renumerar las etapas originales ni confundirlas con resultados de investigación.

| Bloque | Estado | Resultado implementado / prueba | Pendiente y límite |
|---|---|---|---|
| Práctica estudiantil | Cumplido técnico del banco fijo | Dos bloques de tres ejercicios de derivadas, feedback, intento persistente, historial privado y corrección backend. E19: 13 unitarias, 13 integración y 13 Angular en el primer bloque persistente. | Ampliar contenidos según necesidad; no representa evaluación institucional ni personalización estudiantil integral. |
| Asignación y estados | Cumplido técnico | Docente asigna bancos; estudiante entrega; docente consulta intentos/mejor resultado. Cierre, cancelación y reactivación conservan intentos. E20: 18 backend y 16 Angular para el ciclo de estados. | Seguimiento por tema/bloque y filtros. Grupos, vencimientos y cuentas individuales no están cerrados. |
| Recursos generados compartidos | Cumplido como material de estudio | Actividades pueden compartir recurso propio finalizado con fuentes y soluciones; detalle restringido por asignación. E21: HTTP docente/alumno, permisos, CSRF e idempotencia verificados; migración 0015. | No hay entrega/corrección de quizzes dinámicos ni registro de lectura. Elegir explícitamente si esa ampliación se incorporará al plan. |
| UX docente y matemáticas | Implementado; revisión visual pendiente | Flujo Documentos -> Recursos -> Actividades; perfiles opcionales, menú lateral único Explorar y KaTeX síncrono local. E24; guía E22. | Recorrido final en móvil/escritorio. Mantener diferenciados Actividades asignadas, Práctica libre y Uso de generación. |
| Demo remota | Verificada históricamente; no se afirma activa | Túnel HTTPS por enlace y roles ficticios compartidos; sesiones Secure/HttpOnly, CSRF, logout y restauración local documentados. E23. | No ofrece cuentas individuales ni privacidad entre visitantes del mismo perfil ficticio. Reabrir solo cuando se necesite revisar la demo. |
| Limpieza y legibilidad | Limpieza cumplida; documentación de código en este bloque | Retirados 37 archivos .gitkeep y seis carpetas vacías. Cinco directorios generados a Papelera (~4,3 MB). Exclusiones Docker para modelos/registros; nombres frontend cortos. E24. | Mantener comentarios breves en reglas y límites. Evitar describir cada línea o generar documentación redundante. |

<!-- page -->

## 7. Siguientes bloques propuestos para ajustar el plan

El orden siguiente es una propuesta de ejecución basada en los pendientes actuales. No añade fechas ni presupuestos no acordados. El ajuste académico de alcance sigue abierto para revisión del autor y tutor.

| Orden | Bloque y etapas | Trabajo concreto | Dependencias / decisiones | Evidencia para declararlo cumplido |
|---|---|---|---|---|
| N1 | Consolidar MVP / 3, 9, 15 | Revisar flujo docente/alumno, móvil, teclado, menú y fracciones/integrales. Corregir defectos reproducibles y confirmar manuales. | Navegador habilitado; materiales sintéticos del flujo actual. | Lista de recorridos con resultado, capturas vigentes y pruebas de regresión afectadas. |
| N2 | Seguimiento estudiantil / ampliación | Diseñar seguimiento por tema/bloque y filtros de actividades. Definir si habrá entrega/corrección de recursos generados o solo consulta de materiales. | Acordar alcance antes de nuevas entidades/migraciones. No bloquear el benchmark con ampliaciones opcionales. | Contrato y recorrido docente/alumno con persistencia, permisos y criterios por funcionalidad. |
| N3 | Protocolo académico / 7, 11, 14 | Fijar corpus autorizado, consultas, perfiles, objetivos, rúbrica, muestras/repeticiones y tratamiento de fallos. Seleccionar dimensiones de evaluación. | Acuerdo autor/tutor; corpus y revisores. Recursos disponibles y presupuesto explícito. | Protocolo versionado y revisable, corpus y controles fijados antes de enviar nuevas generaciones. |
| N4 | Validar personalización / 11, 14-B | Ejecutar evaluación prospectiva de la política v2/prompt v4 con alto/medio/dificultades y revisión humana de apoyo/dificultad/fidelidad. | N3; cupo y proveedor autorizados. No alterar retrospectivamente pilotos v2/v3. | Resultados completos, rúbrica aplicada, fallos incluidos y conclusión sustentada sobre diferenciación. |
| N5 | Comparaciones reales / 14-A y C | Comparar directo/RAG; incorporar proveedores adicionales si se acuerda. Registrar latencia, tokens, cobertura y costo conocido/desconocido. | N3; autorizar modelos/acceso/presupuesto de C. N4 puede compartir controles del protocolo. | Pares comparables, trazas, revisión humana y análisis reproducible; limitaciones explícitas. |
| N6 | Cierre / 15 y H12 | Regresión final, seguridad del alcance, respaldo/restauración, manuales, resultados, discusión e informe. Preparar entrega reproducible. | N1 y experimentos acordados terminados; decisiones de licencia/publicación si aplica. | Lista de aceptación final, versiones/commit revisados, artefactos de evidencia e informe validado por sus responsables. |

Fuera del alcance actual: CAS real y recepción institucional. Condicionales: segunda asignatura (D), OCR, grupos/vencimientos, nuevas clases de recurso y purga. Se incorporan solo mediante una decisión explícita de alcance.

<!-- page -->

## 8. Evaluación pendiente y decisiones necesarias

| Experimento | Qué compara | Disponible hoy | Falta para ejecutarlo/cerrarlo |
|---|---|---|---|
| A. Directo frente a RAG | Mismo objetivo/tipo/modelo con y sin fuentes recuperadas. | Preparación directa, pares/manifiestos offline, registro y simulación; flujo RAG real del MVP. | Protocolo fijado, generaciones comparables reales, revisión de fidelidad/pertinencia y análisis de fallos. |
| B. Perfiles | Mismo tema/recurso con rendimiento alto, medio y dificultades. | Perfiles, adaptación, snapshots y pilotos v2/v3. Nuevas instrucciones v4 probadas técnicamente. | Evaluación prospectiva v4, rúbrica humana, repeticiones acordadas y análisis de diferenciación. |
| C. Proveedores | OpenAI, Gemini y Claude con controles compartidos. | Gemini real; OpenAI/Claude con pruebas simuladas y fábrica común. | Elegir modelos equivalentes para el diseño, autorizar acceso/presupuesto e integración de envíos; ejecutar y revisar. |
| D. Portabilidad | Cálculo Diferencial y otra asignatura. | Diseño original lo condiciona al tiempo disponible. | Decidir inclusión, elegir corpus/criterios y ejecutar después de las comparaciones principales. |

Propuesta de dimensiones: fidelidad a fuentes, exactitud matemática, pertinencia respecto del objetivo, dificultad/apoyo, calidad pedagógica, personalización, estabilidad, abstenciones/fallos, latencia, tokens y costo con cobertura conocida. Las puntuaciones deben proceder de revisores y criterios acordados; las herramientas offline solo validan y organizan el registro.

Decisiones abiertas para la revisión del plan: (1) objetivo principal medible del MVP y tesis; (2) corpus y permisos; (3) revisores/rúbrica y número de casos/repeticiones; (4) modelos y presupuesto; (5) alcance estudiantil adicional; (6) inclusión de D y otras ampliaciones; (7) licencia/publicación y condiciones de entrega. Este informe registra preguntas de alcance, sin inventar respuestas o aprobaciones.

Comentarios de código: añadidos o ajustados en 95 archivos (60 Python y 35 TypeScript), sobre responsabilidades, propiedad, sesiones, reserva antes de red, concurrencia, idempotencia, estados, desconocidos y tratamiento matemático seguro. Verificada equivalencia de estructura en 138 módulos Python y 69 archivos TypeScript; Ruff aprobado. Los nombres y tipos expresivos no requieren un comentario por línea. Detalle del bloque en continuidad.

<!-- page -->

## 9. Catálogo de evidencias | Base y generación

Las rutas son relativas a la raíz del repositorio. Cada referencia conserva su fecha y alcance. Los reportes y capturas históricos muestran la implementación de su momento; la interfaz actual puede haber cambiado. Se contrastaron con el código presente, sin nuevas llamadas IA ni conexión institucional en esta elaboración.

| ID | Documento / ubicación | Qué demuestra y límite |
|---|---|---|
| E01 | documentacion/investigacion/plan_implementacion_fuente.txt; documentacion/PLAN_DE_TRABAJO.md | Fuente original, etapas 0-15, hitos 1-12 y cambios de alcance. El original no se modifica. |
| E02 | documentacion/pruebas/hito_01.md | Base Angular/FastAPI/PostgreSQL/Docker; health y comandos. No cubre evaluación académica. |
| E03 | documentacion/pruebas/hito_02.md; documentacion/decisiones_tecnicas/0002-sso-ups.md | Acceso mock, adaptador CAS, sesiones y roles; actualizaciones de demo. Sin CAS real. |
| E04 | documentacion/pruebas/hito_03.md | Documentos propios, validación, permisos y estilo. Material sintético. |
| E05 | documentacion/pruebas/hito_04_extraccion.md; documentacion/pruebas/hito_04_indice.md | Extracción, segmentación, modelo real local y vectores reproducibles. |
| E06 | documentacion/pruebas/hito_05.md; documentacion/pruebas/hito_05_recuperacion.json | Recuperación exacta/HNSW con corpus sintético. Falta relevancia independiente. |
| E07 | documentacion/pruebas/hito_06_proveedores.md; documentacion/pruebas/hito_06_gemini_real.md | Contrato/fábrica y primera conexión Gemini real. No demuestra integración real de todos los proveedores. |
| E08 | documentacion/pruebas/hito_07_cuatro_recursos.md; documentacion/api/contenidos.md | Cuatro recorridos mínimos reales y sus límites. |
| E09 | documentacion/pruebas/hito_08_perfiles.md; documentacion/api/perfiles.md | Validación/persistencia/consulta de perfiles sintéticos privados. |
| E10 | documentacion/pruebas/hito_09_personalizacion.md; documentacion/api/personalizacion.md | Política y snapshot de adaptación; pruebas técnicas, no eficacia pedagógica. |
| E11 | documentacion/pruebas/hito_09_piloto_v3.md; documentacion/pruebas/hito_09_piloto_v3_completo.json | Tres resultados reales, consumo y limitaciones observadas. No son benchmark completo. |
| E12 | documentacion/pruebas/hito_09_orientacion_v4.md | Política v2 / instrucciones v4 comprobadas sin nuevas inferencias en ese bloque. |

<!-- page -->

## 10. Catálogo de evidencias | Auditoría, evaluación y MVP

| ID | Documento / ubicación | Qué demuestra y límite |
|---|---|---|
| E13 | documentacion/pruebas/hito_10_auditoria.md; documentacion/api/auditoria_recursos.md | Consulta propia de versiones, hash, fuente, consumo y estados. |
| E14 | documentacion/pruebas/hito_10_metricas.md; documentacion/api/metricas.md | Métricas privadas, cobertura y desconocidos explícitos. |
| E15 | documentacion/pruebas/hito_10_costo_condicionado.md; hito_10_configuracion_ejecucion.md; hito_10_exportacion_historial.md (misma carpeta) | Estimación condicionada versionada, límites guardados y exportación JSON. No prueba facturación. |
| E16 | documentacion/pruebas/hito_11_adaptadores_openai_claude.md | Adaptadores probados con HTTP simulado. Sin credenciales/envíos reales. |
| E17 | documentacion/pruebas/hito_11_matriz_experimental.md; hito_11_pares_offline.md; hito_11_registro_pares.md; hito_11_revision_humana_pares.md (misma carpeta) | Diseño, manifiestos, registro y revisión declarada. La ejecución académica sigue pendiente. |
| E18 | documentacion/pruebas/hito_11_simulacion_pares.md | Recorrido experimental con transporte sintético, sin red ni base de datos. |
| E19 | documentacion/api/practica.md; backend/tests/unitarios/test_practice_validation.py | Banco fijo, corrección servidor, intentos y revisión. Ver continuidad para los bloques históricos. |
| E20 | documentacion/api/asignaciones.md; backend/tests/integracion/test_assignments.py; documentacion/CONTINUIDAD.md | Asignación, propiedad, resultados y ciclo de estados, ampliado posteriormente a materiales. |
| E21 | documentacion/pruebas/revision_integrales_asignaciones.md | Quiz real de cinco preguntas, asignación de recurso, cuota y pruebas HTTP/backend/UI. |
| E22 | documentacion/manuales/flujo_docente.md; documentacion/manuales/guia_docente_mvp.md | Recorrido docente y alcance de las pantallas. |
| E23 | documentacion/manuales/demo_remota_gratuita.md | Operación/revisión histórica del túnel HTTPS y sus límites. No se afirma activo hoy. |
| E24 | documentacion/CONTINUIDAD.md; documentacion/arquitectura/navegacion.md | Nombres cortos, menú/KaTeX, flujo docente, limpieza y verificación por bloque. |
| E25 | documentacion/manuales/manual_tecnico_local.md; infraestructura/scripts/backup-local.ps1; infraestructura/scripts/verify-local-backup.ps1 | Operación y procedimiento de respaldo/verificación. Validar restauración elegida para el cierre final. |

Estado documental: este resumen es la fotografía vigente y la base para revisar el plan. El seguimiento anterior conserva historia; las notas antiguas de pendientes se interpretan según su fecha. No se asigna un porcentaje global de tesis ni una aprobación académica. Próximo punto de control: N1 y acuerdo de protocolo N3, con N2 delimitado como ampliación funcional.
