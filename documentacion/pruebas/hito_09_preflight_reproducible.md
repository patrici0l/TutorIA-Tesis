# Comprobación reproducible previa al piloto salida1024

10 de octubre de 2026. Soporte del hito 9; el piloto continúa pendiente.

Desde la raíz, con el entorno Python de desarrollo y backend/PostgreSQL iniciados:

```powershell
.venv/Scripts/python.exe infraestructura/scripts/check-pilot-readiness.py
```

Opcionalmente agregar `--output seguimiento_privado/preflight_nuevo.json` para preservar
un archivo nuevo. No sobrescribe destinos. Salida 0 significa que todas las condiciones
consultadas coinciden; 1 significa condiciones pendientes; 2 corresponde a manifiesto
modificado, destino existente o consulta fallida. Los errores de Docker no se publican.

La herramienta fija el SHA del manifiesto y los tres IDs originales. Consulta únicamente
los seis registros del piloto/baseline y sus documentos, además del conteo global de
reservas. La transacción PostgreSQL es READ ONLY y REPEATABLE READ. Compara solicitud,
adaptación, perfil sintético, instrucciones, prompt y su hash canónico, fuentes públicas
e internas, hashes de texto, disponibilidad/propiedad y SHA de documentos. Comprueba
orden, ausencia de reserva, cuota UTC, generaciones activas, intervalo mínimo y valores
permitidos de configuración del contenedor. Nunca lee/imprime el archivo .env ni
claves, cookies o tickets; el informe tampoco contiene prompts, textos ni propietarios.

Es una fotografía, no una reserva de cuota ni una validación de sesión/rol autenticado.
Settings se carga en un proceso nuevo dentro del contenedor; no inspecciona la caché del
proceso HTTP. La API conserva la comprobación definitiva y el envío por sesión/CSRF.
No envía inferencias, modifica configuración, limpia generaciones ni escribe en la DB.
Los casos enviados quedan rechazados; una continuación parcial requiere revisar el
historial conforme al protocolo, nunca repetir automáticamente un intento.

## Evidencia de esta sesión

[Informe final](hito_09_preflight_final_20261010.json), 17:13 UTC /12:13 Guayaquil:
integridad correcta en tres casos, sin reservas; 3/5 usadas, cero activas/recientes.
Dos condiciones pendientes: tres llamadas libres y configuración temporal 1024.
Límite conservado en 512, selector teacher. Renovación prevista UTC 11 a las 00:00,
equivalente a las 19:00 locales del 10; volver a consultar, sin garantizar cupo futuro.

Se conservan dos salidas de desarrollo: [inicial](hito_09_preflight_20261010.json)
y [corregida](hito_09_preflight_corregido_20261010.json). La primera calculaba el SHA
solo sobre prompt y produjo tres falsos negativos. Se corrigió según la implementación
existente: SHA-256 del JSON canónico de instructions+prompt. No hubo divergencia de datos.
La segunda confirmó integridad; la final incorpora además los IDs fijados.

15 pruebas enfocadas con estado sintético en memoria: cuota, ejecución activa/reciente,
límites/nivel gratuito/cap alterados, reserva anterior, instrucciones/fuentes modificadas,
documento eliminado, registro ausente, orden/ID cambiado y no sobrescritura sin consultar.
Ruff y formato limpios. Consulta real comprobada, check-health aprobado y huella de las
21 generaciones sin cambio: `5c1ec598642e8d0c35e79d3d61aed1ae` (campos previos a 0011).
No corresponde repetir suites de API/Angular por este script externo de solo lectura.

Pendiente de revisión/commit humano: script, pruebas, tres informes y documentación.
Mensaje sugerido: `feat: verifica condiciones del piloto sin consumir IA`.
No cierra personalización, benchmark ni evaluación académica.
