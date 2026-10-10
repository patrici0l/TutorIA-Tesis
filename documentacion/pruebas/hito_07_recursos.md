# Preparación docente — API y Angular

Verificación del 7 de octubre de 2026. Código guardado en 1c9cc44, rama feature/resource-preparation. Complementa hito_07_preparacion.md; no cierra la generación real ni la evaluación académica.

## Evidencia automática

- Backend Docker/PostgreSQL: 228 pruebas aprobadas, sin omisiones (30,06 s). Cinco pruebas nuevas cubren ruta/roles/sesión/CSRF, respuesta mínima, campos extra, cuerpo excesivo/no-store, errores sin persistencia y cupo por propietario. Los fixtures SQLite delimitan tablas compatibles; trazabilidad JSONB se prueba en PostgreSQL.
- Angular: 42 pruebas aprobadas en 11 archivos. Nuevas pruebas cubren payload por tipo, doble envío, interpolación segura, errores/reintento explícito y bloqueo de estudiantes; navegación incluye la cuarta pestaña docente.
- Ruff check y format check limpios: 121 archivos. Producción Angular compilada: 304,42 kB inicial; 14,59 kB del módulo cargado bajo demanda. Sin advertencias de presupuesto.
- Tras reanudar se reconstruyó Docker con caché conservando volúmenes y migraciones; tres servicios saludables. No se repitieron suites cerradas al modificar únicamente documentación y capturas.

## Navegador y persistencia

Sesión docente ficticia y corpus sintético existente. Se comprobaron campos condicionales quiz (tres por defecto) y retroalimentación; después se preparó EXPLANATION sobre «Derivadas», objetivo «Comprender la tasa de cambio instantánea de una función.». Se observó bloqueo del formulario mientras preparaba y resultado «PREPARADO, SIN GENERAR» con una fuente S1.

ID de preparación ec2b310d-fa00-481f-be17-397f4cd2c133. Consulta SQL posterior confirmó status=prepared, prompt_version=educational-rag-v1 y una fuente; provider, usage, estimated_cost y resource permanecen null. Hay dos preparaciones sintéticas guardadas (una de la comprobación previa). No se borraron documentos ni modelos.

Fuente: documento 84ed0928-238d-46ec-9de2-8f704249ddc3, fragmento 25136e79-2641-45c7-938b-a295cc3a54e5, párrafo 1, intervalo 0–318 exclusivo al final. Texto y hashes visibles coinciden con la muestra existente. Identificador y referencia se expanden mediante details/summary.

Capturas: [escritorio](hito_07_recursos_desktop.png) y [móvil](hito_07_recursos_mobile.png). Viewport móvil solicitado 390×844: ancho DOM disponible y scrollWidth ambos 375 px, sin desbordamiento horizontal de página; formulario de una columna, texto/hashes legibles y pestaña activa visible. Se restauró tamaño normal.

## Configuración y límites

La prueba usó AUTH_MOCK_USER=teacher como variable del proceso Compose; después se restauró el selector del .env mediante compose up sin override. La sesión docente permanece hasta expiración/logout. Por petición directa del autor se preparó el apartado Gemini del .env privado; el autor agregó la clave. Solo se comprobó presencia sin imprimir su valor. LLM_ENABLED=false confirmado dentro del backend; ningún envío externo de IA. .env está ignorado por Git.

No hay historial público para reabrir estas preparaciones ni generación educativa real. Los snapshots conservan texto/solicitud aunque se elimine el documento; retención/purga se definirá antes de corpus real. La similitud y la validación de citas no certifican pertinencia ni exactitud matemática. El límite de cinco intentos/minuto es por proceso, adecuado para el entorno local; producción requiere coordinación compartida.
