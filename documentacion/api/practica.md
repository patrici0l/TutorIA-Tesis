# Práctica introductoria e historial privado

12 de octubre de 2026. `/practica` conserva tres ejercicios fijos de derivadas con
feedback inmediato en Angular. Al completar la actividad, **Guardar resultado** envía
las respuestas al backend, que calcula los aciertos y guarda el intento en PostgreSQL.
No consume IA ni representa una calificación institucional.

## Contrato

- `POST /api/v1/practice/attempts`: sesión activa y cabecera `X-TutorIA-Client: web`.
  Recibe `id` UUID, `version: derivadas-v1` y `answers`, exactamente tres enteros 0…3.
  No admite `score`, `owner_id` ni campos adicionales. Respuesta 200, tanto al crear
  como al repetir el mismo intento sin cambios.
- El backend usa la clave versionada `(0, 2, 3)`. La prueba local compara esta clave
  con el banco Angular; cambiar el banco requiere revisar la versión y el contrato.
- `GET /api/v1/practice/attempts?offset=0&limit=10`: devuelve `items`, `total`,
  `best_score`, `offset`, `limit`. Límite 1…20, desplazamiento 0…100000.
  Sin intentos: total cero y mejor resultado null, nunca un cero inventado.
- Ambos endpoints filtran por usuario autenticado. Docente/admin pueden probar la
  actividad y guardar sus propios resultados, sin leer los de estudiantes.
- Respuestas privadas llevan `Cache-Control: no-store`; cuerpos acotados a 16 KiB.

## Persistencia y reintentos

Migración `0012_practice_attempts`, tabla `intentos_practica`, con clave compuesta
`owner_id, id`, versión, respuestas, aciertos y fecha del servidor. Inserción atómica
con conflicto sin sobrescritura. Mismo usuario/ID/respuestas devuelve el original;
el mismo ID con respuestas distintas responde 409. Otra cuenta tiene su propio espacio.

Angular conserva el UUID al reintentar un guardado fallido y evita envíos simultáneos.
Al reiniciar la práctica crea otro UUID. Se conservan solo intentos completos guardados;
no hay recuperación automática de respuestas parciales ni de un envío incierto tras
cerrar/recargar la pestaña. El historial permite comprobar qué quedó guardado.

## Alcance educativo y privacidad

El feedback y las soluciones del banco son visibles en el cliente para autoestudio.
El cálculo backend impide aceptar una puntuación suministrada, pero no acredita trabajo
independiente ni impide consultar la clave. Repetir el banco no prueba dominio académico.
Las cuentas mock son identidades compartidas de demostración: quienes usan la misma
identidad ven el mismo historial. No introducir datos de estudiantes reales.

Pendientes: asignación por docente, banco ampliado, actividades personalizadas y
seguimiento por competencias. No se añadieron integración universitaria ni notas.

## Verificación

13 pruebas unitarias locales aprobadas, incluida concordancia de clave Angular/backend.
En Docker/PostgreSQL: 13 aprobadas y una omitida (el contenedor backend no contiene
fuentes Angular). Integración verifica durabilidad, idempotencia, conflicto, paginación,
mejor resultado y separación por propietario incluso para admin; datos de prueba
revertidos por transacción externa. 13 pruebas Angular enfocadas aprobadas, incluidos
reintento con mismo UUID, bloqueo de duplicados y fallo de historial sin bloquear práctica.
Ruff limpio; builds backend/frontend realizados. Advertencia Starlette/HTTPX preexistente.

Verificación final: frontend/backend/PostgreSQL saludables y Alembic en 0012 (head). En navegador se completó la práctica, se guardó un intento ficticio de 3/3 y se confirmó su persistencia al recargar con la cuenta Docente Demostración. Ese registro permanece en la DB local. Guía: 162 clases y 270 métodos, comprobaciones DOM aprobadas; sin revisión visual del HTML privado.

El historial permite revisar respuestas guardadas y su retroalimentación, con temas por reforzar. Se interpreta únicamente derivadas-v1 y alternativas válidas. La revisión no altera el ejercicio en curso. Verificado con 9 pruebas Angular del módulo (13 de octubre de 2026).
