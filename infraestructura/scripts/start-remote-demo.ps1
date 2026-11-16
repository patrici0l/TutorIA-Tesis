param(
    [ValidateRange(1, 65535)]
    [int]$FrontendPort = 4200
)

$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runtime = Join-Path $projectRoot 'infraestructura/herramientas/demo-remota'
$statePath = Join-Path $runtime 'state.json'
$overridePath = Join-Path $runtime 'compose.remote.json'
$cloudflared = Join-Path $projectRoot 'infraestructura/herramientas/cloudflared.exe'
$compose = @('compose', '--env-file', (Join-Path $projectRoot 'licencias/secure_data.env'), '--project-directory', $projectRoot,
    '-f', (Join-Path $projectRoot 'docker-compose.yml'))

if (Test-Path -LiteralPath $statePath) {
    throw 'Hay una demo registrada. Ejecuta stop-remote-demo.ps1 antes de iniciar otra.'
}
if (-not (Test-Path -LiteralPath $cloudflared)) {
    throw 'Falta infraestructura/herramientas/cloudflared.exe. Consulta el manual de demo remota.'
}
& $cloudflared --version
if ($LASTEXITCODE -ne 0) { throw 'cloudflared no se puede ejecutar. Instala la version oficial para Windows x64.' }
New-Item -ItemType Directory -Force -Path $runtime | Out-Null

# Verifica el modo base sin imprimir configuracion privada ni cambiar .env.
$guard = @'
import sys
from app.configuracion.settings import Settings
try:
    s = Settings()
    s.validate_auth()
    ok = s.app_env == 'development' and s.auth_mode == 'mock' and not s.auth_demo_public_origin
except Exception:
    ok = False
print('Modo local verificado.' if ok else 'Se requiere configuracion local development/mock.')
sys.exit(0 if ok else 1)
'@
& docker @compose build backend
if ($LASTEXITCODE -ne 0) { throw 'No se pudo construir el backend.' }
& docker @compose run --rm --no-deps backend python -c $guard
if ($LASTEXITCODE -ne 0) { throw 'No se habilito el acceso remoto.' }
& docker @compose up -d --build --wait
if ($LASTEXITCODE -ne 0) { throw 'El entorno local no esta saludable.' }
$binding = (& docker @compose port frontend 8080) -join ''
if ($LASTEXITCODE -ne 0 -or $binding.Trim() -ne "127.0.0.1:$FrontendPort") {
    throw 'El puerto indicado no coincide con el frontend local de este proyecto.'
}
$health = Invoke-RestMethod "http://127.0.0.1:$FrontendPort/api/v1/health"
if (-not $health) { throw 'No se pudo verificar la interfaz local.' }
$modelGuard = @'
import sys
from app.configuracion.settings import get_settings
from app.modulos.rag.servicios.prepare_model import verified
from app.modulos.rag.servicios.model_spec import ARTIFACTS
directory = get_settings().embedding_model_path
ok = all(verified(directory / name, size, digest) for name, (size, digest) in ARTIFACTS.items())
print('Modelo local verificado.' if ok else 'Falta preparar el modelo de busqueda local.')
sys.exit(0 if ok else 1)
'@
& docker @compose exec -T backend python -c $modelGuard
if ($LASTEXITCODE -ne 0) {
    throw 'Desde la raiz: docker compose --env-file licencias/secure_data.env --profile embeddings run --rm prepare-embeddings'
}

$tunnelProcess = $null
$backendChanged = $false
try {
    $runId = [guid]::NewGuid().ToString('N')
    $stdout = Join-Path $runtime "$runId.stdout.log"
    $stderr = Join-Path $runtime "$runId.stderr.log"
    $arguments = @('tunnel', '--no-autoupdate', '--url', "http://127.0.0.1:$FrontendPort")
    $tunnelProcess = Start-Process -FilePath $cloudflared -ArgumentList $arguments `
        -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    # Registra inmediatamente el proceso para poder detenerlo incluso si se interrumpe el arranque.
    @{ pid = $tunnelProcess.Id; started = $tunnelProcess.StartTime.ToUniversalTime().ToString('o') } |
        ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
    $publicOrigin = $null
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        $tunnelProcess.Refresh()
        if ($tunnelProcess.HasExited) { throw 'El tunel termino antes de estar disponible.' }
        $logs = ((Get-Content -LiteralPath $stdout -Raw -ErrorAction SilentlyContinue),
            (Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue)) -join "`n"
        if ($logs -match 'https://[a-z0-9]+(?:-[a-z0-9]+)*\.trycloudflare\.com') {
            $publicOrigin = $Matches[0]
            break
        }
        Start-Sleep -Seconds 1
    }
    if (-not $publicOrigin) { throw 'No se recibio el dominio temporal en 60 segundos.' }
    @{ services = @{ backend = @{ environment = @{
        AUTH_DEMO_PUBLIC_ORIGIN = $publicOrigin
        AUTH_COOKIE_SECURE = 'true'
        AUTH_CALLBACK_URL = "$publicOrigin/api/v1/auth/callback"
        AUTH_FRONTEND_URL = "$publicOrigin/inicio"
        AUTH_LOGIN_URL = "$publicOrigin/login"
    } } } } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $overridePath -Encoding utf8
    $backendChanged = $true
    & docker @compose -f $overridePath up -d --no-deps --wait backend
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo habilitar el backend remoto.' }
    # El dominio puede tardar en propagarse. No anunciar un enlace sin comprobarlo.
    $remoteReady = $false
    for ($attempt = 0; $attempt -lt 12; $attempt++) {
        $tunnelProcess.Refresh()
        if ($tunnelProcess.HasExited) { throw 'El tunel termino durante la verificacion remota.' }
        try {
            & (Join-Path $PSScriptRoot 'check-health.ps1') -BaseUrl $publicOrigin
            $page = Invoke-WebRequest -Uri "$publicOrigin/login" -TimeoutSec 12
            if ($page.StatusCode -ne 200 -or $page.Content -notmatch '<app-root') {
                throw 'La interfaz publica no responde correctamente.'
            }
            $remoteReady = $true
            break
        }
        catch { Start-Sleep -Seconds 2 }
    }
    if (-not $remoteReady) { throw 'No se pudo verificar el acceso HTTPS publico.' }
    Set-Content -LiteralPath (Join-Path $runtime 'enlace.txt') -Value $publicOrigin -Encoding utf8
    Write-Host "Enlace de demostracion: $publicOrigin"
    Write-Host 'Acceso publico: cualquiera con el enlace puede elegir profesor o estudiante, sin correo ni PIN.'
    Write-Host 'Usa el enlace HTTPS tambien en este equipo. Los perfiles ficticios comparten datos por rol.'
    Write-Host 'Mantén Docker y el equipo encendidos. Para cerrar: ./infraestructura/scripts/stop-remote-demo.ps1'
    Write-Host 'Comparte el enlace con tu profesor y pidele elegir el perfil Profesor.'
}
catch {
    if ($null -ne $tunnelProcess -and -not $tunnelProcess.HasExited) {
        Stop-Process -Id $tunnelProcess.Id -ErrorAction SilentlyContinue
    }
    if ($backendChanged) {
        & docker @compose up -d --no-deps --wait backend
        if ($LASTEXITCODE -ne 0) {
            throw 'Tunel cerrado; restauracion local pendiente. Ejecuta stop-remote-demo.ps1.'
        }
    }
    if (Test-Path -LiteralPath $statePath) { Remove-Item -LiteralPath $statePath }
    throw
}
