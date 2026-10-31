param([Parameter(Mandatory = $true)][string]$BackupDirectory)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$backupPath = (Resolve-Path -LiteralPath $BackupDirectory).Path

function Invoke-DockerChecked {
    param([string[]]$DockerArguments)
    $result = & docker @DockerArguments
    if ($LASTEXITCODE -ne 0) { throw 'Falló la comprobación del respaldo con Docker.' }
    return $result
}

Push-Location $projectRoot
$testContainerId = $null
try {
    $manifest = Get-Content -LiteralPath (Join-Path $backupPath 'manifest.json') -Raw | ConvertFrom-Json
    if ($manifest.format_version -ne 'tutoria-local-backup-v1') { throw 'Formato de respaldo no admitido.' }
    $names = @($manifest.archives | ForEach-Object { $_.path })
    if ($names.Count -ne 2 -or 'database.dump' -notin $names -or 'documents.tar.gz' -notin $names) {
        throw 'El manifiesto no contiene los dos archivos previstos.'
    }
    foreach ($entry in $manifest.archives) {
        $path = Join-Path $backupPath $entry.path
        if ((Get-Item -LiteralPath $path).Length -ne $entry.bytes -or
            (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
            throw 'Respaldo alterado o incompleto. No se inició restauración.'
        }
    }
    $postgresId = Invoke-DockerChecked -DockerArguments @('compose', 'ps', '--all', '-q', 'postgres')
    $backendId = Invoke-DockerChecked -DockerArguments @('compose', 'ps', '--all', '-q', 'backend')
    if (-not $postgresId -or -not $backendId) { throw 'Deben existir los contenedores del proyecto para identificar las imágenes.' }
    $postgresImage = Invoke-DockerChecked -DockerArguments @('inspect', '--format', '{{.Image}}', $postgresId)
    $backendImage = Invoke-DockerChecked -DockerArguments @('inspect', '--format', '{{.Image}}', $backendId)

    # PostgreSQL temporal: sin red, puertos, secretos ni volúmenes del proyecto.
    $testContainerId = Invoke-DockerChecked -DockerArguments @(
        'run', '-d', '--pull', 'never', '--network', 'none',
        '--tmpfs', '/var/lib/postgresql/data:rw,size=512m',
        '-e', 'POSTGRES_HOST_AUTH_METHOD=trust', '-e', 'POSTGRES_USER=prototipo_restore',
        '-e', 'POSTGRES_DB=prototipo_restore', $postgresImage
    )
    if ($testContainerId -notmatch '^[0-9a-f]{64}$') { throw 'Identificador temporal inválido.' }
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        & docker exec $testContainerId pg_isready -q -U prototipo_restore -d prototipo_restore
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Seconds 1
    }
    if (-not $ready) { throw 'PostgreSQL temporal no inició a tiempo.' }
    Invoke-DockerChecked -DockerArguments @('cp', (Join-Path $backupPath 'database.dump'), "${testContainerId}:/tmp/database.dump") | Out-Null
    Invoke-DockerChecked -DockerArguments @(
        'exec', $testContainerId, 'pg_restore', '--exit-on-error', '--no-owner', '--no-acl',
        '-U', 'prototipo_restore', '-d', 'prototipo_restore', '/tmp/database.dump'
    ) | Out-Null
    $sql = @'
SELECT json_build_object(
 'migration', (SELECT version_num FROM alembic_version),
 'pgvector_version', (SELECT extversion FROM pg_extension WHERE extname='vector'),
 'table_count', (SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'),
 'documents', (SELECT count(*) FROM documentos),
 'chunks', (SELECT count(*) FROM fragmentos_documento),
 'generations', (SELECT count(*) FROM generaciones_contenido),
 'profiles', (SELECT count(*) FROM perfiles_rendimiento),
 'users', (SELECT count(*) FROM usuarios));
'@
    $databaseCheck = (Invoke-DockerChecked -DockerArguments @(
        'exec', $testContainerId, 'psql', '-X', '-v', 'ON_ERROR_STOP=1',
        '-U', 'prototipo_restore', '-d', 'prototipo_restore', '-Atc', $sql
    )) | ConvertFrom-Json
    if (-not $databaseCheck.migration -or -not $databaseCheck.pgvector_version) { throw 'Restauración sin migración o motor vectorial.' }

    $documentCode = @'
import hashlib, json, tarfile
from pathlib import Path
root = Path('/backup')
manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8-sig'))
expected = manifest['documents']
entries = []
with tarfile.open(root / 'documents.tar.gz', 'r:gz') as archive:
    for member in archive.getmembers():
        if member.isdir():
            continue
        if not member.isfile() or not member.name.startswith('documents/'):
            raise RuntimeError('Entrada no admitida en documentos.')
        name = member.name[len('documents/'):]
        if not name or '..' in Path(name).parts or Path(name).is_absolute():
            raise RuntimeError('Ruta no admitida.')
        data = archive.extractfile(member).read()
        entries.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
if sorted(entries, key=lambda x:x['path']) != sorted(expected, key=lambda x:x['path']):
    raise RuntimeError('Contenido de documentos no coincide con el manifiesto.')
print(json.dumps({'file_count':len(entries),'all_file_hashes_match':True}))
'@
    $documentCheck = (Invoke-DockerChecked -DockerArguments @(
        'run', '--rm', '--pull', 'never', '--network', 'none',
        '--mount', "type=bind,source=$backupPath,target=/backup,readonly",
        '--entrypoint', 'python', $backendImage, '-c', $documentCode
    )) | ConvertFrom-Json
    $report = [ordered]@{
        verification_version = 'prototipo-local-restore-v1'
        verified_at_utc = [DateTime]::UtcNow.ToString('o')
        status = 'passed'
        database_restore = $databaseCheck
        document_archive = $documentCheck
        live_database_modified = $false
        project_volumes_mounted = $false
        limitations = @('DB restaurada en almacenamiento temporal de 512 MiB; no prueba escala de producción.', 'Documentos leídos y cotejados byte a byte sin escribir en el volumen activo.', 'No incluye secretos ni pesos del modelo.')
    }
    $reportPath = Join-Path $backupPath ("restore-verification-" + [Guid]::NewGuid().ToString('N') + '.json')
    [System.IO.File]::WriteAllText($reportPath, (($report | ConvertTo-Json -Depth 8) + "`n"), [System.Text.UTF8Encoding]::new($false))
    Write-Host 'Restauración temporal de DB y hashes de documentos verificados.'
    Write-Host "Informe local: $reportPath"
}
finally {
    if ($testContainerId -and $testContainerId -match '^[0-9a-f]{64}$') {
        & docker rm -f $testContainerId | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-Warning 'El contenedor temporal sigue pendiente de retirar.' }
    }
    Pop-Location
}
