# Protocolo de comparación sintética de perfiles

8 de octubre de 2026. Comparación exploratoria de tres preparaciones, previa al benchmark formal del hito 11. No es evaluación académica ni prueba de mejora del aprendizaje.

Variables fijas: tema Derivadas, recurso EXPLANATION, dificultad solicitada basic, objetivo “Comprender la derivada de f(x)=x² como tasa de cambio y explicar f'(x)=2x usando solo el ejemplo de la fuente.”, corpus docente sintético ya indexado, proveedor/modelo configurados, entrada/salida/timeout y cuotas sin cambios. Antes de generar, cotejar identificadores/hashes de fuentes de las tres preparaciones; si difieren, informar el factor adicional y no atribuir toda diferencia al perfil.

Los tres perfiles tienen los mismos datos académicos ficticios: desempeño 42, intentos 4, regla_potencia, refuerzo recomendado, 120 segundos y tendencia improving. Solo varían el dominio low/medium/high y su identificador ficticio. El porcentaje constante es deliberado para aislar la política basada en dominio; no representa tres alumnos reales ni una regla de calificaciones. El identificador no llega al proveedor.

Política profile-adaptation-v1 y prompt educational-rag-profile-v2. Las diferencias esperadas de preparación son dificultad basic/intermediate/advanced, orientación paso a paso/práctica guiada/mayor complejidad y foco localizado constante. El docente mantiene EXPLANATION para comparar el mismo contrato. No cambiar parámetros después de ver una salida para mejorar artificialmente el contraste.

Cada generación se envía una sola vez por la ruta API con cuota persistente. Registrar UUID, estado, fecha UTC, modelo, consumo conocido o null, latencia, prompt/hash/fuentes y resultado validado. No reintentar fallos, no incrementar límites ni usar scripts directos del proveedor. Si el cupo diario impide completar el conjunto, dejar pendiente la preparación restante y documentar la separación temporal antes de comparar.

Revisión exploratoria: comparar estructura, complejidad propuesta, cantidad/claridad de pasos, uso de fuentes y adecuación a orientación. Comprobar manualmente matemáticas y si cada afirmación está respaldada: pasar validación JSON/citas no demuestra fidelidad semántica. Sin puntuaciones pedagógicas inventadas. Un caso por nivel no controla aleatoriedad ni cambios del proveedor; el experimento formal deberá registrar repeticiones, corpus/rúbrica autorizados y condiciones comparables.
