# Navegación de TutorIA

## Destinos por rol

- Docente: Inicio → Mis documentos → Recursos → Actividades asignadas. Buscar fuentes y Perfiles de aprendizaje son apoyos opcionales; Uso de generación muestra consumo y estados.
- Estudiante: Inicio → Actividades asignadas → Práctica libre.
- Sin sesión: pantalla de acceso sin menú Explorar ni enlace Entrar duplicado.

El [flujo docente](../manuales/flujo_docente.md) describe el recorrido completo. Las
actividades asignadas comparten contenido con un estudiante; la práctica libre es
repaso voluntario con historial personal.

## Implementación e interacción

`frontend/src/app/compartido/componentes/navegacion/nav.ts` concentra los destinos
por rol. Su plantilla, estilos y pruebas son `nav.html`, `nav.scss` y `nav.spec.ts`.
`app.ts` conserva la cabecera, la cuenta y el cierre de sesión.

Explorar se muestra al disponer de sesión y abre un diálogo modal lateral. Cierra
con su botón, el fondo, Escape o al navegar, y devuelve el foco al botón de apertura.
El fondo queda inerte y sin
scroll; el menú admite desplazamiento interno y respeta movimiento reducido.
Los enlaces usan RouterLink, RouterLinkActive y aria-current. El servidor valida
los permisos de cada operación.

## Fórmulas

`compartido/directivas/math-text.directive.ts` importa KaTeX antes de crear las
vistas que lo utilizan. Renderiza al recibir o cambiar el texto; los estilos y las
fuentes se incluyen localmente. El contenido se introduce como texto, con
`trust: false` y tolerancia a errores de LaTeX. Admite delimitadores de línea y de
bloque; las ecuaciones largas se desplazan dentro de su contenedor.

## Verificación

Las pruebas de navegación cubren apertura, cierre, foco, rol y ruta activa. Las
pruebas matemáticas cubren fracciones, integrales, actualización y rechazo de HTML.
Los resultados ejecutados y pendientes se registran en [Continuidad](../CONTINUIDAD.md).
La versión anterior con carrusel se conserva en el historial de Git y sus capturas
en `documentacion/pruebas/navegacion_desktop.png` y `navegacion_mobile.png`.
