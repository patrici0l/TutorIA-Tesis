# TutorIA: integración mínima con ADAPTIA

Guía de implementación y entrega para Patricio. Consolida el contrato del kickoff y
los campos enviados por el consumidor de ADAPTIA; describe el comportamiento implementado.

El [manual visual de Moodle](manual-moodle-tutoria.md) acompaña esta guía con un PDF
autónomo: diagramas, capturas de Playwright señaladas y ejemplos paso a paso.

## Documentación de referencia y decisiones

El kickoff de Patricio define los ocho campos del cuerpo y la respuesta
`success/data/metadata/tracking`; el cliente HTTP existente en
`moodle-worker/ambiente-local/backend/pipeline.py` y `mock_contracts.py` utiliza ese
contrato en su demostración. Esa es la base de esta primera integración.

El Hito A contiene un ejemplo anterior con cinco campos. La propuesta
`jefferson-sagbay/INTEGRACION-ARQUITECTURA.md` plantea además objetivos, tipos de
recurso y fuentes autorizadas; esos parámetros todavía no forman parte de este POST.
El diseño V3 conserva RAG como objetivo de la tesis. El modo directo de esta API no
equivale a entregar toda esa funcionalidad ni sustituye las rutas RAG de TutorIA.

El plan de trabajo PDF de Patricio registra una comprobación anterior con Gemini y
presupuesto autorizado de IA en USD 0. Las pruebas de esta iteración usaron un proveedor
controlado. En la configuración local la clave sigue vacía y la IA está apagada;
el modelo inicial preparado es `gemini-3.1-flash-lite`. Falta verificar una generación real;
no se interpreta el historial del PDF como autorización para activar un proveedor.

`POST /api/v1/tutoria/generate-content`

Esta API recibe el perfil y contexto que envía ADAPTIA, conserva la dificultad elegida por el motor y devuelve `success`, `data`, `metadata` y `tracking`. La versión inicial produce texto estructurado con explicación, ejemplo y ejercicio. No recupera documentos ni produce imágenes o audio; las rutas de documentos/RAG de la web se conservan independientes.

## Configuración del servicio

En el archivo privado `licencias/secure_data.env` para Docker, o `licencias/backend.env` para ejecución directa:

```dotenv
ADAPTIA_ENABLED=true
ADAPTIA_SERVICE_TOKEN=<secreto-aleatorio-de-32-a-512-caracteres-ASCII-sin-espacios>
```

El token identifica al backend de ADAPTIA. Es independiente de las claves del proveedor y de la sesión de profesor; se guarda en los dos servidores que se comunican. No se incluye en este repositorio ni en el navegador de los estudiantes.

La integración está deshabilitada por defecto. Activarla no activa llamadas a un proveedor. Para generar de verdad, el operador debe configurar también `LLM_ENABLED`, proveedor, modelo, clave y confirmación de presupuesto según el proveedor ya soportado por TutorIA. Las pruebas usan un proveedor controlado; no requieren una clave real ni consumen cuota externa.

Después de cambiar la configuración, reconstruir el backend y aplicar la migración aditiva `0018_adaptia_integration` antes de atender llamadas:

```sh
docker compose --env-file licencias/secure_data.env build backend
docker compose --env-file licencias/secure_data.env run --rm migrate
docker compose --env-file licencias/secure_data.env up -d --no-deps --wait backend
```

Se conserva la base de datos y sus volúmenes. La nueva tabla `generaciones_adaptia` registra solicitudes, hashes, estado, proveedor, uso conocido y respuesta. No guarda el token de servicio ni la clave del proveedor.

## Probar desde Swagger

Abrir `http://localhost:4200/api/v1/docs` y buscar **Integración ADAPTIA**.

Swagger y `/api/v1/openapi.json` muestran exclusivamente este POST, su autenticación,
campos y respuestas. Las otras rutas de la aplicación quedan fuera de esta documentación.

1. Pulsar **Authorize** e introducir solo el token de servicio en **ADAPTIABearer**, sin escribir `Bearer`. Swagger añade ese prefijo.
2. Abrir el POST y pulsar **Try it out**. No requiere sesión de profesor ni `x-prototipo-client`.
3. Indicar `X-Request-ID`, un identificador ASCII único para esa solicitud. Mantenerlo al reintentar exactamente el mismo cuerpo.
4. Usar el ejemplo de perfil sintético y ejecutar. `X-Session-ID` es opcional; si falta, el servidor genera uno.

Si el LLM sigue apagado, una solicitud válida y autenticada devuelve HTTP503 con `success:false` y `AI_SERVICE_UNAVAILABLE`. Eso verifica el contrato y el bloqueo de generación; no representa una generación exitosa.

## Solicitud

Máximo 16384 bytes. No acepta campos adicionales ni selección de proveedor/modelo desde el cliente.

```json
{
  "student_id": "stud_hash_abc123xyz",
  "topic": "derivadas",
  "difficulty": 5,
  "preferred_modality": "visual",
  "context": "Explicar la derivada como tasa de cambio con un ejemplo guiado.",
  "performance_history": [
    {"topic": "regla de la potencia", "score": 60, "time": "2026-11-19T10:00:00Z"}
  ],
  "known_concepts": ["funciones"],
  "gaps": ["regla de la potencia"]
}
```

- `student_id`: identificador seudonimizado por ADAPTIA, de 8 a 128 caracteres ASCII alfanuméricos, guion o guion bajo. El llamador es responsable de seudonimizarlo; no enviar nombre ni correo.
- `difficulty`: entero de 1 a 10. Se transmite al generador como lo decide el motor; no se convierte a la escala de tres niveles de la web.
- `preferred_modality`: `visual`, `textual` o `auditory`; orienta el texto. La modalidad auditiva devuelve un guion, no audio.
- `context`: entre 3 y 2000 caracteres.
- `performance_history`: hasta 50 eventos; `score` entre 0 y 100 y fecha ISO8601 con zona horaria.
- `known_concepts` y `gaps`: hasta 20 textos de 160 caracteres por lista, sin entradas vacías ni controles.

## Respuesta exitosa

Ejemplo ilustrativo; las mediciones de una llamada real proceden del proveedor, no de estos valores:

```json
{
  "success": true,
  "data": {
    "content": "Idea\nLa derivada mide el cambio...\n\nEjemplo\n...\n\nPractica\n...",
    "structure": {
      "title": "Derivadas",
      "sections": [
        {"type": "explanation", "title": "Idea", "text": "La derivada mide el cambio..."},
        {"type": "example", "title": "Ejemplo", "text": "Si f(x)=x² entonces f'(x)=2x."},
        {"type": "exercise", "title": "Practica", "text": "Calcula la derivada de x³."}
      ]
    },
    "metadata_generation": {
      "model_used": "modelo-configurado",
      "tokens_used": null,
      "generation_time_ms": 1200
    }
  },
  "metadata": {
    "timestamp": "2026-11-19T10:00:01Z",
    "processing_time_ms": 1250,
    "api_version": "v1.0",
    "mode": "direct",
    "replayed": false
  },
  "tracking": {
    "request_id": "req_adaptia_001",
    "student_id_hash": "stud_hash_abc123xyz",
    "session_id": "session_adaptia_001"
  }
}
```

`tokens_used` conserva el total informado por el adaptador. Si ese total falta,
permanece `null`, aunque se conozcan entrada y salida: no se suman como si fueran
el total, porque pueden faltar otras categorías. Las mediciones parciales se
conservan en la traza. Un total explícito de cero sí se conserva como cero.
Gemini distingue entrada, candidatos, razonamiento y total en su
[contrato oficial de uso](https://aistudio.google.com/api-reference/generate-content#Resource:GenerateContentResponse).

`content` se compone en el servidor a partir de las secciones validadas. Los textos
deben mostrarse como texto, no como HTML confiable; la validación estructural no
acredita exactitud pedagógica.

## Reintentos y cuota compartida

| Situación con el mismo X-Request-ID | Resultado |
| --- | --- |
| Mismo cuerpo y éxito ya guardado | HTTP200, mismo contenido y `metadata.replayed:true`; sin llamar al proveedor. |
| Otro cuerpo | HTTP409; no se envía. |
| Solicitud todavía en curso | HTTP409; no se inicia una segunda generación. |
| Solicitud anterior fallida | HTTP409. Un nuevo envío requiere otro ID y puede consumir cuota. |

El servidor confirma la reserva en PostgreSQL antes de llamar al proveedor. Un fallo posterior también cuenta como intento: puede haber consumo aunque no llegue una respuesta. Los replays no crean otra reserva. `metadata_generation` conserva la medición de la generación original; no volver a contabilizarla como gasto de un replay.

La integración y la web comparten límite diario, exclusión de solicitudes simultáneas y espera mínima entre envíos. Se mantiene la política existente de TutorIA; abrir otro endpoint no crea otro cupo. Las reservas interrumpidas durante más de 90 segundos se cierran como fallidas, sin reenvío automático ni cambio de proveedor.

## Errores

Los errores de las llamadas POST al endpoint incluyen `success:false`, `error`, `metadata` y `tracking`, con `X-Request-ID` en la cabecera de respuesta. No incluyen entradas crudas, claves ni errores internos del proveedor.

| HTTP | Código | Causa |
| --- | --- | --- |
|400/422|`INVALID_REQUEST`|Correlación, JSON o campos inválidos.|
|401|`AUTHENTICATION_FAILED`|Bearer ausente o incorrecto.|
|409|`INVALID_REQUEST`|Conflicto o estado no reutilizable de X-Request-ID.|
|413|`INVALID_REQUEST`|Cuerpo demasiado grande.|
|429|`RATE_LIMIT_EXCEEDED`|Cupo o espera entre generaciones.|
|502/503|`AI_SERVICE_UNAVAILABLE`|Integración/proveedor apagado, fallo del proveedor, salida inválida o trazabilidad no disponible.|
|500|`INTERNAL_SERVER_ERROR`|Fallo no previsto, sin detalles sensibles.|

## Alcance de esta iteración

Los fixtures `backend/tests/fixtures/adaptia_requests.json` conservan tres solicitudes sintéticas del consumidor ADAPTIA existente para verificar el contrato. Las pruebas de integración usan PostgreSQL real y un proveedor controlado para comprobar persistencia, correlación, replay, concurrencia y cuota.

El backend de Moodle dispone ahora de un cliente separado para esta API y la clase
PHP del plugin puede invocarlo explícitamente. El POST provisional501 de la pasarela
se sustituyó por esa conexión. Usa un token de TutorIA independiente del token interno
Moodle→ADAPTIA, timeout70s y una red privada entre backends. El overlay opcional
`infraestructura/docker/compose.adaptia.yml` conecta este backend a la red externa
`adaptia-tutoria`, con alias `tutoria-api`.

La pasarela conserva el identificador de Moodle y registra en
`tracking.upstream_request_id` el identificador separado por docente que recibe
TutorIA. No reintenta ni transforma un fallo en contenido mock. El flujo docente
**Ejecutar MOCK** conserva su implementación independiente; no utiliza este cliente.
Moodle dispone de un formulario nativo en **Curso → Más → TutorIA · Contenido**, con
permisos de docente, historial propio y solicitudes inmutables. La interfaz conserva
un fallo503 como fallo y no publica contenido automáticamente. Sus comprobaciones de
renderizado de éxito usan un fixture identificado. La generación con proveedor real
sigue pendiente de configuración y prueba explícita.

Se dejan para siguientes iteraciones RAG en este contrato, multimedia, evaluación pedagógica, autenticación institucional y cambios de interfaz que no sean necesarios para el consumo de la API.
