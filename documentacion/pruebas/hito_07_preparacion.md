# Preparación del hito 7 — Contratos, prompts y trazabilidad

Fecha: 6 de octubre de 2026. Rama feature/content-contracts, base 444c90a.

Gemini permanece desactivado por indicación del autor; no hubo llamadas reales, claves, gastos ni recursos simulados presentados en el producto. Se prepara el flujo, no se declara completo el hito 7 ni el 10.

## Reproducción

```powershell
.venv/Scripts/ruff.exe check backend
.venv/Scripts/ruff.exe format --check backend
docker compose up -d --build --wait
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml build test-backend
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --rm --no-deps test-backend
git diff --check
```

Resultado: **223 pruebas backend aprobadas, sin skips**, 23,55 segundos en esta ejecución Docker. De ellas, 34 nuevas unitarias de contratos/prompts y nueve de PostgreSQL para trazabilidad. Las 34 también pasaron aisladas en Windows. Ruff check limpio y 117 archivos con formato correcto. Advertencias conocidas de Starlette TestClient/HTTPX y pypdf.add_js en rechazo de PDF activo; no nuevos fallos.

Docker reconstruido/arrancado, tres servicios saludables; Alembic head 0006_content_trace confirmado por consulta. Se conservaron migraciones 0001–0005, volúmenes, corpus/modelo y .env. LLM_ENABLED=false confirmado imprimiendo solo booleano. Consulta de count de generaciones_contenido tras las pruebas: cero; rollback completo de datos sintéticos. No hubo cambios Angular; compilación previa reutilizada por caché y sus 38 pruebas corresponden al cierre anterior.

## Cobertura nueva

- Construcción y validación estructural de los cuatro tipos iniciales, con esquema propio y citas obligatorias.
- Exclusión de owner/provider/model/perfil del cliente; tipos futuros rechazados; feedback requiere respuesta, quiz cantidad entera y opciones distintas.
- NFC, vacíos, controles, sustitutos Unicode; estructura, longitudes y límites de contexto sin truncamiento.
- Fuente con órdenes hostiles permanece como dato JSON y no se incorpora a instrucciones; se comprueba formato, no resistencia empírica de un LLM.
- Prompt hash reproducible, hash específico de fragmento y snapshots estables frente a mutación posterior; recuperación top-3 recibe propietario correcto.
- Salidas inválidas: JSON/fences/claves duplicadas, tipo incorrecto, insuficiencia explícita, citas ajenas/repetidas/vacías, count/índice/opciones quiz incorrectos y recursión excesiva.
- Persistencia real de preparación, prompt, referencias y versiones; ausencia de transacción tras preparación/lectura; otro propietario no accede ni finaliza.
- Recursos de prueba completan ciclo privado para los cuatro tipos; estado final no se sobrescribe. Restricción SQL rechaza succeeded sin recurso/fecha.
- Salida con cita inválida registra failed y metadata conocida sin guardar recurso. Fallo remoto usa código permitido y conserva desconocidos null. Modelo seleccionado queda registrado incluso si falla red; respuesta de otro modelo no completa el registro.

Primer intento de colección Docker tuvo un import cruzado entre archivos de pruebas no resoluble; fixtures sintéticos se separaron en tests/fixtures/content_reference.py. La suite final completa pasa sin omitir casos. El Python local carece de pgvector; se retiró un import de anotación innecesario del servicio para que sus contratos unitarios no dependan de SQL. Las pruebas SQL/modelo se ejecutaron en Docker con dependencias ya fijadas.

## Límites y siguiente bloque

Las salidas sintéticas son fixtures técnicos, no contenido validado ni resultados de Gemini. Sin evaluación de exactitud, calidad educativa, referencias efectivamente suficientes o personalización. No hay nuevas rutas públicas ni interfaz de recursos/historial. Preparar una experiencia docente para revisar solicitud/fuentes sin invocar Gemini; después integrar el coordinador y activar solo cuando el autor retome modelo/presupuesto/clave. Perfiles/rendimiento, métricas/costo, retención y evaluación independiente pendientes. Ver decisión 0008.
