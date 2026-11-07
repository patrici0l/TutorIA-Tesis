$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$statePath = Join-Path $projectRoot 'infraestructura/herramientas/demo-remota/state.json'
$expectedPath = Join-Path $projectRoot 'infraestructura/herramientas/cloudflared.exe'
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $process = Get-Process -Id $state.pid -ErrorAction SilentlyContinue
    if ($process) {
        if ($process.Path -ne $expectedPath -or
            $process.StartTime.ToUniversalTime().Ticks -ne ([datetime]$state.started).ToUniversalTime().Ticks) {
            throw 'El PID registrado pertenece a otro proceso. No se detuvo ningun proceso.'
        }
        Stop-Process -Id $process.Id
        $process.WaitForExit(10000) | Out-Null
    }
}
& docker compose --env-file "$projectRoot/licencias/secure_data.env" --project-directory $projectRoot -f (Join-Path $projectRoot 'docker-compose.yml') `
    up -d --no-deps --wait backend
if ($LASTEXITCODE -ne 0) { throw 'Tunel cerrado; no se pudo confirmar la restauracion del backend local.' }
if (Test-Path -LiteralPath $statePath) { Remove-Item -LiteralPath $statePath }
$linkPath = Join-Path $projectRoot 'infraestructura/herramientas/demo-remota/enlace.txt'
if (Test-Path -LiteralPath $linkPath) { Remove-Item -LiteralPath $linkPath }
Write-Host 'Demo remota cerrada. Acceso local restaurado; datos y documentos conservados.'
