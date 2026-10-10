> Nota histórica

El ensayo de este documento precede al flujo API/UI. Su script manual fue retirado el 9 de octubre
porque no utilizaba la cuota persistente. El coordinador interno y sus pruebas se conservan;
las generaciones nuevas se solicitan por la API/UI autenticada con reserva de cuota.

# Coordinador educativo y prueba RAG real

7 de octubre de 2026. El autor confirmó mediante captura de AI Studio que el proyecto de su clave está en Nivel gratuito y autorizó usarlo. Se mantiene presupuesto USD 0, sin modificar facturación ni activar compras/recargas. Captura y clave no se copian al repositorio.

## Implementación

GenerateContentService prepara la solicitud sobre el corpus del propietario, confirma snapshot y target explícito en PostgreSQL, llama una vez a LLMProvider y finaliza por GenerationTraceService. Resultado validado o código seguro de fallo; sin reintento ni fallback. Antes de la red no queda una transacción SQL abierta. No se expone como ruta pública todavía ni se cambia la preparación de Angular para que genere automáticamente.

La prueba manual app.modulos.contenidos.smoke requiere --free-tier-confirmed; importar el módulo o ejecutar --help no llama red. Solo acepta el documento sintético conocido por UUID/hash, usuario activo teacher/admin, documento no eliminado y fuentes exclusivamente de esa muestra. Cualquier otra fuente impide el envío. Clave solo desde configuración privada. Modelo 3.1 Flash-Lite, salida máxima 512 tokens, timeout final 30 s, una llamada por ejecución y frecuencia una/minuto/proceso. No usarla en healthchecks ni suites automáticas.

## Pruebas

Diez pruebas nuevas con PostgreSQL y proveedor ficticio: cuatro recursos, evidencia durable antes de la llamada, propiedad de snapshots, una sola llamada, timeout/cuota/salida incompleta, ausencia de fuentes, JSON inválido con conservación de consumo e interrupción inesperada. Suite completa: **238 aprobadas, dos advertencias conocidas, 17,99 s**. Ruff check/format check: 125 archivos limpios. git diff --check limpio. No hubo cambios Angular; se conserva evidencia anterior de 42 pruebas, sin afirmar nueva ejecución.

El primer comando focalizado usó una imagen de pruebas previa y no encontró el archivo; se reconstruyó y nueve pruebas pasaron. Tras añadir la prueba de interrupción se reconstruyó nuevamente y se ejecutó la suite completa indicada.

## Prueba real con fuentes

Primera llamada: timeout a los 15 s. ID 0331084d-5d0b-4a03-b6d4-a6b65767731f, estado failed, código llm_timeout, sin publicar recurso; consumo desconocido. Segunda llamada manual explícita, timeout ampliado a 30 s: éxito con ID 19f52cf3-eec8-440c-8681-b3b0d353f161, tipo EXPLANATION, versión educational-rag-v1, una fuente y citas S1. Se confirmó SQL y se exportó únicamente evidencia sintética/metadata permitida en [hito_07_generacion_real.json](hito_07_generacion_real.json).

Consumo informado en éxito: 1076 input, 327 output, 1403 total, latencia de proveedor 1551 ms. Versión gemini-3.1-flash-lite. Reasoning/cache y estimated_cost no informados quedan null. No se convierte consumo desconocido en cero ni se atribuye un cargo efectivo sin consultar facturación; la condición autorizada es usar únicamente el proyecto gratuito confirmado.

La explicación contiene f'(x)=2x para f(x)=x² y una referencia al ejercicio sintético. Validación de estructura/alias no certifica exactitud de toda la salida ni respaldo semántico; es una comprobación técnica, no un benchmark académico. Quiz, ejercicio y feedback se verificaron sin red; aún faltan pruebas reales por recurso y flujo Angular de generación. Hito 7 continúa parcial.

## Continuación

API de generación con sesión/roles/CSRF, concurrencia y cupo persistente, estados explícitos y revisión de fuentes en Angular. Mantener los límites de cuota gratuitos y detenerse ante 429 sin habilitar facturación. Un límite por minuto/proceso no es un tope diario global ni una prueba programática del nivel de facturación. Decisión de retención/purga y corpus real aún pendiente.
