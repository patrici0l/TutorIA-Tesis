# Reglas de desarrollo de TutorIA-Lucero

Leer README.md y documentacion/PLAN_DE_TRABAJO.md antes de implementar. La fuente completa está en documentacion/investigacion/plan_implementacion_fuente.txt. Respetar el avance vertical del plan; no saltar a LLM antes de validar recuperación RAG.

La instrucción del autor del 5 de octubre de 2026 reemplaza la autenticación del plan: SSO/CAS UPS, modos mock/cas y sesión HttpOnly. Prohibido agregar Google OAuth, registro por correo/contraseña o password/password_hash a usuarios institucionales. Leer documentacion/decisiones_tecnicas/0002-sso-ups.md. No conectar al CAS real hasta disponer de parámetros autorizados por TI.

Actualizar documentacion/CONTINUIDAD.md al cerrar cada bloque y antes de interrumpir trabajo extenso: estado, pruebas reales, cambios pendientes, rama y próximo paso. No inventar porcentajes de contexto o resultados.

Mantener seguimiento_privado/BITACORA.md como itinerario personal por fecha y sesión (America/Guayaquil): objetivo, trabajo realizado, pruebas/resultados, limitaciones, commit y próximo paso. Esta carpeta está excluida de Git; nunca forzar su incorporación ni copiar la bitácora a documentación pública. Reconstrucciones históricas deben indicar su fuente y no inventar horarios/duración. No registrar secretos ni datos institucionales reales. Al cerrar cada punto verificable del plan, hacer un commit descriptivo de sus cambios y actualizar la bitácora privada con su hash; no etiquetar pendientes como terminados ni incluir cambios ajenos.

- Stack: Angular, FastAPI, PostgreSQL/pgvector, Alembic, Docker.
- Carpetas de dominio en español sin tildes. Servicios, clases, métodos y API en inglés. Interfaz en español.
- Endpoints bajo /api/v1; lógica fuera de routers y SQL en repositorios.
- Componentes con TS, HTML, SCSS y spec separados; soporte de movimiento reducido.
- Nunca leer ni imprimir secretos para diagnóstico. No versionar .env ni secretos_locales.
- No registrar tickets CAS, cookies ni URLs de callback con query. Mantener CSRF en escrituras y sesiones ligadas al modo de autenticación. Los roles locales no se elevan desde atributos no autorizados del CAS.
- No almacenar claves de IA en Angular o imágenes. Documentar variables con valores vacíos.
- Cambios de esquema únicamente por migraciones. No inventar entidades definitivas sin validar casos de uso.
- Pruebas por funcionalidad y evidencia reproducible; no declarar un hito terminado sin su criterio de cierre.
- Mantener trazabilidad con requisitos y actualizar documentación en cada hito.
- No atribuir resultados experimentales ni aprobación académica sin evidencia.
