# Informe de fallos, correcciones y valor agregado de TutorIA

**Fecha:** 2026-11-19. **Estado:** 10 hallazgos originales corregidos y verificados localmente.

[Abrir el PDF con las 12 comparativas antes y después](informe-ui-ux-2026-11-19.pdf).

Este Markdown conserva la explicación técnica y funcional para revisión humana o por otro agente. El PDF contiene las capturas incrustadas: error anterior en rojo, solución aplicada en verde y comprobación del cambio. Para compartir las evidencias basta con enviar el PDF; no requiere imágenes externas.

## Resultado y alcance

- La auditoría inicial detectó 8 defectos y 2 mejoras. Los 10 hallazgos se corrigieron. También se resolvieron dos desbordamientos adicionales al ampliar el texto. Quedan comprobaciones dirigidas de cobertura adicional en A11Y-02 y VIS-01, detalladas abajo.
- Frontend: **162 pruebas unitarias aprobadas en 29 archivos** y compilación de producción correcta.
- E2E: **16 escenarios únicos con último resultado satisfactorio**, con backend, base de datos y embeddings reales. Una primera batería tuvo 15 aprobados y una expectativa de texto incorrecta; se corrigió y se repitieron los recorridos afectados. La ampliación de la prueba móvil detectó desbordamientos adicionales; después de corregirlos, esa prueba pasó. No se afirma una ejecución conjunta nueva de toda la batería tras cada ajuste.
- Backend: la batería anterior registró **633 aprobadas y 1 omitida**. Esta fase corrigió la interfaz y no repitió esa batería.
- Se usaron datos sintéticos. Las fuentes nuevas habilitadas por los E2E se retiraron al terminar. La generación LLM siguió deshabilitada; se verificó su bloqueo en UI y API.
- Las capturas documentan estados de prueba distintos: pueden variar los identificadores, las fechas y las cantidades de registros.

## Valor agregado por hallazgo

| ID | Cambio | Valor agregado funcional | Evidencia PDF |
| --- | --- | --- | --- |
| UX-01 | Aplicación de perfiles | El perfil guardado se convierte en una entrada operable de la preparación: el docente puede aplicarlo y revisar la dificultad efectiva. | [Páginas 3](informe-ui-ux-2026-11-19.pdf#page=3) |
| UX-03 | Protección de práctica | El estudiante controla si guarda, conserva o descarta una práctica; cancelar una salida conserva sus respuestas. | [Páginas 4](informe-ui-ux-2026-11-19.pdf#page=4) |
| A11Y-02 | Continuidad del teclado | El teclado conserva una ubicación identificable en feedback, pregunta y resultado, y alcanza las nuevas opciones. | [Páginas 5](informe-ui-ux-2026-11-19.pdf#page=5) |
| A11Y-01 | Contraste de textos | La instrucción pasa de 1,82:1 a 11,86:1; Pregrado pasa de 3,91:1 a 5,96:1 en las mediciones de contraste. | [Páginas 6, 7](informe-ui-ux-2026-11-19.pdf#page=6) |
| VIS-01 | Foco visible en móvil | El título enfocado queda completo bajo la cabecera en las cuatro anchuras comprobadas; también se corrigió el texto ampliado. | [Páginas 8](informe-ui-ux-2026-11-19.pdf#page=8) |
| UX-02 | Disponibilidad de generación | La interfaz evita un envío que el servicio no puede atender y explica la causa sin consumir cuota. | [Páginas 9](informe-ui-ux-2026-11-19.pdf#page=9) |
| UX-04 | Validación por campo | El docente reconoce qué campo corregir, conserva lo escrito y recibe una explicación específica vinculada al control. | [Páginas 10, 11](informe-ui-ux-2026-11-19.pdf#page=10) |
| VIS-03 | Ayuda de búsqueda literal | La ayuda describe el alcance real de la búsqueda y permite acceder a la recuperación por significado. | [Páginas 12](informe-ui-ux-2026-11-19.pdf#page=12) |
| VIS-02 | Estados de documentos | El docente reconoce en la lista si el material está procesado, indexado y habilitado para recursos. | [Páginas 13](informe-ui-ux-2026-11-19.pdf#page=13) |
| UX-05 | Carga automática de perfiles | La pantalla muestra los perfiles al entrar y elimina la acción manual antes necesaria para verlos. | [Páginas 14](informe-ui-ux-2026-11-19.pdf#page=14) |

## Detalle de los hallazgos y sus correcciones

### UX-01 - La personalización por perfil guardado no tiene una ruta operable desde la interfaz

**Prioridad:** P1. **Tipo:** Defecto. **Estado:** corregido y verificado localmente.

**Problema anterior:** El detalle del perfil no ofrece enlace de uso. preparar.html no contiene selector ni llamadas a loadProfiles/selectProfile/chooseProfile, aunque preparar.ts implementa esas funciones y envía profile_id si selectedProfile tiene valor. Las vistas inspeccionadas no contienen controles de perfil.

**Impacto del problema:** El docente puede registrar perfiles que no puede aplicar al flujo principal desde la UI; la función central de personalización queda desconectada.

**Cómo se reprodujo antes de corregir:**

1. Entrar como profesor.
2. Abrir Perfiles de aprendizaje.
3. Actualizar lista y abrir un perfil existente.
4. Buscar una acción para usarlo en un recurso.
5. Entrar en Recursos y buscar un selector de perfil.

**Solución implementada:** Enlace «Usar este perfil» y selector opcional en Recursos. Selección conservada al elegir asignatura y sincronizada en URL; quitar perfil recupera dificultad manual. Tema de solo lectura mientras hay perfil para evitar solicitudes incompatibles.

**Valor agregado:** El perfil guardado se convierte en una entrada operable de la preparación: el docente puede aplicarlo y revisar la dificultad efectiva.

**Criterio de aceptación:** Desde un perfil existente se puede llegar a Recursos, elegir o quitar el perfil y preparar una solicitud cuyo profile_id corresponda a la elección. La UI muestra el perfil aplicado y la dificultad efectiva; sin perfil conserva la elección manual.

**Comprobación y evidencia:**

- [PDF, página 3: Aplicar un perfil guardado](informe-ui-ux-2026-11-19.pdf#page=3). El enlace existe y abre Recursos con profile_id. El E2E comprobó el perfil y la dificultad básica en una preparación real.

**Código relacionado:**

- [frontend/src/app/profesor/recursos/preparar.ts](../../../frontend/src/app/profesor/recursos/preparar.ts).
- [frontend/src/app/profesor/recursos/preparar.html](../../../frontend/src/app/profesor/recursos/preparar.html).
- [frontend/src/app/profesor/perfiles/perfiles.html](../../../frontend/src/app/profesor/perfiles/perfiles.html).

### UX-03 - Reiniciar o salir de una práctica descarta el resultado que todavía no se ha guardado

**Prioridad:** P2. **Tipo:** Defecto. **Estado:** corregido y verificado localmente.

**Problema anterior:** La pantalla pide Guardar el resultado antes de empezar otro intento o salir, pero ambos controles permiten salir sin confirmación. Volver a practicar borra resultado y respuestas y devuelve a la primera pregunta; navegar y volver también reinicia. Se observaron cero diálogos de confirmación.

**Impacto del problema:** El alumno puede perder una práctica completa por una acción presentada como continuación normal.

**Cómo se reprodujo antes de corregir:**

1. Entrar como estudiante.
2. Responder las tres preguntas y abrir el resultado.
3. Sin Guardar resultado, pulsar Volver a practicar.
4. Repetir el recorrido y salir mediante Volver al inicio.

**Solución implementada:** Diálogo con Guardar y continuar, Seguir aquí y Descartar y continuar para reinicio, rutas y cierre de sesión. Recargar usa confirmación nativa. Cancelar conserva respuestas. Se evitan envíos concurrentes y se reutiliza el identificador del intento al reintentar; el recorrido satisfactorio verificado realizó un solo POST. Un reintento manual puede producir otra petición con el mismo identificador sin crear otro intento.

**Valor agregado:** El estudiante controla si guarda, conserva o descarta una práctica; cancelar una salida conserva sus respuestas.

**Criterio de aceptación:** Con resultado pendiente, Reiniciar y Salir ofrecen guardar, cancelar o descartar explícitamente. Cancelar conserva respuestas; guardar crea un único intento. Los E2E verifican cancelar, guardar y descartar.

**Comprobación y evidencia:**

- [PDF, página 4: Proteger resultados sin guardar](informe-ui-ux-2026-11-19.pdf#page=4). Cancelar conserva el resultado. Guardar y continuar produjo un solo POST de intento; reinicio, rutas, logout y recarga están protegidos.

**Código relacionado:**

- [frontend/src/app/estudiante/practica/practica.html](../../../frontend/src/app/estudiante/practica/practica.html).
- [frontend/src/app/estudiante/practica/practica.ts](../../../frontend/src/app/estudiante/practica/practica.ts).

### A11Y-02 - El foco no se restituye a la nueva pregunta de práctica

**Prioridad:** P2. **Tipo:** Defecto. **Estado:** corregido y verificado localmente.

**Problema anterior:** Al aparecer la pregunta 2, activeElement es BODY. El primer Tab registrado después de Siguiente sigue en BODY y no entra a las nuevas opciones. Después de Comprobar el foco también queda en BODY, aunque un Tab sí encuentra Siguiente pregunta.

**Impacto del problema:** El estudiante pierde su ubicación al avanzar y debe volver a localizar los controles. El anuncio aria-live del enunciado no sustituye la ubicación del foco.

**Cómo se reprodujo antes de corregir:**

1. Entrar como estudiante y abrir Práctica libre.
2. Elegir una respuesta y activar Comprobar.
3. Llegar a Siguiente pregunta con Tab y activarlo.
4. Comprobar el foco y continuar con Tab.

**Solución implementada:** Tras comprobar se enfoca la retroalimentación; al avanzar se enfoca la nueva pregunta y Tab llega a las opciones. El resultado recibe foco al terminar. El indicador de pregunta y tema admite varias filas para evitar desbordar al ampliar el texto.

**Valor agregado:** El teclado conserva una ubicación identificable en feedback, pregunta y resultado, y alcanza las nuevas opciones.

**Criterio de aceptación:** Completar las tres preguntas usando solo teclado mantiene un foco identificable en cada transición; las nuevas opciones son alcanzables y el objetivo enfocado queda visible.

**Alcance comprobado y cobertura pendiente:** se verificó una transición con teclado y llegada al primer radio mediante Tab; la revisión adicional comprobó el foco en las tres preguntas y el resultado. Falta registrar un recorrido completo de las tres preguntas exclusivamente con teclado para cubrir todo el criterio original.

**Comprobación y evidencia:**

- [PDF, página 5: Mantener el foco al cambiar de pregunta](informe-ui-ux-2026-11-19.pdf#page=5). DOM: foco en question-title después de Siguiente. Después de Tab, el primer radio está enfocado. La captura muestra ese segundo paso.

**Código relacionado:**

- [frontend/src/app/estudiante/practica/practica.html](../../../frontend/src/app/estudiante/practica/practica.html).
- [frontend/src/app/estudiante/practica/practica.ts](../../../frontend/src/app/estudiante/practica/practica.ts).

### A11Y-01 - La instrucción principal para elegir una respuesta tiene contraste insuficiente

**Prioridad:** P2. **Tipo:** Defecto. **Estado:** corregido y verificado localmente.

**Problema anterior:** El legend de la práctica usa rgb(242,183,5) sobre blanco, 13 px: contraste 1,82:1. Pregrado usa rgb(113,125,138) sobre rgb(245,247,250), 11,52 px: 3,91:1. Ambos son textos normales, por debajo de 4,5:1.

**Impacto del problema:** La instrucción que introduce las respuestas es difícil de leer para personas con baja visión o contraste reducido.

**Cómo se reprodujo antes de corregir:**

1. Entrar como estudiante.
2. Abrir Práctica libre.
3. Leer Selecciona una respuesta antes de elegir una opción; contrastar también Pregrado en login.

**Solución implementada:** Leyenda de práctica en navy y etiqueta Pregrado en tinta con mayor contraste. Medición de estilos calculados: ambos textos superan 4,5:1.

**Valor agregado:** La instrucción pasa de 1,82:1 a 11,86:1; Pregrado pasa de 3,91:1 a 5,96:1 en las mediciones de contraste.

**Criterio de aceptación:** Los estilos calculados de los dos textos alcanzan al menos 4,5:1. Comprobar valores sin redondear y conservar evidencia del color y fondo.

**Comprobación y evidencia:**

- [PDF, página 6: Leer la instrucción de respuesta](informe-ui-ux-2026-11-19.pdf#page=6). Colores calculados: rgb(0,54,114) sobre blanco. Relación 11,8601:1, superior al mínimo de 4,5:1 para texto normal.
- [PDF, página 7: Leer la etiqueta Pregrado](informe-ui-ux-2026-11-19.pdf#page=7). Colores calculados: rgb(85,96,110) sobre rgb(245,247,250). Contraste 5,9573:1; antes era 3,91:1.

**Código relacionado:**

- [frontend/src/app/estudiante/practica/practica.scss](../../../frontend/src/app/estudiante/practica/practica.scss).
- [frontend/src/app/inicio/login.scss](../../../frontend/src/app/inicio/login.scss).
- [frontend/src/styles.scss](../../../frontend/src/styles.scss).

### VIS-01 - La cabecera móvil tapa el título al desplazar el foco a la biblioteca

**Prioridad:** P2. **Tipo:** Defecto. **Estado:** corregido y verificado localmente.

**Problema anterior:** activeElement=library-title. A 320 y 390 px, el título empieza en y=155.34375 y termina en 189.890625; la cabecera termina en y=178.96875. Quedan tapados unos 23.6 px del título, dejando visible aproximadamente el tercio inferior.

**Impacto del problema:** Se pierde el contexto justo después de actualizar o avanzar a un resultado; el usuario recibe foco en un objetivo parcialmente oculto.

**Cómo se reprodujo antes de corregir:**

1. Iniciar como profesor.
2. Abrir /documentos con ventana de 320 o 390 px.
3. Pulsar Actualizar en Mis documentos.
4. Esperar a que termine el desplazamiento.

**Solución implementada:** Altura real de cabecera medida con ResizeObserver y margen de desplazamiento dinámico. Título íntegramente visible tras Actualizar en 320/390/768/1280 y con texto al 200% en 390. Se corrigió además la contracción y partición de texto de la marca: sin desbordamiento a 320/390 con fuente raíz al 200%.

**Valor agregado:** El título enfocado queda completo bajo la cabecera en las cuatro anchuras comprobadas; también se corrigió el texto ampliado.

**Criterio de aceptación:** Tras Actualizar y paginar Documentos, el título enfocado queda totalmente visible en 320, 390, 768 y 1280 px; repetir con fuentes y mensajes de error. No basta con que la página no desborde horizontalmente.

**Alcance comprobado y cobertura pendiente:** se midió el título después de Actualizar en 320, 390, 768 y 1280 px y con texto ampliado al 200 % en 390. Falta una comprobación dirigida de paginación, cambios de fuentes y mensajes de error para cubrir todo el criterio original.

**Comprobación y evidencia:**

- [PDF, página 8: Ver el título completo en móvil](informe-ui-ux-2026-11-19.pdf#page=8). A 390px: título en y=195,28 y cabecera hasta y=178,97; separación de 16,31px. E2E también comprobó 320,768,1280 y texto ampliado.

**Código relacionado:**

- [frontend/src/styles.scss](../../../frontend/src/styles.scss).
- [frontend/src/app/compartido/atencion-vista.service.ts](../../../frontend/src/app/compartido/atencion-vista.service.ts).
- [frontend/src/app/app.scss](../../../frontend/src/app/app.scss).

### UX-02 - Generar permanece habilitado cuando el servicio informa que la generación no está habilitada

**Prioridad:** P2. **Tipo:** Defecto. **Estado:** corregido y verificado localmente.

**Problema anterior:** GET /content/quota devuelve enabled=false, used=0 y remaining=5. La pantalla muestra Generación no habilitada y 5 de 5 solicitudes disponibles, pero el botón Generar recurso con estas fuentes está visible y habilitado. El template solo lo desactiva durante generating(). No se pulsó el CTA durante esta auditoría.

**Impacto del problema:** El usuario recibe mensajes contradictorios y puede invertir tiempo en un recorrido sin salida. La ausencia de generación real es una condición local; el fallo UX es ofrecer la acción a pesar de conocer esa condición.

**Cómo se reprodujo antes de corregir:**

1. Entrar como profesor.
2. Recursos → Mis recursos.
3. Abrir una preparación guardada con Continuar preparación.
4. Comparar disponibilidad y CTA Generar.

**Solución implementada:** Generar se deshabilita durante consulta, fallo de disponibilidad, servicio apagado o cuota agotada y explica la causa. Una petición directa sigue siendo rechazada por API sin consumir cuota.

**Valor agregado:** La interfaz evita un envío que el servicio no puede atender y explica la causa sin consumir cuota.

**Criterio de aceptación:** Con enabled=false o sin cuota, la UI explica la causa y no ofrece un envío imposible. Preparar, consultar y descargar siguen disponibles. Mantener la verificación de rechazo del servidor mediante API en la batería E2E.

**Comprobación y evidencia:**

- [PDF, página 9: Explicar y bloquear generación no disponible](informe-ui-ux-2026-11-19.pdf#page=9). E2E: enabled=false, botón visible y disabled. La API rechazó una solicitud directa con 503 y mantuvo la cuota sin consumo.

**Código relacionado:**

- [frontend/src/app/profesor/recursos/cuota.html](../../../frontend/src/app/profesor/recursos/cuota.html).
- [frontend/src/app/profesor/recursos/preparar.html](../../../frontend/src/app/profesor/recursos/preparar.html).

### UX-04 - La validación del perfil no identifica el campo ni la causa que impide guardar

**Prioridad:** P2. **Tipo:** Defecto. **Estado:** corregido y verificado localmente.

**Problema anterior:** Devuelve Revisa los campos y confirma que utilizas datos ficticios aunque la confirmación está marcada. El foco permanece en Guardar perfil y no se identifica el campo incorrecto. El método agrupa más de una docena de causas en un único mensaje. En una comprobación independiente, ALUMNO 1 y desempeño 101 mantienen Guardar deshabilitado sin explicación visible; los campos carecen de aria-invalid y aria-describedby para el error.

**Impacto del problema:** Obliga a adivinar la corrección y puede causar reenvíos repetidos, especialmente en un formulario largo.

**Cómo se reprodujo antes de corregir:**

1. Completar identificador, tema, desempeño e intentos válidos.
2. Escribir regla_potencia dos veces en Errores frecuentes.
3. Confirmar que los datos son ficticios y pulsar Guardar perfil.

**Solución implementada:** Validación específica por campo, mensajes vinculados mediante aria-describedby y aria-invalid y foco en primer error. Se conservan los datos. Probados identificador con espacios, desempeño 101 y etiquetas duplicadas.

**Valor agregado:** El docente reconoce qué campo corregir, conserva lo escrito y recibe una explicación específica vinculada al control.

**Criterio de aceptación:** Cada entrada inválida identifica el campo y la causa, preserva los datos, relaciona el mensaje mediante aria-describedby/aria-invalid y permite llegar a la corrección con teclado. Probar duplicados, identificador con espacios y desempeño mayor a 100.

**Comprobación y evidencia:**

- [PDF, página 10: Corregir etiquetas duplicadas](informe-ui-ux-2026-11-19.pdf#page=10). Se comprobó el mensaje específico y su asociación aria-describedby/aria-invalid. Corregir las etiquetas permite guardar sin rehacer el formulario.
- [PDF, página 11: Identificar errores por campo](informe-ui-ux-2026-11-19.pdf#page=11). Identificador con espacio y desempeño 101 activan errores vinculados a sus campos. Se enfoca el primer error y se conservan los valores.

**Código relacionado:**

- [frontend/src/app/profesor/perfiles/perfiles.ts](../../../frontend/src/app/profesor/perfiles/perfiles.ts).
- [frontend/src/app/profesor/perfiles/perfiles.html](../../../frontend/src/app/profesor/perfiles/perfiles.html).

### VIS-03 - La búsqueda literal de biblioteca se presenta como semántica

**Prioridad:** P2. **Tipo:** Defecto. **Estado:** corregido y verificado localmente.

**Problema anterior:** La ayuda dice Selecciona una asignatura para realizar la búsqueda semántica en el texto. El control usa /api/v1/documents/text-search, cuyo repositorio ejecuta DocumentChunk.text.icontains(text, autoescape=True), sin embeddings. La búsqueda semántica real está en otra pantalla.

**Impacto del problema:** El usuario puede interpretar ausencia de coincidencias literales como mala recuperación semántica y no descubre la herramienta adecuada para consultar conceptos equivalentes.

**Cómo se reprodujo antes de corregir:**

1. Iniciar como profesor.
2. Abrir /documentos.
3. Leer la ayuda de Buscar en el texto extraído.
4. Comparar ese control con la pantalla Buscar fuentes.

**Solución implementada:** La ayuda identifica coincidencias de texto sin distinguir mayúsculas y enlaza la búsqueda por significado. El algoritmo de búsqueda permanece literal.

**Valor agregado:** La ayuda describe el alcance real de la búsqueda y permite acceder a la recuperación por significado.

**Criterio de aceptación:** El control de biblioteca se describe como búsqueda de palabras o fragmentos; la recuperación semántica se identifica y enlaza a Buscar fuentes. No cambiar el algoritmo solo para acomodar la ayuda.

**Comprobación y evidencia:**

- [PDF, página 12: Describir la búsqueda que realmente se realiza](informe-ui-ux-2026-11-19.pdf#page=12). La búsqueda literal mantiene su algoritmo. El E2E comprobó la ayuda y que el enlace semántico lleva a /busqueda.

**Código relacionado:**

- [frontend/src/app/profesor/documentos/documentos.html](../../../frontend/src/app/profesor/documentos/documentos.html).
- [backend/app/modulos/documentos/repositorios/document_repository.py](../../../backend/app/modulos/documentos/repositorios/document_repository.py).

### VIS-02 - La biblioteca no diferencia visualmente fuentes habilitadas y retiradas

**Prioridad:** P2. **Tipo:** Mejora. **Estado:** corregido y verificado localmente.

**Problema anterior:** La fila muestra un badge verde cuando processing_status es processed y el texto Fragmento(s) · Texto procesado. La plantilla no representa index_status ni published_at. La señal es idéntica para un documento procesado habilitado, retirado o pendiente de índice.

**Impacto del problema:** Procesamiento y autorización para RAG se perciben como el mismo estado; diagnosticar por qué una materia no aporta fuentes exige abrir documentos uno por uno.

**Cómo se reprodujo antes de corregir:**

1. Iniciar como profesor.
2. Abrir /documentos con materiales procesados.
3. Consultar el estado visible de cada fila sin abrir sus detalles.

**Solución implementada:** La lista separa Texto procesado, Índice preparado y Habilitado para recursos/Sin habilitar. Se comprobó el cambio real al retirar una fuente; no se atribuye Retirado a materiales nunca habilitados.

**Valor agregado:** El docente reconoce en la lista si el material está procesado, indexado y habilitado para recursos.

**Criterio de aceptación:** Dos documentos con el mismo procesamiento y distinta habilitación se distinguen sin abrir el detalle. No atribuir Retirado a un documento que nunca estuvo habilitado.

**Comprobación y evidencia:**

- [PDF, página 13: Reconocer si un documento está habilitado](informe-ui-ux-2026-11-19.pdf#page=13). Una fuente nueva mostró Habilitado para recursos; al retirarla mostró Sin habilitar sin perder el índice. Verificado por UI y API.

**Código relacionado:**

- [frontend/src/app/profesor/documentos/biblioteca.html](../../../frontend/src/app/profesor/documentos/biblioteca.html).
- [frontend/src/app/profesor/documentos/documentos-etiquetas.ts](../../../frontend/src/app/profesor/documentos/documentos-etiquetas.ts).

### UX-05 - Los perfiles existentes requieren una carga manual cada vez que se visita la pantalla

**Prioridad:** P3. **Tipo:** Mejora. **Estado:** corregido y verificado localmente.

**Problema anterior:** Al entrar no hay botones Abrir y se muestra Consulta tus perfiles guardados con Actualizar lista. Tras pulsarlo aparecen cuatro perfiles. La pantalla Recursos sí inicia las consultas para su catálogo, por lo que cambia el patrón entre módulos.

**Impacto del problema:** Introduce un clic recurrente y puede hacer que un usuario nuevo no reconozca que ya existen observaciones guardadas.

**Cómo se reprodujo antes de corregir:**

1. Entrar como profesor con perfiles ya existentes.
2. Abrir Perfiles de aprendizaje.
3. Comparar la lista al entrar y después de Actualizar lista.

**Solución implementada:** Los perfiles se consultan al entrar y después de guardar. Actualizar sigue disponible; el reintento de paginación conserva la página solicitada.

**Valor agregado:** La pantalla muestra los perfiles al entrar y elimina la acción manual antes necesaria para verlos.

**Criterio de aceptación:** Al entrar en Perfiles se ven estados de carga, resultados, vacío o error sin un clic previo; Actualizar conserva su función de recarga.

**Comprobación y evidencia:**

- [PDF, página 14: Cargar perfiles al entrar](informe-ui-ux-2026-11-19.pdf#page=14). Captura tras entrar en Perfiles. El E2E recargó la página y encontró el perfil guardado sin solicitar carga manual.

**Código relacionado:**

- [frontend/src/app/profesor/perfiles/perfiles.ts](../../../frontend/src/app/profesor/perfiles/perfiles.ts).
- [frontend/src/app/profesor/perfiles/perfiles.html](../../../frontend/src/app/profesor/perfiles/perfiles.html).

## Cobertura adicional pendiente

- **A11Y-02:** registrar las tres preguntas completas exclusivamente con teclado. La verificación disponible combina una transición por teclado y comprobaciones de foco en las tres preguntas.
- **VIS-01:** repetir la medida del título al paginar, cambiar fuentes y mostrar errores. La evidencia disponible acredita Actualizar en cuatro anchuras y texto ampliado.
- Estas tareas amplían la cobertura del criterio original; los arreglos de foco y margen dinámico ya están implementados.

## Cómo revisar el valor agregado con otro agente

Para cada ID, contrastar el problema anterior, el impacto y la solución implementada con el código relacionado. Evaluar el resultado contra el criterio de aceptación y revisar la comparación visual en la página del PDF indicada. Separar los cambios verificados de las hipótesis que todavía necesitan estudio.

- [Pruebas E2E de los recorridos principales](../../../frontend/e2e/tutoria.spec.ts).
- [Pruebas E2E de las correcciones de UI/UX](../../../frontend/e2e/ux-corrections.spec.ts).
- Las pruebas de componentes están junto al código en archivos `.spec.ts`. Los JSON, registros de ejecución, capturas originales y herramientas de generación se conservan fuera de esta entrega, en el seguimiento local de Patricio.

## Límites de la evidencia

- Los resultados demuestran comportamiento técnico y cambios observables. No cuantifican mejora del aprendizaje, satisfacción, tiempos de tarea ni reducción de abandono.
- No se realizó un estudio SUS con participantes ni una evaluación pedagógica. No se certifica cumplimiento integral de WCAG.
- No se evaluaron generación real con proveedor LLM ni autenticación CAS institucional.
- El aumento de fuente raíz al 200 % es una prueba de texto ampliado; no equivale a todo escenario de zoom del navegador.
- Las referencias de código describen el estado de esta revisión; futuras modificaciones pueden cambiar la implementación.

## Formato de entrega

Esta carpeta contiene dos archivos: este Markdown, legible y revisable por un agente, y el PDF con todas las comparativas incrustadas. Las imágenes PNG/SVG y los registros auxiliares se conservan en la carpeta de Patricio y en la documentación local; no forman parte de esta entrega versionable.
