# Rúbrica de cumplimiento y validación de TutorIA

Fecha: 15/11/2026. Rúbrica propuesta para revisión con el tutor; los pesos no son una calificación institucional aprobada.

## Escala y aplicación

- 0: pendiente, sin evidencia suficiente.
- 1: implementación parcial.
- 2: implementado y verificado técnicamente, sin aceptación del tutor en el contexto real.
- 3: validado con casos representativos autorizados y aceptado por tutor o responsable institucional, según corresponda.

Cada versión suma 100 puntos de peso. Cuando se evalúe formalmente, la contribución de cada criterio será peso × nivel / 3. No se asigna una nota global retrospectiva: primero debe revisarse la evidencia y acordarse la rúbrica. Una versión no se cierra por promedio si falta alguno de sus criterios obligatorios.

Las pruebas de noviembre registradas en los documentos de versión son evidencia histórica; no se han vuelto a ejecutar todas al preparar esta rúbrica. La comprobación del 15/11 cubrió compilación Docker/Angular, salud de los servicios, integridad del modelo local y acceso HTTPS con sesiones de demostración de ambos roles. No incluyó generación externa ni CAS real.

## Versión 0.1: base documental

| Criterio | Peso | Situación documentada | Evidencia necesaria para aceptación |
|---|---:|---|---|
| Cargar y validar PDF con texto, DOCX y TXT | 15 | Implementado; pruebas sintéticas | Archivos autorizados de ambas asignaturas y rechazos correctos |
| Conservar originales, procedencia, permiso e integridad | 20 | Implementado; permiso declarado | Cotejo de originales y evidencia específica de autorización |
| Extraer, normalizar y fragmentar con referencias | 20 | Implementado; pruebas sintéticas | Revisar fórmulas, símbolos, tablas y referencias frente al original |
| Separar documentos y consulta textual por asignatura y propietario | 15 | Implementado y probado técnicamente | Casos de ambas materias y accesos indebidos rechazados |
| Conservar versiones documentales y permitir cotejar fuentes | 15 | Implementado y probado técnicamente | Demostrar actualización sin sobrescribir la versión anterior |
| Usabilidad y aceptación del flujo documental | 15 | Pendiente de aceptación docente | Tutor completa carga → proceso → consulta → cotejo y registra observaciones |

Conclusión: base técnica implementada; cierre académico pendiente de corpus autorizado y aceptación docente. Se mantienen las limitaciones de extracción de PDF escaneado y ciertas fórmulas DOCX descritas en la versión.

## Versión 0.2: recuperación y generación con fuentes

| Criterio | Peso | Situación documentada | Evidencia necesaria para aceptación |
|---|---:|---|---|
| Habilitar y retirar fuentes por versión | 15 | Implementado y probado técnicamente | Tutor acepta la política y demuestra habilitación/retirada |
| Recuperar semánticamente con E5 y pgvector | 20 | Integración con modelo local probada | Consultas representativas con fuentes pertinentes en ambas asignaturas |
| Filtrar RAG por asignatura, propietario, permiso y estado | 15 | Implementado; pruebas de aislamiento | Confirmar que fuentes ajenas o retiradas no entran en nuevas preparaciones |
| Generar explicación y ejemplo sustentados | 20 | Flujo y adaptadores implementados; aceptación pendiente | Ejecuciones del modelo acordado con revisión de corrección matemática y fidelidad |
| Adaptar por perfil sintético | 15 | Reglas implementadas según dominio y errores informados | Comparar mismo objetivo con perfiles y aceptar la diferencia de apoyo |
| Conservar trazabilidad y gestionar fallos | 15 | Implementado y probado técnicamente | Revisar solicitud, perfil, fuentes, prompt, modelo, parámetros, tokens y errores de ejecuciones representativas |

Conclusión: base técnica implementada y probada; pendiente cierre académico de v0.1, revisión pedagógica y ejecución representativa con el modelo acordado. Configurar o habilitar un proveedor no acredita la calidad de sus resultados.

## Versión 0.3 propuesta: login institucional y piloto integrado

Esta propuesta incorpora la validación del login real y conserva el alcance v0.3 del plan: seis recursos, tres LLM, dos asignaturas, fuentes externas autorizadas y piloto comparativo. El login real por sí solo no cierra v0.3 ni equivale a integración completa con ADAPTIA.

| Criterio | Peso | Punto de partida | Criterio de aceptación propuesto |
|---|---:|---|---|
| Login real institucional | 20 | Adaptador CAS y pruebas locales; conexión institucional pendiente | Acceso autorizado de docente y estudiante; ticket inválido, vencido y reutilizado rechazado; callback y sesión verificados |
| Roles, aislamiento y sesiones reales | 15 | Controles locales existentes | Identidad y rol validados con contrato institucional; accesos cruzados rechazados; cierre local y caducidad comprobados |
| Contrato de integración ADAPTIA | 10 | Acuerdos institucionales pendientes | Validación de contrato, identificadores, autenticación entre servicios y respuesta estándar con responsables |
| Completar los seis recursos del plan | 15 | Hay capacidades parciales adelantadas | Explicación, ejemplo, ejercicio, cuestionario, pista y feedback solicitables y revisados |
| Evaluar tres LLM en dos asignaturas | 15 | Hay adaptadores; evaluación comparativa pendiente | Ejecuciones reales bajo casos y parámetros acordados; registrar calidad, tiempos, tokens y costo disponible |
| Fuentes externas y condiciones con/sin RAG | 10 | Pendiente de aceptación dentro de este hito | Fuentes autorizadas, fijas y trazables; comparar sin RAG, RAG docente y RAG docente + externas |
| Piloto docente/estudiante y preparación de evaluación | 15 | Demo remota disponible; piloto formal pendiente | Casos, perfiles, corpus y rúbrica congelados; resultados y problemas registrados; casos piloto separados de finales |

## Secuencia para validar el login real

1. Coordinar con TI/Jefferson la confirmación del protocolo institucional. El código actual implementa CAS XML; debe confirmarse que ese sea el contrato autorizado.
2. Recibir endpoints oficiales de acceso y validación, atributos de identidad, política de roles, dominios permitidos y autorización para cuentas de prueba. Confirmar la regla actual que deriva el rol del dominio; no asumir que sustituye al contrato institucional.
3. Establecer un hostname HTTPS de prueba estable y autorizar el callback `/api/v1/auth/callback`. El Quick Tunnel actual es una demo temporal cuyo dominio cambia al reiniciarlo.
4. Preparar un entorno de validación separado con datos autorizados, configurar `AUTH_MODE=cas`, cookie Secure y URLs HTTPS coherentes; comprobar que no se puede elegir libremente el rol de demo.
5. Ejecutar casos positivos con docente/estudiante y negativos: identidad/dominio no autorizado, ticket ausente/inválido/vencido/reutilizado, state ausente/alterado, proveedor caído, sesión expirada y acceso a datos de otro propietario.
6. Comprobar cierre de sesión de TutorIA. Confirmar por separado si se requiere cierre global institucional: el cierre local no acredita logout del proveedor.
7. Conservar resultados sin contraseñas, tickets, cookies o tokens; obtener aceptación del responsable institucional y del tutor para el alcance que les corresponda.

Las pruebas automatizadas de CAS demuestran comportamiento frente a respuestas simuladas; la prueba HTTPS del 15/11 usó `AUTH_MODE=mock`. Ninguna sustituye una validación contra el servicio institucional real.

## Pendientes funcionales adicionales

Para priorización con el tutor: editar actividades y definir su retirada/eliminación preservando las entregas; decidir la política de corrección de perfiles. Actualmente las actividades permiten cerrar, cancelar y reactivar; los perfiles son observaciones sintéticas que se conservan como registros independientes. Estos cambios no se presentan como requisitos originales ya acordados de v0.3.

## Fuentes internas

- [Alcance y evidencia v0.1](Version-0.1.md).
- [Alcance y evidencia v0.2](Version-0.2.md).
- [Plan operativo](../../DOCUMENTACION/Plan%20de%20trabajo/01_plan_de_trabajo.md).
- Código de autenticación: `backend/app/modulos/autenticacion/servicios/cas_login_service.py`, `cas_validation_service.py` y `backend/app/configuracion/settings.py`.

Esta rúbrica no modifica el plan aprobado, no certifica una versión ni da por acordados contratos institucionales.
