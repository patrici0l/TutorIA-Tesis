# Reglas de desarrollo de TutorIA-Lucero

Leer README.md y documentacion/PLAN_DE_TRABAJO.md antes de implementar. La fuente completa está en documentacion/investigacion/plan_implementacion_fuente.txt. Respetar el avance vertical del plan; no saltar a LLM antes de validar recuperación RAG.

- Stack: Angular, FastAPI, PostgreSQL/pgvector, Alembic, Docker.
- Carpetas de dominio en español sin tildes. Servicios, clases, métodos y API en inglés. Interfaz en español.
- Endpoints bajo /api/v1; lógica fuera de routers y SQL en repositorios.
- Componentes con TS, HTML, SCSS y spec separados; soporte de movimiento reducido.
- Nunca leer ni imprimir secretos para diagnóstico. No versionar .env ni secretos_locales.
- No almacenar claves de IA en Angular o imágenes. Documentar variables con valores vacíos.
- Cambios de esquema únicamente por migraciones. No inventar entidades definitivas sin validar casos de uso.
- Pruebas por funcionalidad y evidencia reproducible; no declarar un hito terminado sin su criterio de cierre.
- Mantener trazabilidad con requisitos y actualizar documentación en cada hito.
- No atribuir resultados experimentales ni aprobación académica sin evidencia.
