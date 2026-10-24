# Revisión de integrales, asignación y disponibilidad

24 de octubre de 2026. Rama `feature/resource-preparation`. Cambios pendientes de
revisión y commit humano; se conservaron los cambios previos de acceso remoto.

## Diagnóstico comprobado

- Un quiz de integrales de cinco preguntas estaba guardado con error llm_incomplete,
  máximo de salida 512, entrada 1789 y salida 508. El adaptador solo emite ese código
  cuando Gemini responde MAX_TOKENS. La respuesta truncada no es un recurso válido.
- AssignmentSubmission admitía exclusivamente derivadas-v1/reglas-v1 y rechazaba
  resource_id como campo extra. Se reprodujeron literal_error y extra_forbidden con
  el código previo desplegado. La pantalla ofrecía únicamente esos dos bancos.
- La configuración de salida actual se conservaba en 512 pese al valor por defecto
  anterior de 1024. Se ajustó únicamente esa variable local a 4096 y el valor por
  defecto en Settings/Compose/.env.example al mismo máximo permitido existente.

## Cambios

Migración 0015_resource_assignments aplicada: resource_id opcional, FK y check de
coherencia. Recursos propios succeeded asignables con version resource-v1. Detalle
protegido por docente propietario o alumno destinatario; entrega material y fuentes,
sin prompts ni perfiles privados. Listado conserva paginación y datos previos.
Material generado se comparte con soluciones para consulta; no añade corrección de
quizzes dinámicos, nota, entregas ni seguimiento de lectura.

Enlace Asignar este recurso desde resultado e historial. Formulario propone título,
explica el tipo de actividad y conserva UUID en reintentos. Recursos pendientes/ajenos
no caen silenciosamente en un banco de derivadas. Confirmaciones de guardar/asignar,
validaciones, errores y controles de sesión/CSRF siguen activos.

Aviso global de cuenta de prueba, textos de demostración y apellido de demostración
en cabecera retirados. Personalización opcional plegable y recorrido de tres pasos.
Se conserva la validación de datos sintéticos requerida por el contrato actual de perfiles.

GET /api/v1/content/quota: solo teacher/admin; no-store; enabled, daily_limit, used,
remaining, resets_at, max_output_tokens y timeout_seconds. Lee la misma persistencia
de reservas del límite de generación, compartido entre docentes, incluyendo fallos,
con reinicio a medianoche UTC (19:00 del día anterior en Ecuador continental).
El porcentaje mostrado corresponde al cupo utilizado. La generación en curso muestra
su etapa y barra indeterminada: el proveedor no proporciona porcentaje de ejecución.
El saldo de tokens del proveedor es desconocido; no se presenta como cero ni como cupo
restante de TutorIA. El consumo reportado se conserva en trazabilidad por recurso.

Rechazos 401/403/429/503 previos a reservar permiten reintentar la preparación; los
resultados inciertos de red conservan el bloqueo de reenvío para evitar duplicados.

## Verificación real

Por HTTP en localhost:4200 con dos sesiones separadas, docente y estudiante:

1. Repetición de la solicitud original de integrales (quiz5) con 4096 tokens: 201 en
   preparar y 200 succeeded al generar, cinco preguntas completas, validadas y persistidas.
2. Consumo devuelto: entrada 1789, salida 637, total 2426; máximo conservado 4096.
   Una llamada Gemini en este bloque. Cupo pasó de 1 usado/4 restantes a 2 usados/3 restantes.
3. Asignación 200; estudiante obtiene el mismo recurso y fuentes, 200. Reintento exacto
   devuelve la misma asignación. Escritura sin cabecera CSRF 403, creación por estudiante
   403, historial docente inaccesible para estudiante 403; logout de ambas sesiones 204.
4. Se conservan el recurso y su actividad abiertos para revisión en la aplicación.

No se cambió el cupo diario de cinco ni el timeout local de treinta segundos. La subida
correcta de este caso no garantiza que toda solicitud futura quepa ni certifica exactitud
matemática: continúa la revisión docente de contenido y fuentes.

## Pruebas automatizadas

- Angular: 97 pruebas, 22 archivos, aprobadas mediante `npm test -- --watch=false`.
- Backend/PostgreSQL: 91 aprobadas y una omitida por no tener las fuentes Angular
  dentro del contenedor. Esa comprobación pasó localmente junto con las 14 pruebas
  de test_practice_validation.py.
- Cobertura: cuatro tipos de recurso, recursos pendientes/ajenos, coherencia de contrato,
  privacidad del detalle, permisos, CSRF, idempotencia, estado y persistencia; límites
  compartidos, fallos reservados y cambio de día UTC; vista de cupo, recuperación de
  error de disponibilidad y reintento tras 429.
- Build de producción Angular y análisis Ruff aprobados. Migración 0015 aplicada.

Comando backend reproducible desde la raíz:

```powershell
docker compose -f docker-compose.yml -f infraestructura/docker/compose.test.yml run --rm --no-deps test-backend python -m pytest -q -rs tests/integracion/test_generation_quota.py tests/integracion/test_resource_assignments.py tests/integracion/test_assignments.py tests/unitarios/test_generation_messages.py tests/unitarios/test_settings.py tests/unitarios/test_generation_api.py tests/unitarios/test_history_api.py tests/unitarios/test_content_preparation_api.py tests/unitarios/test_practice_validation.py tests/unitarios/test_content_contracts.py
.\.venv\Scripts\python.exe -m pytest backend/tests/unitarios/test_practice_validation.py -q
```

La ejecución inicial de todas las unitarias locales no pudo recoger test_vector_index
porque el venv de Windows carece de numpy. Las verificaciones finales de este bloque
usan el contenedor del proyecto con dependencias instaladas; no se afirma haber pasado
toda la suite del repositorio.

## Revisión visual y pendientes

Navegador verificó login, inicio y Preparar recursos sin el aviso global, y abrió el
historial. Después Work deshabilitó el navegador, por lo que el último ajuste de cupo y
material estudiantil tiene verificación de componentes y HTTP, pero no captura visual
final. Revisar visualmente en escritorio y móvil cuando vuelva a estar habilitado.

Pendiente commit humano de este alcance (excluir cambios previos ajenos al bloque).
Mensaje sugerido: `fix: corrige generacion y asignacion de recursos y muestra cupo disponible`.
