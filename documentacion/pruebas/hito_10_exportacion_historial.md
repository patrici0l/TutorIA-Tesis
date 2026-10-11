# Descarga del historial con trazabilidad

10 de octubre de 2026. El autor indicó continuar el plan dejando Gemini pendiente.
Esta función de trazabilidad/revisión del MVP no realiza inferencias ni consulta cuota.

## Uso y alcance

En `/recursos`, abrir **Mis recursos**, cargar y abrir un registro. Aparece
**Descargar recurso y trazabilidad · JSON**, incluso si su estado es preparado,
en proceso o fallido. El archivo `tutoria-recurso-{UUID}.json` conserva el HistoryDetail
consultado: preparación, contenido disponible, fuentes originales, adaptación/perfil
asociado, fechas, estado, auditoría y valores desconocidos sin sustituirlos por cero.
Si el estado cambia después, abrir nuevamente el historial para obtener otra fotografía.

La descarga utiliza el detalle ya autorizado y cargado por la API existente, crea un Blob
JSON UTF-8 en el navegador y no realiza HTTP. No se agrega una ruta pública ni se envía
material a un proveedor. El botón solo aparece al restaurar un registro del historial;
no exporta valores de un formulario ni presenta una preparación reciente como traza leída.
El enlace temporal se retira y su URL se libera después del clic; se limpia inmediatamente
ante fallo. El nombre solo admite el UUID, sin títulos, rutas ni identidad del perfil.
Los mensajes describen una solicitud de descarga, no certifican escritura en disco.

El archivo incluye los textos de las fuentes y perfil visibles para su propietario.
No es una copia completa de la DB/documentos ni una recreación del prompt: el contrato
público no incluye instrucciones, prompt crudo, propietario interno, secretos ni respuesta
original del estudiante en FEEDBACK. La revisión offline terminal admite el formato de
HistoryDetail para explicaciones/ejercicios/quiz adaptados; no certifica calidad pedagógica.
Si no hay auditoría histórica, conserva esa ausencia. No añade evaluaciones humanas.

## Verificación

18 pruebas Angular enfocadas aprobadas en Docker sin red, 1.24 s:
cuatro del servicio de descarga, tres del componente, nueve de preparación y dos del
historial. Comprueban igualdad del JSON con el detalle consultado, UTF-8, cero/null,
texto parecido a HTML sin insertarlo como HTML, nombre UUID, liberación diferida de URL,
limpieza ante fallo, rechazo de ID inválido, mensajes recuperables, limpieza al cambiar
recurso y ausencia de HTTP al descargar desde la página real del componente.

Primer intento: 16/17 pasaron; FileReader quedó bloqueado por temporizadores ficticios
generales del test. Se acotó el reloj ficticio a setTimeout/clearTimeout y pasaron17/17.
Después de añadir la prueba de integración de página, el conjunto final pasó18/18.
No fue un fallo observado en un navegador real. Prettier aplicado a archivos afectados.

Build de producción aprobado: 306.23 kB inicial, módulo preparación37.98 kB.
Frontend reconstruido/desplegado, backend/frontend/PostgreSQL healthy y check-health
aprobado. 21 generaciones conservan su huella de campos anteriores
`5c1ec598642e8d0c35e79d3d61aed1ae`. Sin cambios de backend/esquema/configuración ni IA.
Pruebas DOM simulan el clic del navegador: no se afirma descarga manual real en esta sesión.

Reproducir el conjunto con la imagen de la etapa build y los cuatro archivos anteriores:

```powershell
docker build --file frontend/Dockerfile --target build --tag tutoria-frontend-tests:local .
docker run --rm --network none tutoria-frontend-tests:local npm test -- --watch=false --include=src/app/modulos/contenidos/servicios/resource-export.service.spec.ts --include=src/app/modulos/contenidos/componentes/resource-export/resource-export.component.spec.ts --include=src/app/modulos/contenidos/paginas/preparacion/preparation.component.spec.ts --include=src/app/modulos/contenidos/componentes/resource-history/resource-history.component.spec.ts
```

## Continuación y commit

Gemini/piloto salida1024 quedan pendientes por instrucción directa del autor; ya no se
tratan como requisito para avanzar las tareas independientes. Próximo: herramientas y
matriz de evaluación de resultados guardados, con decisiones humanas explícitas; después
endurecimiento y documentación del MVP. No se declara benchmark real ni cierre académico.

Revisar/commitear servicio/componente de exportación con sus pruebas, integración en
preparación y documentación del bloque. Mensaje sugerido:
`feat: descarga recursos del historial con trazabilidad`.
No incluir automáticamente los otros bloques pendientes; cero commits automáticos.
