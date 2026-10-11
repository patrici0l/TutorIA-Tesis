# Revisión reproducible de pilotos con éxitos y fallos

10 de octubre de 2026. Herramienta auxiliar para preparar revisión de personalización;
no ejecuta benchmark ni declara validación pedagógica. No usa BD, Settings, credenciales
ni proveedores. La herramienta anterior offline_review conserva su contrato de tres éxitos.

## Problema resuelto

Un lote con dos fallos y un éxito no puede revisarse mediante una herramienta que exige
tres recursos válidos. Excluir fallos o reemplazarlos ocultaría el resultado del piloto.
trial_review admite tres historiales terminales, low/medium/high, y conserva cada estado.
No acepta casos pendientes, identificadores repetidos, niveles inconsistentes ni recursos
publicados como éxito sin contrato/citas válidos. Un fallo sin código público conserva
null; códigos crudos desconocidos se rechazan, sin exportarlos.

## Ejecutar sobre resultados guardados

Desde backend/, después de instalar las dependencias indicadas en README:

```powershell
../.venv/Scripts/python.exe -m app.modulos.evaluacion.trial_review ../documentacion/pruebas/hito_09_piloto_v4_low.json ../documentacion/pruebas/hito_09_piloto_v4_medium.json ../documentacion/pruebas/hito_09_piloto_v4_high.json ../seguimiento_privado/revision_terminal_v4.json
```

Los argumentos corresponden a low, medium, high y archivo nuevo de salida, en ese orden.
Cada entrada es el detalle íntegro obtenido de GET /api/v1/content/history/{id} sobre
datos sintéticos revisados. El destino debe tener carpeta existente; no se sobrescribe
un informe, una revisión humana ni la propia entrada. Cada archivo admite hasta 2 MiB.
Se conserva SHA-256 de bytes originales, incluidos BOM y saltos de línea.

Solo admite perfiles sintéticos y preparaciones adaptadas. El indicador synthetic no
anonimiza texto libre ni documentos: revisar el contenido antes de usar o compartir las
exportaciones. No incluye identificador ficticio del estudiante, owner_id ni mensajes
crudos, pero sí fuentes/afirmaciones necesarias para la revisión.

El formato cubre explicaciones, ejercicios y quizzes. FEEDBACK no se admite: el historial
público omite la respuesta original y no se inventa una para revalidar ese contrato.
No añade endpoints, llamadas a IA ni persistencia en la aplicación.

## Qué comprueba y qué deja pendiente

| Dato | Tratamiento |
|---|---|
| Estados | Los tres casos, incluidos fallos; no sustituir contenido truncado. |
| Petición/perfil | Compara excepto dificultad e identidad/nivel/fecha del perfil. |
| Fuentes | Compara snapshots públicos íntegros entre casos. |
| Modelo/versiones | Compara proveedor/modelo solicitado/prompt/política; conserva versiones devueltas de cada caso. |
| Límites de ejecución | Igualdad solo si los tres tienen execution_configuration; cualquier ausencia deja igualdad null. |
| Consumo | Subtotal conocido y cobertura; total de lote null si falta un total reportado. Cero conocido se conserva. |
| Costo/latencia | Valores por caso; sin sumar costos parciales o inventar moneda. |
| Revisión humana | Bloques citados y cinco dimensiones con decisiones null. |

control_evidence_status distingue different_controls, incomplete_evidence y
complete_recorded_controls. No compara factores contra un protocolo externo: el evaluador
debe cotejarlos también con el manifiesto fijado antes del envío. La igualdad entre casos
no basta para afirmar cumplimiento del protocolo, causalidad o estabilidad del proveedor.

ready_for_controlled_semantic_review solo es true con tres recursos válidos y controles
registrados coincidentes, incluidos límites. No asigna notas ni significa aprobación.
Un caso válido puede revisarse individualmente aunque esa marca sea false. Los fallos no
reciben contenido ni puntuaciones ficticias. Consultar la [rúbrica propuesta](hito_09_revision_offline.md).

## Aplicación a evidencia v4 real conservada

[Informe generado](hito_09_revision_terminal_v4.json), separado del
[paquete asistido anterior](hito_09_revision_v4.md). Los tres archivos originales mantienen
sus hashes. El informe vuelve a generarse de forma idéntica desde esas entradas.

- Tres casos: un recurso válido y dos fallos llm_incomplete.
- Seis bloques citados del caso medio; decisiones humanas pendientes.
- 2476 tokens de un caso son subtotal conocido; consumo total del lote desconocido.
- Cuatro controles de petición/perfil/fuentes/proveedor y versiones solicitadas coinciden.
- Cero casos con límites guardados: evidencia de configuración incompleta, sin atribuir
  512 desde los Settings actuales. El protocolo histórico documenta el límite separado.
- Sin tres recursos válidos, no hay comparación de diferenciación entre niveles.

La corrección posterior de metadatos/configuración no se aplica retroactivamente a estas
entradas. No se alteró el manifiesto salida1024 ni se consumió Gemini para producir el informe.

## Verificación proporcional

58 pruebas enfocadas aprobadas en Docker/PostgreSQL en 1.00 s: herramienta nueva y anterior,
reservas, trazas, coordinador e historial. Las pruebas nuevas cubren fallos incluidos,
consumo parcial/cero/desconocido, configuraciones distintas, objetivos distintos, casos
repetidos/pendientes/inconsistentes, citas inválidas, perfil no sintético, fecha sin zona,
modelo ausente y protección del destino. No usan proveedores externos.

Los códigos seguros compartidos se trasladaron a contenidos/errors.py para que el análisis
offline no importe repositorios/servicios de BD. Contratos anteriores conservados. Ruff y
formato limpios. Sin cambios Angular, nuevas migraciones o pruebas visuales en este bloque.
Backend reconstruido con la herramienta; servicios saludables y check-health aprobado.
Las 21 generaciones originales mantienen la huella anterior de sus campos. Cupo 3/5,
cero activas: no se reservó ni envió ningún caso salida1024.

Próximo paso principal: protocolo salida1024 con tres cupos libres y configuración/integridad
verificadas; después aplicar esta herramienta a los tres resultados terminales y realizar
revisión humana. Preparar herramientas de análisis no cierra etapa 14 ni el hito 9 académico.
