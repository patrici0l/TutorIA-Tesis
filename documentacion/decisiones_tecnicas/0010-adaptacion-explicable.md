# 0010: Adaptación explícita y auditable del perfil

Estado: preparación implementada y verificada, 8 de octubre de 2026; evaluación de salidas pendiente.

La sección 15 del plan pide apoyo distinto para dominio alto/medio/bajo y refuerzo localizado. Se adopta una política determinista versionada, independiente del proveedor: low→basic/pasos, medium→intermediate/práctica, high→advanced/complejidad. Se conserva la selección del recurso y se sugieren alternativas compatibles con los cuatro contratos existentes.

Se recibe únicamente el UUID del perfil propio. El tema debe coincidir; no hay búsqueda automática del “último estudiante” ni cruce de observaciones de otros propietarios. No se infieren niveles, gravedad de errores o equivalencias temáticas. Los errores informados concentran la orientación, sin etiquetar dificultades globales de una persona. Porcentaje y apoyo recomendado quedan en el snapshot, sin introducir umbrales/ponderaciones académicas inventadas.

La preparación conserva perfil completo, política, motivo y dificultades solicitada/efectiva en una columna nueva nullable. El historial recupera ese snapshot; registros manuales anteriores permanecen compatibles. Las instrucciones contienen reglas del servidor, mientras que las etiquetas se tratan como datos no confiables. El proveedor no recibe identificadores ni el perfil completo.

Consecuencias: la política es revisable y experimental, no sustituye una rúbrica docente. Perfil mal etiquetado o errores irrelevantes requieren revisión humana. No puede determinarse la mayor debilidad sin datos de severidad. La generación sigue siendo explícita y su calidad necesita comparación real antes de cerrar el criterio académico del hito 9.
