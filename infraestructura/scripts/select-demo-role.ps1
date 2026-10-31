param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('student', 'teacher')]
    [string]$Role
)

$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$composeFiles = @('compose', '-f', (Join-Path $projectRoot 'docker-compose.yml'),
    '-f', (Join-Path $projectRoot 'infraestructura/docker/compose.demo.yml'))
$previousRole = [Environment]::GetEnvironmentVariable('Prototipo_DEMO_ROLE', 'Process')
try {
    $env:Prototipo_DEMO_ROLE = $Role
    # Comprueba la configuración efectiva sin mostrar variables, cookies ni secretos.
    $guard = @'
import sys
try:
    from app.configuracion.settings import Settings
    s = Settings()
    s.validate_auth()
    ok = s.app_env == 'development' and s.auth_mode == 'mock'
except Exception:
    ok = False
print('Configuracion local mock verificada.' if ok else 'Operacion rechazada: requiere development/mock y configuracion valida.')
sys.exit(0 if ok else 1)
'@
    & docker @composeFiles run --no-deps --rm backend python -c $guard
    if ($LASTEXITCODE -ne 0) { throw 'No se cambio el rol. Revisa Docker y la configuracion local.' }
    & docker @composeFiles up -d --no-deps --wait backend
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo confirmar el arranque del backend.' }
    Write-Host "Proximo acceso de demostracion: $Role. Cierra la sesion actual y vuelve a entrar."
    Write-Host 'La seleccion afecta a los proximos accesos de esta instancia; no cambia sesiones existentes.'
    Write-Host 'No modifica .env. Un compose up sin este complemento puede restaurar el rol de la configuracion base.'
}
finally {
    [Environment]::SetEnvironmentVariable('Prototipo_DEMO_ROLE', $previousRole, 'Process')
}
