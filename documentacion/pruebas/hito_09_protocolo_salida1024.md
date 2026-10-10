# Protocolo prospectivo: capacidad de salida de 1024 tokens

10 de octubre de 2026. Identificador personalizacion-x2-salida1024-piloto-01.
Manifiesto: hito_09_protocolo_salida1024.json. Fijado antes de inferencias.
Estado inicial: no ejecutado. No sustituye ni reintenta los registros del piloto v4.

## Hipótesis y controles

Investigar si 1024 tokens permiten completar los tres recursos que con 512 produjeron
dos MAX_TOKENS. Mantener perfiles originales v4, objetivo, fuentes, prompt v4/política v2,
Gemini 3.1 Flash-Lite, timeout 30 s, entrada 12000, orden low→medium→high y una llamada
por nivel. No crear perfiles más favorables ni modificar guía para reducir la dificultad.
Preparar registros nuevos con los mismos profile_id; exigir SHA de prompt idéntico a su
correspondiente v4, además de fuentes idénticas y versiones. No reenviar IDs terminales.

Único parámetro de inferencia modificado: max_output_tokens 512→1024. No se altera el
presupuesto USD 0, cinco reservas/día UTC, una simultánea ni separación mínima 60 s.
La corrección 1610020 cambia la captura de metadatos ante fallo, no el prompt. Diferencia
temporal y aleatoriedad del proveedor impiden inferencia causal y comparación estadística.
Una muestra por nivel sirve para viabilidad técnica, no para estabilidad ni aprendizaje.

## Condiciones de ejecución

1. Leer manifiesto y verificar su SHA contra el preflight. Comprobar tres cupos disponibles,
   ausencia de generación activa, nivel gratuito confirmado y demás valores fijados.
2. Preparar por API autenticada, reutilizando perfiles/documentos v4. Guardar IDs y detalles
   antes del primer envío. Si prompts o fuentes difieren, detener y documentar, sin inferencia.
3. La preparación no incorpora límite de salida: la configuración activa puede seguir en
   512. Antes de enviar, establecer temporalmente 1024 en backend y registrar comprobación
   no sensible del proceso real. No confundir el preflight de preparación con ese control.
4. Enviar solo mediante POST /api/v1/content/{id}/generate, sesión/CSRF y cuota persistente.
   Una llamada por caso, tres máximo; conservar fallos/truncamientos/timeouts. Si se interrumpe,
   consultar historial y continuar solo casos sin reserva, nunca repetir un caso enviado.
5. Guardar respuesta, versiones, uso, costo condicionado, latencia y fechas. Si faltan tokens,
   no sumar null como cero. Citas de alias válidos no certifican respaldo de afirmaciones.
6. Restaurar configuración previa (512 y selector mock), cerrar sesión y comprobar salud.
   No adoptar 1024 como valor permanente por un único piloto ni aumentar cuota diaria.

## Criterio de decisión fijado previamente

- Viabilidad del límite: informar contratos válidos de tres intentos y motivo de cada fallo.
  Tres éxitos habilitan revisión de diferenciación, no la aprueban automáticamente.
- Semántica: misma rúbrica synthetic-review-v1; alcance x², respaldo de fuentes, corrección,
  apoyo por nivel y claridad. No usar longitud como indicador de calidad. Ver protocolo v4.
- Si persiste MAX_TOKENS o timeout: cerrar este piloto y analizar evidencia antes de nuevos
  cambios. No seguir aumentando límites ni elegir resultados exitosos selectivamente.
- Si no hay tres recursos válidos: diferenciación no evaluable entre los tres niveles.
  Revisión humana pendiente en todos los casos; no asignar calificaciones automáticas.

## Estado al definirlo

Consulta del 10 de octubre 10:37 UTC (05:37 Guayaquil): 3/5 reservas, cero activas.
No hay cupo suficiente para iniciar este lote. Se permite preparar sin inferencia;
la ejecución queda pendiente de nueva comprobación cuando haya cupo. No hay automatización
ni cambio anticipado del límite activo. Sistemas universitarios permanecen fuera de alcance.
