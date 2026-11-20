# Versión 0.3 — avance local

19/11/2026. Rama `feature/v0.3-ejemplos-pistas`, basada en `362334c`.
Este avance no declara cerrada la v0.3. Jefferson continuará sus cambios en otras
ramas; antes de unirlos corresponde revisar posibles cruces.

## Implementado

- Ejemplo resuelto independiente (`EXAMPLE`): enunciado, pasos y resultado.
- Pista independiente (`HINT`): enunciado y una a tres ayudas, sin campos de solución.
  El problema se indica en el tema y objetivo. El prompt pide no revelar el resultado;
  el validador estructural no certifica que una frase no lo revele: revisar el contenido.
- Selección en preparación docente, presentación con fuentes e identificación en historial.
- Contratos de actividades actualizados para guardar, asignar y consultar ambos tipos.
- Contratos de generación directa y preparación experimental ampliados a seis recursos.
- Prompts versionados: RAG v3, RAG con perfil v6, directo v2 y pares experimentales v2.
  Los recursos y prompts históricos guardados no se reescriben.
- [Guía y JSON para Jefferson](../docs/api/README.md): flujo actual de preparación y
  generación, respuestas simuladas, errores, sesión y prueba local.

Los nuevos tipos de recurso conservan el almacenamiento JSON existente.
La conexión externa añade la migración `0018_external_sources` para guardar procedencia
estructurada; no reclasifica documentos anteriores ni modifica sus permisos.
Los cuatro tipos anteriores conservan su estructura, incluidos los ejemplos dentro
de explicaciones y las pistas dentro de ejercicios.

## Conexión real con Wikipedia en español

Desde **Documentos → Buscar fuentes externas**, el docente busca un tema, revisa una
versión del artículo y confirma su incorporación a una asignatura. Se guarda como TXT
adaptado, con enlace permanente, versión, fecha, licencia y atribución. La captura JSON
original de MediaWiki (HTML y wikitext) se conserva junto al documento y se puede
descargar desde su sección de origen; ambas copias tienen huellas de integridad.

El material llega sin procesar ni habilitar. Se utiliza el flujo existente de proceso,
índice, revisión y habilitación. La búsqueda y preparación conservan su procedencia
externa; la retirada impide nuevas recuperaciones. Los respaldos de la carpeta de
materiales incluyen también las capturas originales. Eliminar expresamente el material
elimina ambos archivos.

La importación vuelve a consultar la revisión elegida y comprueba que el texto coincide
con el revisado. Solo se consulta el host fijo de Wikipedia en español, sin seguir
redirecciones ni aceptar direcciones del navegador. Hay límites de tiempo, tamaño y
consultas por docente. Las fórmulas MathML compatibles se convierten a TeX; una fórmula
no compatible bloquea la importación. Se omiten imágenes, multimedia y bloques de
navegación; la revisión humana de fórmulas, tablas y contenido sigue siendo necesaria.

Cada importación crea un documento independiente; no se actualiza automáticamente ni
se deduplican importaciones repetidas. La revisión fijada y las copias conservadas
permiten identificar qué texto se usó aunque Wikipedia cambie.

## Verificación al 19 de noviembre

- Backend: 590 pruebas unitarias aprobadas y una omitida; dos avisos de deprecación.
- PostgreSQL: 73 pruebas de integración aprobadas y dos omitidas, en una base temporal
  separada con las migraciones aplicadas hasta `0018_external_sources`.
- Frontend: 169 pruebas aprobadas en 30 archivos; compilación Angular y Ruff aprobados.
- Consulta real de los artículos Derivada y Distribución normal, con revisión, licencia
  y texto matemático recuperados.
- Un E2E real aprobado después del ajuste visual final: búsqueda → revisión → importación
  de Derivada → captura original → extracción → índice E5 real → habilitación → RAG →
  preparación → retirada. También comprueba exclusión antes de publicar y tras retirar.
- Capturas revisadas en escritorio y móvil; sin desbordamiento horizontal a 390 px.
- Pruebas negativas: roles, propietario, cabecera, falta de confirmación, texto alterado,
  tamaño excesivo, errores remotos, tiempos de espera y captura original modificada.
- Los JSON de ejemplo para Jefferson siguen siendo simulados, validados contra contratos.

Se consultó Wikipedia realmente; no se hicieron llamadas a modelos generativos. La
prueba utilizó una asignatura de prueba y retiró/eliminó el material al finalizar.
La aplicación habitual y sus datos no se actualizaron: las verificaciones se ejecutaron
en servicios temporales separados. La migración y reconstrucción local quedan pendientes
para ver el cambio en la instalación habitual; no se realizó despliegue público.

## Pendiente

Login institucional y despliegue se revisarán con el tutor. Continúan pendientes los
acuerdos ADAPTIA, acceso del estudiante a solicitudes de generación, ejecuciones
comparables de tres modelos, selección y aceptación del corpus externo y piloto de ambas
asignaturas. Falta el selector experimental entre fuentes docentes y docentes más externas;
por ahora RAG usa todas las fuentes propias habilitadas de la materia. CORE, OpenAlex y
Wolfram Alpha no están integrados.
La aceptación docente de v0.2 sigue separada del cierre técnico marcado en Git.
