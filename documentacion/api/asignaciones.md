# Actividades asignadas

Primera versión local, 14 de octubre de 2026. Un profesor asigna un banco fijo de tres
preguntas a una cuenta de estudiante activa. Se mantiene el alcance de demostración:
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
No existe actualización ni eliminación de asignaciones en esta versión.

## Límites y próximos pasos

Sin grupos, vencimientos, entrega única, edición, cancelación o avisos externos.
El alumno puede repetir una actividad; se muestra su mejor puntuación entre esos intentos.
Asignar una práctica no demuestra una relación académica institucional. Para un despliegue
real se requieren cuentas verificadas, relación docente/grupo y política de acceso aprobada.
