# 0012 — Preparación de retención y purga

9 de octubre de 2026. Estado: propuesta técnica; sin purga implementada/activada.

Los documentos borrados pueden dejar texto en snapshots de generaciones, en el prompt y
en el recurso. El historial conserva esta evidencia deliberadamente. Borrar un documento
no equivale a retirar todo su contenido de TutorIA. La política institucional de plazos,
autorizaciones y respaldos aún no está definida: no inventar una política de UPS ni activar
limpieza automática sobre los datos existentes.

## Condiciones técnicas de una futura implementación

1. Separar primero el registro persistente de reservas del contenido educativo. Hoy el
   limitador consulta generaciones_contenido; eliminar estas filas podría reponer el cupo
   del día, ignorar la espera de un minuto o la ejecución en curso. Una futura tabla de
   reservas conservará fecha/estado mínimo, sin texto académico, y se escribirá bajo el
   mismo bloqueo/transacción. Migración con backfill de reservas existentes y pruebas de
   límite tras purga, concurrencia, reinicio y UTC. Las trazas antiguas sin fecha no se
   convertirán en nuevas llamadas ficticias.
2. Decidir si se elimina el recurso completo o se redactan snapshots. Una redacción debe
   contar con un estado/contrato explícito: no servir un recurso cuyas fuentes se vaciaron
   como si conservara evidencia completa. Modificar esquema requiere nueva migración.
3. Inventariar documentos, fragmentos/vectores, perfiles, request/adaptation/sources/
   retrieval snapshots, instrucciones/prompt, recursos y archivos del volumen. Considerar
   datos de feedback y referencias históricas; separar sesión/cupo de contenido.
4. Ejecutar primero simulación de alcance por propietario/identificadores y conteos, sin
   mostrar contenido ni secretos. Proteger permisos/CSRF si se expone por API. Nunca
   permitir que admin purgue otro propietario de forma implícita.
5. Excluir ejecuciones activas, evitar carreras con generación/reservas y definir el orden
   transaccional de BD y reconciliación de archivos. Confirmar alcance antes de una acción
   irreversible. No eliminar volúmenes Docker para cumplir la retención.
6. Registrar evidencia mínima de la operación sin copiar textos que se pretendían retirar.
   Definir qué pasa con copias de seguridad y exportaciones; eliminar en la base activa no
   elimina los respaldos. Establecer procedimiento probado antes de datos institucionales.

## Decisiones que faltan

Plazos por categoría y ambiente, responsable autorizado, relación entre baja de documento
y generaciones derivadas, retención de observaciones/feedback, tratamiento de respaldos y
evidencia académica que debe conservarse. El ambiente actual contiene muestras sintéticas;
se conservan para reproducir pruebas. No fijamos un plazo arbitrario ni borramos esta evidencia.

El diagnóstico SQL [retencion_diagnostico.sql](../base_datos/retencion_diagnostico.sql)
es exclusivamente de lectura y devuelve conteos. No implementa ni certifica la política.
