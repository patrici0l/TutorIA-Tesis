# Perfiles de rendimiento: contrato sintético v1

Hito 8, 7 de octubre de 2026. Base `/api/v1/profiles`. Sesión TutorIA obligatoria, rol teacher/admin y propiedad por creador; un administrador tampoco consulta perfiles ajenos. El identificador ficticio no vincula una cuenta institucional. No se reciben estudiantes reales ni se conecta todavía un servicio externo.

## Rutas

- POST `/profiles`: valida y guarda una observación; responde 201 con UUID, `created_at`, `schema_version` y datos normalizados. Requiere el mismo encabezado CSRF del cliente Angular que las otras escrituras.
- GET `/profiles`: resumen privado paginado, `offset=0` y `limit=10` por defecto; offset entre 0 y 100000, límite entre 1 y 20. Orden descendente por fecha/UUID, incluye total. No devuelve errores ni datos adicionales en la lista.
- GET `/profiles/{id}`: instantánea propia completa. UUID inválido: 422; inexistente o ajeno: mismo 404. Rol estudiante: 403. Sesión inválida: 401.

Respuestas `Cache-Control: no-store`. Cuerpo máximo 16 KiB. POST limitado a diez intentos/minuto por usuario y proceso; exceso 429 y Retry-After: 60. Este límite local no es distribuido y reiniciar el proceso lo reinicia. No se usa Gemini, RAG ni la cuota de generación.

## Solicitud de ejemplo

```json
{
  "student_id": "SYN-001",
  "topic": "Derivadas",
  "performance": 42,
  "attempts": 4,
  "frequent_errors": ["regla_potencia"],
  "mastery_level": "low",
  "recommended_support": "reinforcement",
  "resolution_time_seconds": 120,
  "progress_trend": "improving",
  "data_kind": "synthetic"
}
```

`data_kind` es obligatorio y únicamente acepta synthetic. Es una declaración del cliente, no un detector de datos reales; Angular exige confirmación explícita de uso ficticio. No ingresar nombres, matrículas, correos ni calificaciones reales.

| Campo | Validación |
|---|---|
| student_id | 1–64 caracteres ASCII: letras, números, guion y guion bajo |
| topic | 1–160 caracteres |
| performance | Número finito 0–100; no strings ni booleanos |
| attempts | Entero estricto 1–10000 |
| frequent_errors | Opcional, lista vacía por defecto; máximo diez etiquetas distintas de 1–100 caracteres |
| mastery_level | low, medium o high, informado por el emisor |
| recommended_support | reinforcement, practice o challenge |
| resolution_time_seconds | Opcional/null; número finito 0–86400 |
| progress_trend | Opcional/null; improving, stable o declining |
| data_kind | synthetic |

Identificador, tema y errores se normalizan a Unicode NFC y se recortan en sus extremos; se rechazan controles y sustitutos Unicode. Los errores repetidos tras normalización se rechazan. Campos desconocidos, incluyendo propietario, son 422. El propietario se obtiene exclusivamente de la sesión.

TutorIA conserva el desempeño, nivel y apoyo enviados: no calcula notas, umbrales ni relaciones entre estos campos. Un desempeño de 100 con nivel low permanece así. El vocabulario de apoyo es un contrato inicial de demostración; su correspondencia con el sistema externo deberá confirmarse antes de integrar.

## Persistencia y experiencia de usuario

Migración 0008: `perfiles_rendimiento`, UUID, creador, payload JSONB validado, fecha y versión `performance-profile-v1`. Restricciones SQL para objeto JSON y versión; la validación de los campos pertenece al esquema de aplicación. Las observaciones son inmutables: otra petición crea otro UUID incluso con el mismo estudiante/tema. No hay actualizaciones, eliminación ni clave de idempotencia. Ante un resultado ambiguo de red, consultar la lista antes de reenviar.

Angular `/perfiles` ofrece formulario, validaciones, estados de carga/error, lista de diez entradas, paginación y detalle. No guarda perfiles en localStorage; al recargar se consulta la lista. Texto interpolado, sin HTML activo ni reintentos automáticos. Guardar bloquea envíos dobles mientras está pendiente.

La preparación de recursos ya admite perfiles propios y conserva su snapshot/política: ver [personalización](personalizacion.md). Credenciales de integración externa, validación de contenido adaptado y políticas de retención/purga quedan para las etapas siguientes. No activar perfiles reales antes de definir esos controles.
