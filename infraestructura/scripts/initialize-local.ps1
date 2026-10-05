$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$envPath = Join-Path $projectRoot '.env'
if (Test-Path -LiteralPath $envPath) {
    Write-Host 'Ya existe .env; se conserva sin modificaciones.'
    exit 0
}
$passwordBytes = New-Object byte[] 32
$jwtBytes = New-Object byte[] 48
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $rng.GetBytes($passwordBytes); $rng.GetBytes($jwtBytes) } finally { $rng.Dispose() }
$password = -join ($passwordBytes | ForEach-Object { $_.ToString('x2') })
$jwt = -join ($jwtBytes | ForEach-Object { $_.ToString('x2') })
$template = Get-Content -Raw -LiteralPath (Join-Path $projectRoot '.env.example')
$template = $template -replace '(?m)^DB_PASSWORD=.*$', "DB_PASSWORD=$password"
$template = $template -replace '(?m)^JWT_SECRET=.*$', "JWT_SECRET=$jwt"
[System.IO.File]::WriteAllText($envPath, $template, [System.Text.UTF8Encoding]::new($false))
Write-Host 'Configuración local creada. No se han mostrado ni versionado los secretos.'
