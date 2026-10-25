# Navegación de TutorIA

El menú docente sigue Inicio → Mis documentos → Recursos → Actividades asignadas; Buscar fuentes y Perfiles de aprendizaje son apoyos opcionales, y Uso de generación permite consultar consumo y estados. Recorrido completo: [flujo docente](../manuales/flujo_docente.md).

La implementación vigente se encuentra en `frontend/src/app/compartido/componentes/navegacion/nav.ts`, con `nav.html`, `nav.scss` y `nav.spec.ts`. Los nombres anteriores en la evidencia histórica corresponden a la estructura previa al refactor del 24 de octubre.

## 24 de octubre — menú lateral y renderizado matemático

Rama `feature/resource-preparation`. Solicitud UI/UX implementada: Explorar abre
un menú lateral modal nativo, sin carrusel ni segunda lista de destinos. Cierre
por botón, fondo, Escape y navegación; foco restaurado, fondo inerte, desplazamiento
del fondo bloqueado y movimiento reducido respetado. Portada sin enlaces secundarios
redundantes; se conservan cambios previos del autor en cabecera y pie.

Conceptos separados: Actividades asignadas (ejercicios/materiales del docente) y
Práctica libre (repaso voluntario e historial personal). Rutas y persistencia intactas.
KaTeX y CSS/fuentes empaquetados localmente; importación estática antes de crear las
vistas matemáticas. Directiva síncrona para texto de recursos y ejercicios, incluidos
quiz, soluciones y revisión; actualiza al cambiar entradas. Admite los delimitadores de KaTeX $, $$, \( y \[;
texto como textContent, trust=false y errores tolerados, sin habilitar HTML externo.

Pruebas: 34/34 iniciales en siete archivos; tras nueva prueba de quiz y orden de
menú, 11/11 en los tres archivos afectados (35 casos distintos en total). Build
producción aprobado, inicial 327.05 kB sin advertencias. Navegador local: acceso
docente, menú abierto, Escape/foco y navegación Inicio comprobados visualmente.
No había recursos guardados en la base local; fórmulas verificadas con fixtures,
sin consumir IA. No se ejecutó una matriz completa de tamaños/dispositivos.

Pendiente de commit humano. Revisar frontend y documentación de este bloque sin
incluir LICENSE, modelos ni cambios previos ajenos. Mensaje sugerido:
`feat(ui): simplificar navegación y renderizar fórmulas con KaTeX`.
Próximo: revisar visualmente un recurso real cuando exista en la base local;
continuar seguimiento por tema y filtros de actividades según el plan.

## Implementación anterior — 6 de octubre (referencia histórica)

Implementada el 6 de octubre de 2026 a solicitud directa del autor. Sustituye la barra lateral por cabecera superior fija al desplazarse, pestañas horizontales y un acceso Explorar. Mantiene Angular y la paleta UPS existente.

## Estructura reutilizable

frontend/src/app/compartido/componentes/navegacion/navigation.component.ts concentra destinos según sesión/rol, estado del desplegable, medición del scroll, navegación y foco. HTML, SCSS y pruebas están separados en la misma carpeta. App conserva marca, cuenta, cierre de sesión y contenedor de contenido; integra app-workspace-navigation sin duplicar lógica de autenticación.

Los enlaces usan RouterLink y RouterLinkActive, con aria-current=page. Son enlaces de navegación, no widgets ARIA tab/menubar: Tab sigue el orden natural. No hay destinos ficticios ni enlaces a funcionalidades aún pendientes. Inicio aparece con sesión; Documentos solo para teacher/admin; sin sesión se muestra Acceso UPS. El servidor sigue siendo responsable de autorizar operaciones.

## Interacción

Explorar abre por clic, Enter o Espacio, evitando aperturas accidentales al pasar el cursor. El botón informa aria-expanded y aria-controls. El panel anima altura mediante grid-template-rows, opacidad y desplazamiento durante 220–300 ms. Cerrado tiene inert y aria-hidden, por lo que sus enlaces no reciben foco. Cierra al elegir un destino, finalizar navegación, hacer clic fuera, mover foco fuera o pulsar Escape. Escape devuelve foco al botón. En pantallas bajas el panel puede desplazarse internamente.

Las pestañas principales permiten desplazamiento horizontal táctil y con flechas cuando hay desbordamiento. Las flechas muestran límites mediante estados disabled. La pestaña activa tiene fondo azul suave, texto azul y subrayado amarillo; se revela dentro del contenedor al navegar o cambiar tamaño, sin desplazar toda la página. ResizeObserver se desconecta al destruir el componente. Los estados se miden tras renderizar y al desplazar.

La hoja global ya respeta prefers-reduced-motion. El componente también cambia scroll programático a auto cuando se solicita movimiento reducido. Las áreas de interacción miden al menos 44 px de altura. La cabecera y contenido responden a cambios de anchura; en móvil se simplifica la identidad visual de cuenta. No se agregaron Tailwind ni otro framework: SCSS proporciona las transiciones y mantiene el stack del plan.

## Verificación

24 pruebas Angular aprobadas (8 archivos), de ellas 5 nuevas: apertura/Escape/foco/inert; cierre exterior y foco; destinos por rol; ruta activa/cierre tras navegación; extremos del scroll y movimiento reducido. Ejecutadas en contenedor Node para evitar la demora del entorno local de pruebas.

Compilación de producción en Docker correcta, sin advertencias de presupuesto: bundle inicial aproximadamente 300 kB. Frontend recreado y saludable. Navegador real: apertura en escritorio, Escape, responsive a 390×844, revelado de Documentos activo, desplazamiento en ambos sentidos y navegación a Inicio desde el menú. Anchura de documento observada 375 px con viewport 390 px: sin desbordamiento horizontal de página. Se restauró el tamaño normal al finalizar.

Capturas en documentacion/pruebas/navegacion_desktop.png y navegacion_mobile.png. Este ajuste solo modifica navegación y presentación; no amplía el alcance académico del hito 4.

Comandos reproducibles desde la raíz:

```powershell
docker build --target build -t tutoria-frontend-validation:local -f frontend/Dockerfile .
docker run --rm tutoria-frontend-validation:local npm test -- --watch=false
docker compose up -d --build --no-deps --wait frontend
```

Referencia técnica del motor: [auto-render de KaTeX](https://katex.org/docs/autorender.html) y [opciones de seguridad](https://katex.org/docs/options.html).
