# TutorIA: punto de reentrada para ADAPTIA

Este documento pertenece al proyecto de Patricio y se conserva dentro de su
repositorio. Registra qué aporta TutorIA, su contrato, evidencia y pendientes.
Corte documental: **19/11/2026**.

## Estado del componente

Implementado POST /api/v1/tutoria/generate-content, con Bearer de servicio,
validación, correlación, reserva durable e idempotencia. Swagger muestra solo
esa operación. El contrato genera texto directo; no incluye documentos/RAG,
imágenes ni audio. Las rutas RAG de la aplicación web conservan su funcionamiento.

La conexión desde Moodle se comprobó con LLM apagado: una solicitud válida devolvió
503 y una dificultad inválida, 422. La salida exitosa del manual es un fixture
controlado de interfaz. Falta la primera generación externa con clave y cuota
verificadas; modelo preparado: gemini-3.1-flash-lite.

## Fuentes dentro de este repositorio

- [Contrato, campos, configuración, errores e idempotencia](docs/api/adaptia.md).
- [Configuración inicial y arranque](README.md).
- [Manual visual: índice y límites](docs/api/manual-moodle-tutoria.md).
- [Módulo de integración](backend/app/modulos/integracion_adaptia).
- [Migración aditiva 0018](backend/alembic/versions/0018_adaptia_integration.py).
- [Pruebas unitarias del contrato](backend/tests/unitarios/test_adaptia_integration.py).
- [Pruebas de persistencia](backend/tests/integracion/test_adaptia_database.py).

La clave del proveedor permanece en configuración privada del backend; es distinta
del token interno de ADAPTIA. Consumo desconocido se conserva como null. Las pruebas
controladas y el 503 no acreditan una respuesta pedagógica de Gemini.

## Avance del 19/11/2026: total de tokens desconocido

Se corrigió el servicio ADAPTIA para conservar null cuando el adaptador no informa
total_tokens. Antes sumaba entrada y salida y podía omitir otras categorías. Las
mediciones parciales se conservan en la traza y un cero explícito sigue siendo cero.

Validación dirigida: 90 casos unitarios de ADAPTIA/proveedor y 11 de integración con
PostgreSQL aislado aprobados, incluidos persistencia y replay con total desconocido.
La regresión reprodujo dos fallos antes de la corrección. Ruff aprobado. Estos
resultados usan proveedor controlado y no acreditan una llamada real a Gemini.

Backend reconstruido y actualizado localmente. Se verificó su hash de código y
estado saludable; el smoke por el proxy confirmó API, PostgreSQL/pgvector y Swagger,
y el smoke desde PHP de Moodle conservó 503/422 con correlación. LLM sigue apagado
y la clave Gemini vacía. No se modificaron bases ni se ejecutaron migraciones nuevas.

## Próximo paso

Configurar la clave y confirmar acceso/cuota; después verificar una solicitud
ficticia y guardar su respuesta, correlación y consumo conocido. Publicación real
en cursos y ampliación del contrato a RAG quedan para otra iteración.

## Actualizar ambos niveles

Registrar aquí los avances propios de TutorIA, conservando el contrato detallado
en docs/api/adaptia.md. En el workspace completo, actualizar además
**ADAPTIA/integracion/ESTADO-ACTUAL.md** y **BITACORA.md** con el efecto sobre Moodle
y los demás proyectos. Esa carpeta general no es necesaria para leer este documento
en una copia independiente del repositorio.
