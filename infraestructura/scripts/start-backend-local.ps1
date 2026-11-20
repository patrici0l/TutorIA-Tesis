param([switch]$NoReload)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$python = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (!(Test-Path $python)) { throw 'Falta .venv. Sigue la preparación sin Docker del README.' }
if (!(Test-Path (Join-Path $projectRoot 'licencias/backend.env'))) { throw 'Configura licencias/backend.env siguiendo el README.' }
if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
    throw 'El puerto 8000 está ocupado. Detén el backend anterior antes de iniciar.'
}
Push-Location (Join-Path $projectRoot 'backend')
try {
    $arguments = @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000')
    if (!$NoReload) { $arguments += '--reload' }
    & $python @arguments
    if ($LASTEXITCODE -ne 0) { throw 'El backend terminó con un error. Revisa la salida anterior.' }
} finally { Pop-Location }
