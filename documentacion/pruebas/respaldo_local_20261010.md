# Respaldo local y comprobación aislada de recuperación

10 de octubre de 2026. Tarea auxiliar de operación; no cierra hito 12 ni modifica la
evaluación experimental. Cero llamadas Gemini y cero commits automáticos.

## Cambio

backup-local.ps1 crea database.dump, documents.tar.gz y manifest.json en una carpeta
nueva excluida de Git. Exige aplicación/migraciones/preparador inactivos y PostgreSQL
activo. Lee documentos desde un helper sin red con volúmenes montados en solo lectura.
No copia .env ni pesos y conserva hashes de archivos y documentos individuales.

verify-local-backup.ps1 rechaza archivos alterados antes de restaurar, usa la imagen
PostgreSQL del proyecto en un contenedor temporal sin red/puertos/volúmenes activos,
restaura con pg_restore --exit-on-error y comprueba documentos contra el manifiesto.
El contenedor DB usa tmpfs de 512 MiB; se retira al finalizar. El informe de comprobación
se guarda separado del manifiesto. Ver [manual técnico](../manuales/manual_tecnico_local.md).

## Pruebas reales

- Ambos scripts pasan el parser de PowerShell.
- backup-local rechaza servicios activos antes de crear una copia.
- verify-local-backup rechaza una fixture sintética con hash incorrecto antes de crear
  el contenedor de restauración; no se alteró la copia real para esta prueba.
- git check-ignore confirma exclusión de respaldos_locales.
- Cero generaciones activas antes de detener frontend/backend.
- Copia real completada y hashes verificados; PostgreSQL y volúmenes conservados.
- Aplicación reanudada: frontend/backend/postgres healthy y migrador Exited (0).
- check-health verifica nginx → API → DB → pgvector después de reanudar.
- pg_restore en DB temporal completó sin error; consulta estructural posterior válida.
- Archivo de documentos leído: dos archivos y todos los hashes individuales coinciden.
- Contenedor temporal retirado; solo permanece el PostgreSQL original entre contenedores
  de su imagen al comprobar. Sin sobrescribir la DB activa ni recuperar archivos encima de ella.

| Dato | DB restaurada | DB activa consultada después |
|---|---|---|
| Migración | 0010_cost_basis | 0010_cost_basis |
| Documentos | 2 | 2 |
| Fragmentos | 2 | 2 |
| Generaciones | 21 | 21 |
| Perfiles | 9 | 9 |
| Usuarios | 2 | 2 |

DB restaurada: ocho tablas públicas y pgvector 0.8.2. Los conteos iguales y restauración
exitosa no son una comparación criptográfica de cada fila ni un ensayo de carga.
Los archivos de copia/informe permanecen privados en respaldos_locales; no se publican
sesiones, identidades, contenido del dump ni rutas individuales de documentos.

## Límites y pendientes

No se ensayó sustituir el entorno activo, pérdida total de disco, permisos productivos,
restauración en otra máquina ni recuperación a un punto temporal. No hay programación
automática, cifrado propio, política de retención ni copias externas gestionadas.
Para escrituras fuera de la aplicación, el operador debe asegurar inactividad también
de esos clientes. Los pesos son regenerables; los secretos necesitan custodia separada.
La aplicación se pausó brevemente para consistencia y quedó recuperada.

Próximo paso principal mantiene el protocolo salida1024 y revisión humana. Operación
local dispone ahora de un procedimiento repetible, sin declarar cierre de la tesis.
