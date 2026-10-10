# Piloto v3: resultados y límites

9 de octubre de 2026. Protocolo `personalizacion-x2-v3-piloto-01` fijado antes del
primer envío. Tres intentos por API autenticada, uno por nivel, todos succeeded.
No se declara validación pedagógica ni cierre académico del hito 9.

- [Protocolo](hito_09_protocolo_v3.md) y [manifiesto exacto](hito_09_protocolo_v3.json).
- [Preparaciones anteriores al envío](hito_09_piloto_v3_preparaciones.json).
- [Registro parcial conservado](hito_09_piloto_v3_resultados.json): contiene solo low,
  guardado antes de la interrupción; no sustituirlo por el resultado final.
- [Resultados completos](hito_09_piloto_v3_completo.json): recuperados del historial.

SHA-256 del manifiesto: `155aed6d4dff38eb87b1da5cee0727facfac6ad37d790bb76da416c2cde5f42f`.
Registro previo: 10:13:20.375629 UTC; primera reserva: 10:13:20.384599 UTC.
El nuevo documento tiene 882 caracteres normalizados/un fragmento; las tres preparaciones
recuperaron las mismas dos fuentes. S1 es el texto inicial y S2 el nuevo desarrollo de x².
Se comprobaron hashes de corpus, prompts y snapshots al reanudar, sin reconstruirlos.

| Perfil | Inicio UTC, 9 de octubre | Entrada / salida / total | Latencia proveedor |
|---|---|---|---|
| low | 10:13:20.384599 | 1980 / 486 / 2466 | 2643 ms |
| medium | 14:26:30.387859 | 1973 / 455 / 2428 | 15589 ms |
| high | 14:27:34.453597 | 1975 / 496 / 2471 | 1988 ms |

Total conocido: 7365 tokens (5928 entrada, 1437 salida). Modelo gemini-3.1-flash-lite,
prompt educational-rag-profile-v3, política profile-adaptation-v1, salida máxima 512,
timeout 30 s. Costo desconocido/null; no se consultó factura ni se activó facturación.

## Interrupción y recuperación

Al retomar, Docker estaba detenido y su arranque falló por el socket temporal dockerInference.
Se conservó su carpeta run mediante renombrado local reversible y se reinició sin restablecer
datos ni volúmenes. Con los servicios saludables, SQL confirmó low succeeded y medium/high
prepared sin fecha de reserva. Solo estos dos se enviaron: sin reintentar low ni duplicar perfiles.
El selector mock se restauró a student y la sesión de prueba se cerró.

Separación entre primer y último inicio: 15254.068998 s (4 h 14 min 14 s).
Esto y la ausencia de semilla/temperatura fija limitan comparaciones causales y de latencia.
Contador global UTC 9 al cerrar: cuatro reservas, cero generaciones activas; incluye la
generación alta v2 anterior a este piloto. Los límites diarios no se cambiaron.

## Lectura técnica asistida por Codex

Los tres recursos contienen resumen, cuatro pasos y ejemplo trabajado. Los pasos desarrollan
el mismo cociente incremental, expansión, simplificación y límite. Las tres respuestas
incluyen h≠0 antes de dividir y llegan correctamente a 2x; los pasos citan S2, que los respalda.
El resumen bajo/alto cita S1 y S2: S1 aporta el resultado; la justificación completa está en S2.

- Low desarrolla el procedimiento y termina con pendiente cero en a=0, explícita en S2.
- Medium usa instrucciones algo más breves y presenta f'(a)=2a, también en S2.
- High repite los cuatro pasos y añade a=3, pendiente 6. Es una sustitución aritmética
  correcta de la fórmula de S2, pero ese valor concreto no figura en la fuente. Debe
  distinguirse como aplicación derivada; no es un ejemplo copiado de S2. No introduce
  otra función ni un ejercicio para resolver, aunque la correspondencia con el criterio
  de respaldo explícito requiere revisión humana.

Se mantuvo el alcance de x² y no se repitió la ampliación a g(x) del alto v2. Sin embargo,
las diferencias de apoyo/profundidad son pequeñas: no basta cambiar dificultad en metadatos.
El alto no priorizó un análisis conceptual distinto y el medio casi repitió la secuencia baja.
No usar longitud ni número de pasos como prueba única de personalización o calidad.

El corpus y el prompt cambiaron respecto a v2, por lo que no se atribuye el resultado solo
a v3. Una observación por nivel no demuestra estabilidad ni mejora de aprendizaje.
La revisión humana y su rúbrica siguen pendientes. El siguiente ajuste técnico se orienta
a instrucciones de apoyo/profundidad más concretas, versionadas y sin alterar este piloto.

## Verificación proporcional

El verificador offline validó los tres contratos/citas y coincidencia de petición salvo
dificultad, perfil salvo identidad/nivel, fuentes y proveedor/modelo/prompt/política.
Detectó 6 bloques citados por caso, consumo conocido 3/3 y revisión semántica pendiente.
No se repitió la suite completa por datos/documentación. Health confirmó nginx → API →
PostgreSQL/pgvector después de restaurar la configuración. El piloto se ejecutó por API;
no se atribuye una nueva prueba visual de Angular a esta sesión.
