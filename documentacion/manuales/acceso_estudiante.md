# Acceso como estudiante

## Demostración local disponible

Acceso recomendado: abre http://localhost:4200/login y elige **Probar como estudiante** o **Probar como profesor**. Cierra tu sesión anterior si ya estabas dentro. No necesitas ejecutar un script para alternar. Los dominios mostrados describen los perfiles previstos, no validan identidad. Ambos perfiles son cuentas ficticias compartidas.

### Selección predeterminada por consola (opcional)

Desde la raíz del repositorio, con Docker y la aplicación local preparados:

```powershell
./infraestructura/scripts/select-demo-role.ps1 -Role student
```

Cierra tu sesión en TutorIA y vuelve a entrar por http://localhost:4200/login.
Pulsa «Probar como estudiante». La identidad ficticia será
estudiante.demo@example.org y verás el inicio estudiantil con acceso a práctica.
No necesitas contraseña ni una cuenta de la UPS. Las prácticas de la identidad
docente permanecen separadas de las del estudiante.

Para volver a la demostración docente:

```powershell
./infraestructura/scripts/select-demo-role.ps1 -Role teacher
```

El script valida development/mock, recrea solo el backend y espera su salud.
No modifica .env, no acepta admin y no cambia los roles de usuarios existentes.
La selección afecta a todos los próximos accesos mock de esta instancia, no a las
sesiones abiertas. Es una identidad compartida de prueba, no varias cuentas reales.
Un `docker compose up` sin el complemento puede restaurar la selección base;
vuelve a ejecutar el script para elegir el rol deseado.

## Acceso por dominio institucional

El adaptador existente contempla est.ups.edu.ec como dominio estudiantil. El
flujo previsto es botón UPS → autenticación CAS → validación de ticket en backend
→ comprobación del correo y dominio permitidos → sesión HttpOnly de TutorIA.
El dominio se comprueba sobre la identidad validada por CAS, nunca sobre un correo
enviado por el navegador. En cuentas existentes se conserva el rol local autorizado.

Todavía no se ha conectado ni confirmado el servicio real de la UPS. Se necesitan:

1. URLs autorizadas de login y validación CAS y entorno de pruebas.
2. Dominio HTTPS de TutorIA y callback registrado; política del parámetro state.
3. Atributos confirmados de correo, identificador estable, nombre y apellido.
4. Política aprobada de dominios y roles, certificados y conectividad.

El dominio donde publiques TutorIA es distinto del dominio del correo del alumno.
Publicar la web en un dominio no habilita por sí solo la autenticación institucional.
Consulta la [decisión de autenticación](../decisiones_tecnicas/0002-sso-ups.md).
