$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (!(Test-Path (Join-Path $projectRoot 'frontend/node_modules'))) { throw 'Ejecuta npm ci desde frontend antes de iniciar.' }
if (Get-NetTCPConnection -LocalPort 4200 -State Listen -ErrorAction SilentlyContinue) {
    throw 'El puerto 4200 está ocupado. Detén la interfaz anterior antes de iniciar.'
}
Push-Location (Join-Path $projectRoot 'frontend')
try {
    & npm.cmd start
    if ($LASTEXITCODE -ne 0) { throw 'La interfaz terminó con un error. Revisa la salida anterior.' }
} finally { Pop-Location }
