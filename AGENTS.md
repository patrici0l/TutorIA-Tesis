# Reglas de desarrollo de TutorIA-Lucero

Leer README.md y documentacion/PLAN_DE_TRABAJO.md antes de implementar. La fuente completa está en documentacion/investigacion/plan_implementacion_fuente.txt. Respetar el avance vertical del plan; no saltar a LLM antes de validar recuperación RAG.

La instrucción del autor del 5 de octubre de 2026 reemplaza la autenticación del plan: SSO/CAS UPS, modos mock/cas y sesión HttpOnly. Prohibido agregar Google OAuth, registro por correo/contraseña o password/password_hash a usuarios institucionales. Leer documentacion/decisiones_tecnicas/0002-sso-ups.md. No conectar al CAS real hasta disponer de parámetros autorizados por TI.

Actualizar documentacion/CONTINUIDAD.md al cerrar cada bloque y antes de interrumpir trabajo extenso: estado, pruebas reales, cambios pendientes, rama y próximo paso. No inventar porcentajes de contexto o resultados.

Mantener seguimiento_privado/BITACORA.md como itinerario personal por fecha y sesión (America/Guayaquil): objetivo, trabajo realizado, pruebas/resultados, limitaciones, commit y próximo paso. Esta carpeta está excluida de Git; nunca forzar su incorporación ni copiar la bitácora a documentación pública. Reconstrucciones históricas deben indicar su fuente y no inventar horarios/duración. No registrar secretos ni datos institucionales reales. Instrucción vigente del autor del 9 de octubre: cero commits automáticos. Al cerrar cada punto verificable, notificar explícitamente al autor los cambios que debe revisar y commitear, con alcance y mensaje sugerido. No ejecutar git commit por cuenta propia. Registrar el hash solo cuando exista y se haya verificado; mientras tanto indicar pendiente de commit humano. No etiquetar pendientes como terminados ni incluir cambios ajenos.

Alcance vigente del 9 de octubre: no conectar sistemas universitarios en esta etapa inicial; CAS y recepción institucional de rendimiento quedan fuera del alcance actual, con adaptadores conservados. Mantener el diseño de autenticación institucional por dominio, modo mock y sesión HttpOnly; no sustituirlo por contraseñas locales ni confiar en un correo enviado por Angular. Pruebas proporcionales al cambio y riesgo: priorizar casos relevantes y regresiones afectadas, sin duplicaciones ni repetición completa por cambios solo documentales. No eliminar pruebas útiles solo para reducir su número.

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
