# Actividades asignadas

Actualizado el 24 de octubre de 2026. Un profesor asigna un banco fijo de tres
preguntas o un recurso propio generado correctamente a una cuenta de estudiante activa. Se mantiene el alcance de demostración:
no importa matrículas universitarias, no consume IA y no emite calificaciones oficiales.

## Recorrido

1. Entra una vez como estudiante para que exista su cuenta ficticia.
2. Cierra sesión y entra como profesor. Abre **Actividades**.
3. Escribe título, correo del estudiante, bloque e instrucciones opcionales.
   En la demostración, el correo es `estudiante.demo@example.org`.
4. Entra como estudiante, abre **Mis actividades** y pulsa **Resolver actividad**.
5. Completa y guarda. El profesor verá intentos y mejor resultado al actualizar su listado.

La interfaz avisa al alumno de que el resultado de esa actividad será visible para el
docente que la asignó. Los intentos libres no se comparten ni se adjuntan retroactivamente.
Las identidades mock son compartidas; esta entrega no crea cuentas personales.

## Contratos y autorización

- `POST /api/v1/practice/assignments`: teacher/admin y cabecera X-TutorIA-Client.
  Recibe id UUID, student_email, version (derivadas-v1 o reglas-v1), title (1–120)
  e instructions (0–2000). Campos extra rechazados. Busca solo el correo exacto
  normalizado de una cuenta activa student; no ofrece un directorio de usuarios.
- Reintentar el mismo UUID y contenido devuelve la asignación original. Otro contenido
  o propietario con ese UUID responde 409. La interfaz conserva el UUID tras fallos de red.
- `GET /api/v1/practice/assignments`: historial paginado propio, limit 1–20 y offset
  0–100000. El alumno ve lo asignado a él; el docente/admin solo lo creado por él.
- `GET /api/v1/practice/assignments/{id}`: mismo ámbito; un UUID ajeno devuelve 404.
- `POST /api/v1/practice/attempts` añade assignment_id opcional. Si está presente,
  el backend exige destinatario y versión correctos antes de guardar. El UUID del intento
  no puede reutilizarse para moverlo a otra asignación ni convertirlo en práctica libre.
- El docente recibe únicamente número de intentos y mejor puntuación de la actividad;
  no recibe respuestas ni historial libre. Listados y detalles llevan no-store.

## Persistencia

Migración 0013 crea asignaciones_practica y añade assignment_id nullable a intentos_practica.
Los registros anteriores quedan como práctica libre. Una clave foránea compuesta
comprueba en PostgreSQL asignación + alumno + versión. El puntaje lo calcula el servidor.
La migración 0014 añade status (open/closed/cancelled) y status_changed_at nullable.
Las asignaciones anteriores empiezan abiertas; las respuestas guardadas no se modifican.
No existe eliminación ni edición de título, destinatario o banco en esta versión.

## Cerrar, cancelar y reactivar

Desde Actividades, el docente elige la acción y confirma sus efectos en la tarjeta.

| Estado | Significado | Nuevos intentos |
| --- | --- | --- |
| Abierta (open) | Disponible para resolver o repetir | Permitidos |
| Cerrada (closed) | Finalizada la recepción de entregas | Bloqueados |
| Cancelada (cancelled) | Retirada por el docente | Bloqueados |

Cerrar o cancelar conserva la actividad, los intentos y el mejor resultado. **Reactivar**
vuelve a permitir entregas. El alumno puede consultar el resumen de una actividad cerrada
o cancelada, abrir su historial y continuar con la práctica libre. No hay cambios en vivo:
el listado se actualiza al cargar/actualizar; si el profesor cierra mientras el alumno resuelve,
el guardado informa del cierre y conserva las respuestas en pantalla mientras no salga.

`POST /api/v1/practice/assignments/{id}/status` recibe `status` y `expected_status`,
ambos en open/closed/cancelled. Exige sesión teacher/admin, propiedad y X-TutorIA-Client;
campos extra rechazados y cuerpo máximo 16 KiB. Un alumno obtiene 403; otra cuenta docente,
404. Si el estado actual difiere del esperado y del solicitado, responde 409 y exige actualizar.
Repetir el estado ya aplicado devuelve el registro sin cambiar la fecha. Este control compara
el estado actual, no conserva un registro histórico completo de transiciones.

Los listados/detalles incluyen estado y fecha del último cambio. Cierre y guardado adquieren
el mismo bloqueo de fila en PostgreSQL hasta terminar la transacción: si el cierre se aplica
primero no entra el intento; si el guardado termina primero se conserva ese resultado.
Un reintento exacto de un resultado ya guardado se recupera incluso después del cierre;
un nuevo UUID o respuestas diferentes se rechazan. Reintentar la creación tampoco reactiva.

## Límites y próximos pasos

Sin grupos, vencimientos, entrega única, edición del contenido o avisos externos.
El alumno puede repetir una actividad abierta; se muestra su mejor puntuación entre esos intentos.
Asignar una práctica no demuestra una relación académica institucional. Para un despliegue
real se requieren cuentas verificadas, relación docente/grupo y política de acceso aprobada.

## Recursos generados (24 de octubre)

Desde Preparar recursos, genera o abre un resultado correcto en Mis recursos y pulsa
Asignar este recurso. El formulario conserva el vínculo y propone su título. El correo
del destinatario debe pertenecer a una cuenta estudiante activa que haya iniciado sesión.

POST recibe version `resource-v1` y resource_id UUID además de los campos comunes.
El servidor verifica propietario y estado succeeded antes de persistir. Recurso ajeno,
inexistente o aún sin resultado: 404. resource-v1 sin resource_id, o banco fijo con
resource_id: 422. Otro contenido para un UUID ya utilizado: 409.

La migración 0015 añade resource_id nullable, clave foránea a generaciones_contenido y
check de coherencia con version. Conserva todas las asignaciones e intentos anteriores.
El listado incluye resource_id; el detalle autorizado añade resource y sources. Nunca
expone prompt, respuesta del estudiante del request, adaptation_snapshot ni auditoría.
Los materiales contienen las soluciones del recurso, por lo que son material de estudio;
no admiten intentos ni registran calificaciones o lectura. Cerrar/cancelar cambia el estado
y conserva el material para consulta, como las respuestas históricas de bancos fijos.
