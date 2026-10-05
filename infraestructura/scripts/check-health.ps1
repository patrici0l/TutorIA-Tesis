param([string]$BaseUrl = 'http://localhost:4200')
$ErrorActionPreference = 'Stop'
$health = Invoke-RestMethod -Uri "$BaseUrl/api/v1/health" -TimeoutSec 12
foreach ($field in @('status', 'api', 'database', 'pgvector')) {
    if ($health.$field -ne 'ok') { throw "Verificación fallida: $field" }
}
Write-Host 'Conexión nginx -> FastAPI -> PostgreSQL/pgvector verificada.'
