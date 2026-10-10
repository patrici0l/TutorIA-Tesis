# Guía docente del MVP local

Versión de trabajo del 10 de octubre de 2026. Describe funciones implementadas; pendiente
de validación de usabilidad con el autor. No certifica calidad pedagógica ni cierra el proyecto.

## Acceso y alcance

Con el entorno iniciado, abre http://localhost:4200/login y pulsa **Iniciar sesión con
cuenta UPS**. En esta etapa el acceso es una simulación local: no conecta con la universidad
ni requiere una contraseña real. Usa únicamente materiales y perfiles ficticios de prueba.

Documentos, búsqueda, perfiles, generación y métricas son espacios de docente/admin sobre
sus datos propios. Si aparece **Espacio docente**, la sesión corresponde a estudiante:
el responsable local debe seleccionar la identidad docente de demostración y debes cerrar
sesión y volver a entrar. No hay un botón para que el estudiante eleve sus permisos.
La preparación técnica del entorno está en el [README](../../README.md).

## Recorrido sin consumir Gemini

1. Abre **Documentos** (`/documentos`). Introduce un título, elige PDF, DOCX o TXT
   de hasta 10 MiB y pulsa **Guardar documento**. El archivo debe ser propio o autorizado.
2. En **Mis documentos**, abre **Detalles** y pulsa **Procesar documento**. Comprueba
   los fragmentos y sus referencias; un PDF sin texto extraíble no se convierte mediante OCR.
3. Pulsa **Preparar índice vectorial** y espera a que termine. El modelo de indexación
   es local. Procesar y crear el índice son pasos distintos; cargar el archivo no basta.
4. En **Buscar fuentes** (`/busqueda`), escribe una consulta, por ejemplo «tasa de cambio
   instantánea». Puedes indicar máximo de fragmentos y similitud mínima. Lee los resultados
   en su contexto; similitud alta no demuestra que una afirmación sea correcta.
5. Opcionalmente, abre **Perfiles** (`/perfiles`) y registra una **Nueva observación**:
   identificador ficticio, tema, desempeño, intentos, nivel informado, apoyo y errores.
   Confirma que los datos son sintéticos y pulsa **Guardar perfil sintético**. El nivel
   se conserva como lo informas: la aplicación no deduce una nota ni diagnostica al alumno.
6. Abre **Preparar recursos** (`/recursos`), define tema y objetivo concreto. Elige
   explicación, ejercicio, quiz o feedback. Quiz requiere 1–5 preguntas; feedback requiere
   una respuesta ficticia para revisar, que se guardará con la preparación.
7. Para adaptar el apoyo, pulsa **Consultar mis perfiles** y selecciona uno del mismo
   tema. Revisa el motivo y dificultad aplicada. Con **Usar dificultad manual** decides
   la dificultad sin perfil; el tipo de recurso sigue siendo tu elección.
8. Pulsa **Preparar y revisar fuentes**. Se guardan solicitud y hasta tres fragmentos
   recuperados. Comprueba contenido, referencias y adaptación antes de generar.

Estos pasos no envían una solicitud a Gemini. Tampoco lo hacen consultar historial,
perfiles o métricas. Las preparaciones ya creadas para experimentos tienen IDs y protocolos
propios: no las uses para ensayar ni las vuelvas a generar fuera de ese procedimiento.

## Generación explícita

Solo al pulsar **Generar con Gemini · nivel gratuito** se envían las instrucciones y el
contexto preparado al proveedor. La etiqueta depende de la configuración gratuita
confirmada por el operador; no verifica la facturación de Google.

La demostración permite cinco reservas por día UTC para todo el entorno, una generación
simultánea y al menos un minuto entre inicios. Los fallos también cuentan. Medianoche UTC
corresponde a las 19:00 de Guayaquil; el límite de Google puede ser diferente. No aumentes
la cuota local para eludir un límite del proveedor.

Una preparación enviada no se vuelve a enviar. Si la pantalla pierde conexión, abre
**Mis recursos** antes de realizar otra acción: el backend pudo haber terminado la solicitud.
No prepares otra copia solo para repetir un fallo de un experimento. Fuera de protocolos,
una nueva preparación es una solicitud distinta y consume otro intento al generarla.

Un recurso generado pasó validación de estructura y pertenencia de citas. Revisa todavía
las matemáticas, el respaldo real de cada afirmación y la adecuación del apoyo antes de usarlo.

## Historial y métricas

En **Mis recursos**, dentro de `/recursos`, recupera preparaciones y resultados con sus
fuentes originales. Abre **Ver trazabilidad de este recurso** para fechas, modelo,
versiones, tokens, latencia, costo condicionado y código de fallo. Consultar no genera de nuevo.

`/metricas` resume tus propias ejecuciones, sus estados y cobertura de mediciones.
**Desconocido** no significa cero. Tokens totales son los reportados, no una suma inferida.
La latencia del proveedor no incluye todo el recorrido de la aplicación. Un costo de cero
condicionado al nivel gratuito no es un comprobante de factura. Las métricas no miden aprendizaje.

## Situaciones habituales

| Situación | Qué revisar |
|---|---|
| No aparecen fuentes | Documento propio procesado e indexado, consulta pertinente y umbral de búsqueda. No generar sin fundamento suficiente. |
| Procesamiento o índice interrumpido | Abrir Detalles y Actualizar estado. La interfaz ofrece reintento tras el plazo correspondiente; no borrar el archivo para forzarlo. |
| Fuentes cambiaron al generar | Revisar materiales y preparar de nuevo; no sustituir las fuentes de una traza ya enviada. |
| Límite diario o solicitud muy reciente | Esperar al cupo o intervalo indicado. Un fallo también ocupa reserva. |
| `llm_incomplete` | Salida truncada por límite de tokens; no hay recurso publicable. Conservar el fallo y revisar el protocolo con el responsable. |
| `llm_timeout` | Se agotó la espera; consumo puede quedar desconocido. Revisar historial, sin reintento automático. |
| Recurso rechazado por formato o citas | No se publica como válido; revisar la evidencia del fallo, sin asumir calidad por una respuesta parcial. |
| Acceso o sesión caducados | Volver a iniciar sesión; no introducir claves de IA ni contraseña institucional en formularios de TutorIA. |

Eliminar un documento exige confirmación en su pantalla. No elimina automáticamente las
fuentes históricas guardadas en preparaciones anteriores. No borres corpus usado en una
evaluación en curso. Al terminar la sesión, usa la acción de cerrar sesión.

## Verificación de esta guía

Rutas, etiquetas y condiciones cotejadas con las plantillas Angular y contratos de API
vigentes el 10 de octubre. No se repitió un recorrido completo ni se consumió Gemini para
redactarla. La revisión con un docente real y las capturas finales siguen pendientes.
