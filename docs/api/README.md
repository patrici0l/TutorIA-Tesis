# Ejemplos de consumo

19/11/2026. Contrato local existente, con avance de v0.3 en la rama
`feature/v0.3-ejemplos-pistas`. El login institucional y el despliegue siguen pendientes.

Los JSON de esta carpeta son **simulados**, no resultados de una llamada a IA.
Sus identificadores, documentos, hashes y fechas no corresponden a registros reales.
Permiten preparar un consumidor simulado; para ejecutar contra TutorIA hay que usar
los identificadores que devuelva esa instalación. No contienen credenciales.

## Qué recibe y devuelve TutorIA

El ejemplo pide explicar la derivada de x². El recorrido tiene dos pasos:

| Paso | Petición | Respuesta simulada |
|---|---|---|
| Preparar: buscar fuentes propias habilitadas y guardar la solicitud; no llama al LLM | `POST /api/v1/content/prepare`, cuerpo [01-preparar-request.json](01-preparar-request.json) | HTTP 201, [02-preparar-response.json](02-preparar-response.json) |
| Generar: enviar la preparación al proveedor configurado | `POST /api/v1/content/{id}/generate`, cuerpo [03-generar-request.json](03-generar-request.json) | HTTP 200, [04-generar-response.json](04-generar-response.json) |

Usar en el segundo paso el `id` devuelto por el primero. Las citas `S1` del recurso
apuntan a `citation_id` en `sources` de la preparación. El proveedor y el modelo se
configuran en el servidor; no se mandan en estos cuerpos. `profile_id` es opcional:
si se envía debe pertenecer al docente y ser compatible con el tema. En ese caso la
respuesta incluye la adaptación y la dificultad efectiva.

## Acceso actual y prueba local

Se utiliza una sesión de docente/administrador mediante cookie `prototipo_session`.
Las escrituras requieren además `x-prototipo-client: web` y JSON. No existe todavía
un contrato Bearer de integración ADAPTIA. No copiar ni compartir cookies reales.

Con la instalación local iniciada:

1. Abrir `http://localhost:4200/login` e ingresar como Profesor en modo demo.
2. Tener un documento propio de Cálculo Diferencial procesado, indexado y habilitado.
3. Abrir `http://localhost:4200/api/v1/docs` en el mismo navegador. El navegador
   conserva la sesión; introducir `web` en la cabecera del endpoint.
4. Probar `/content/prepare` con el primer JSON y guardar el identificador obtenido.
5. Consultar `GET /api/v1/content/quota` antes de generar. Ejecutar `/generate`
   solo si se quiere una llamada real al proveedor habilitado: puede consumir cuota
   y presupuesto. Para emular el consumo basta con los archivos de esta carpeta.
6. Consultar `GET /api/v1/content/history/{id}` para recuperar el detalle guardado.

El OpenAPI está en `/api/v1/openapi.json`. No hace falta desplegar para revisar
estos ejemplos o simular las respuestas.

## Errores y reintentos

- HTTP 422 al preparar sin fuentes: [05-error-sin-fuentes.json](05-error-sin-fuentes.json).
- HTTP 503 al generar con el proveedor deshabilitado: [06-error-generacion-deshabilitada.json](06-error-generacion-deshabilitada.json).
- Sin sesión válida, el acceso se rechaza; sin la cabecera de escritura, HTTP 403.
- Un error del proveedor o una salida inválida puede devolver HTTP 200 con
  `status: "failed"`, `resource: null` y `message`. El consumidor debe revisar
  `status`, no solo el código HTTP.
- No repetir automáticamente `/generate` si se pierde la respuesta: consultar el
  historial primero. La reserva evita un segundo envío de la misma preparación;
  no equivale a que toda repetición devuelva de nuevo una respuesta satisfactoria.
- Si una fuente se retira o cambia antes del envío, hay que preparar otra vez.

## Nuevas opciones de v0.3

El mismo flujo admite `EXAMPLE` y `HINT`, además de los cuatro tipos anteriores.
Para pedir un ejemplo, usar `resource_type: "EXAMPLE"` y un objetivo como
«Resolver paso a paso la derivada de f(x)=x²». Devuelve `statement`,
`solution_steps` y `answer`, además de tipo y título.

Para una pista, usar `resource_type: "HINT"` y un objetivo como
«Dar una pista para derivar f(x)=x² sin revelar el resultado». Devuelve
`statement` y `hints`, además de tipo y título. Cada bloque conserva `text` y
`citations`. No admite campos de solución; que el texto no revele la respuesta
requiere también revisión docente. El problema se especifica en tema/objetivo.

No enviar `student_answer` ni `question_count` para estos dos tipos:
esos campos corresponden a `FEEDBACK` y `QUIZ`, respectivamente.


## Fuentes externas de Wikipedia

Requieren la misma sesión docente/administrador. Prefijo:
`/api/v1/documents/external/wikipedia`.

| Método y ruta | Uso |
|---|---|
| `GET /search?q=Derivada` | Hasta cinco artículos de Wikipedia en español, con `page_id` y título |
| `GET /preview/{page_id}` | Texto adaptado, advertencias y `source` con revisión, fechas, licencia y hashes |
| `POST /import` | Guarda la revisión confirmada sin procesarla ni habilitarla |
| `GET /snapshot/{document_id}` | Descarga privada de la captura JSON original con integridad comprobada |

Cuerpo de importación (sustituir identificadores y hash con los de la vista previa):

```json
{
  "page_id": 28789,
  "revision_id": 175700257,
  "text_sha256": "HASH_DE_64_CARACTERES_DEVUELTO_POR_PREVIEW",
  "course": "Cálculo Diferencial",
  "authorization_confirmed": true
}
```

La cabecera `x-prototipo-client: web` es obligatoria al importar. No se recibe texto,
URL ni licencia desde el cliente: el servidor los consulta de nuevo para esa revisión.
Un texto cambiado devuelve 409 y exige repetir la revisión. Un artículo incompatible o
demasiado grande devuelve 422; fallos del proveedor, 503; tiempo agotado, 504; límite
local de consultas, 429. Ninguno produce una habilitación automática.

La respuesta 201 es un `DocumentResponse` con `external_source` y `published_at: null`.
El origen externo también se conserva en los resultados RAG y las fuentes de la
preparación. El documento se procesa e indexa con las rutas existentes; después se
revisa y se habilita explícitamente. La importación no requiere una clave de IA.

Referencias de implementación: [búsqueda](https://www.mediawiki.org/wiki/API:Search),
[revisiones](https://www.mediawiki.org/wiki/API:Revisions),
[contenido de una revisión](https://www.mediawiki.org/wiki/API:Parsing_wikitext),
[licencia del sitio](https://www.mediawiki.org/wiki/API:Siteinfo) y
[identificación del cliente](https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy).

Prueba E2E externa opcional: establecer `WIKIPEDIA_LIVE_TEST=1` y `E2E_BASE_URL` hacia
un entorno de prueba, y ejecutar `npm run test:e2e -- fuentes-externas.spec.ts` desde
frontend. Consulta Wikipedia, crea un documento de prueba, lo procesa e indexa y lo
retira/elimina al finalizar; no solicita generación LLM. No ejecutarla sobre producción.
