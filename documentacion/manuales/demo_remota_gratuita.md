# Demo remota gratuita mediante enlace público

Por solicitud explícita del autor del 23 de octubre de 2026, cualquier persona con
el enlace puede entrar con los botones de profesor y estudiante. No hay correo,
PIN, contraseña ni cuentas nuevas. Esta decisión reemplaza la propuesta inicial
con restricción por correo.

## Compartir con el profesor

1. Mantener Docker Desktop y la computadora encendidos, con internet y sin suspensión.
2. Desde la raíz del proyecto, ejecutar en PowerShell:

```powershell
./infraestructura/scripts/start-remote-demo.ps1
```

3. Copiar el enlace HTTPS mostrado y enviarlo al profesor. También se guarda en
   `secretos_locales/demo-remota/enlace.txt`.
4. El profesor abre el enlace y pulsa **Probar como profesor**. Puede cerrar sesión
   y elegir **Probar como estudiante** para revisar el otro recorrido.

El script verifica servicios y modelo local, inicia Cloudflare Quick Tunnel y
configura las redirecciones HTTPS. Requiere el ejecutable oficial en
`secretos_locales/herramientas/cloudflared.exe`, ya instalado en este equipo.
Si el frontend usa otro puerto, indicar `-FrontendPort` con el puerto configurado.
No modifica `.env`, no consume IA al iniciar y no conecta sistemas UPS.

## Cerrar y volver a abrir

```powershell
./infraestructura/scripts/stop-remote-demo.ps1
```

El cierre detiene el proceso de túnel registrado y restaura el acceso local,
conservando documentos y base de datos. Si falla Docker, repetir tras recuperarlo.
Para una nueva sesión ejecutar otra vez el inicio: se genera un enlace diferente.
Si el inicio se interrumpe, ejecutar el cierre antes de volver a intentarlo.
Durante la demo usar el enlace HTTPS también en este equipo; no ejecutar otros
comandos `docker compose up` ni el selector local de rol, pues podrían restaurar
las URLs locales. No eliminar volúmenes para solucionar problemas.

## Alcance y limitaciones

- El enlace es público: cualquiera que lo reciba puede elegir cualquiera de los
  dos roles ficticios, consultar, crear o eliminar datos según las funciones del rol.
- Cada rol comparte los mismos datos locales entre visitantes. No hay cuentas
  individuales ni aislamiento de los cambios del tutor. Usar material de demostración.
- La computadora, Docker y el túnel deben seguir activos. La velocidad depende de
  la conexión local. No se contrata alojamiento ni dominio; se usa electricidad e
  internet del autor.
- El dominio cambia cada vez y Cloudflare no garantiza disponibilidad. El tráfico
  pasa por Cloudflare. El túnel no proporciona respaldos de la base local.
- Límite de 200 solicitudes simultáneas en vuelo (no 200 usuarios), HTTP 429 al
  superarlo; no se soporta SSE.
- Gemini conserva su configuración y cupo global actual: las generaciones de los
  visitantes comparten ese cupo. No se activa facturación ni se amplían límites.
- La extracción de PDF escaneados requiere OCR todavía pendiente. El contenido
  generado y la extracción matemática requieren revisión del docente.

## Configuración técnica

`AUTH_DEMO_PUBLIC_ORIGIN` permite un origen HTTPS exacto de `trycloudflare.com`
solo en development/mock con cookies Secure. Las tres URLs de autenticación deben
coincidir. Sin la excepción, mock sigue restringido a loopback. No se toman las
redirecciones de cabeceras del visitante. Se conservan HttpOnly, SameSite y CSRF.
Esta validación de origen no es una restricción de visitantes: el túnel es público.
Estado, logs y complemento Compose quedan en `secretos_locales`, excluido de Git.

[Documentación oficial de Quick Tunnels y límites](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).
