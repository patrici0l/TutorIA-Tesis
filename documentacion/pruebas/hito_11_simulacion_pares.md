# Recorrido experimental con transporte simulado

11 de octubre de 2026. CLI `app.modulos.evaluacion.paired_simulation` implementada:
manifiesto validado → adaptador OpenAI/Claude con HTTP ficticio → registro de ambos
brazos → plantilla de revisión humana. No ejecuta inferencia, RAG en vivo ni acceso a DB.

## Uso reproducible

Desde `backend`, con el entorno Python de desarrollo instalado:

```powershell
../.venv/Scripts/python.exe -m app.modulos.evaluacion.paired_simulation ../documentacion/pruebas/hito_11_simulacion_manifiesto.json ../documentacion/pruebas/hito_11_simulacion_respuestas.json ../seguimiento_privado/simulacion_pares_nueva.json
```

El destino debe ser nuevo. El ejemplo utiliza `model-test`, un nombre ficticio, y respuestas
sintéticas. Cada brazo del archivo de respuestas contiene `status_code` y `body`, con el
formato HTTP del adaptador elegido. El manifiesto declara proveedor/modelo, límites y timeout.
Para Claude, preparar otro manifiesto con ese objetivo y cuerpos Messages compatibles.
Solo se admiten OpenAI y Claude en este recorrido; Gemini permanece aplazado.

La configuración usa únicamente valores explícitos y predeterminados: no lee `.env`,
variables del operador ni archivos de secretos. El transporte siempre es `MockTransport`,
con claves ficticias; no existe una opción para activar red real en esta CLI.
Los controles deben ser compatibles con los límites actuales de los adaptadores:
salida 128–4096 tokens, timeout 5–60 segundos, entrada 1000–24000 caracteres.

## Entregable

Un JSON reúne `manifest`, `batch`, `report` y `assessment_template`, con procedencia
`synthetic_fixture`, huella de respuestas e identificadores reproducibles. Se pueden
extraer estos objetos para las CLI de registro y evaluación existentes. La plantilla
mantiene revisor, fecha y decisiones pendientes; no inventa valoraciones académicas.

Conserva los dos brazos ante errores HTTP, salida truncada, abstención o contenido inválido.
Los tokens provienen de las respuestas ficticias y no equivalen a consumo medido.
La latencia queda desconocida: el tiempo de proceso local no mide un servicio externo.
Los prompts directos no reciben las fuentes de RAG. El archivo original del manifiesto
no cambia y el paquete no declara finalizado el benchmark.

## Verificación

143 pruebas enfocadas aprobadas en 1,62 s: simulación, preparación, registro, revisión
humana y adaptadores. Incluyen 24 nuevas pruebas del recorrido, cuatro recursos × dos
proveedores, fallos conservados, controles HTTP, red bloqueada durante tests, entorno
ignorado, repetibilidad y destino exclusivo. Ruff sin errores.

La CLI se ejecutó además sobre el ejemplo guardado y produjo el paquete local
`seguimiento_privado/simulacion_pares_20261011.json` (excluido de Git).
No se reconstruyeron contenedores porque este bloque se ejecuta offline en desarrollo.
No se modificaron servicios, datos de la aplicación ni configuración local.

Pendientes reales: diseño experimental aprobado (corpus, modelos, orden, repeticiones,
rúbrica y presupuesto), autorización de uso real de proveedores, mediciones efectivas y
evaluación humana. Las comprobaciones sintéticas no reemplazan ninguno de estos puntos.
