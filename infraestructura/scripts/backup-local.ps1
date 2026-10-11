# Copia consistente: detener frontend/backend antes de ejecutar; PostgreSQL sigue activo.
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path

function Invoke-DockerChecked {
    param([string[]]$DockerArguments)
    & docker @DockerArguments
    if ($LASTEXITCODE -ne 0) { throw 'Falló Docker durante el respaldo. La copia no está completa.' }
}

Push-Location $projectRoot
try {
    foreach ($service in @('frontend', 'backend', 'prepare-embeddings', 'migrate')) {
        $running = & docker compose ps --status running -q $service
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo comprobar el estado de los servicios.' }
        if ($running) { throw "Detén el servicio $service antes de respaldar. No se creó ninguna copia." }
    }
    $postgresId = & docker compose ps --status running -q postgres
    if ($LASTEXITCODE -ne 0 -or -not $postgresId) { throw 'PostgreSQL debe estar iniciado.' }
    $backendId = & docker compose ps --all -q backend
    if ($LASTEXITCODE -ne 0 -or -not $backendId) { throw 'Debe existir el contenedor backend con sus volúmenes.' }
    $backendImage = & docker inspect --format '{{.Image}}' $backendId
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo identificar la imagen del backend.' }

    $identifier = [Guid]::NewGuid().ToString('N')
    $backupDirectory = Join-Path $projectRoot "respaldos_locales/$identifier"
    New-Item -ItemType Directory -Path $backupDirectory | Out-Null
    $containerDump = "/tmp/tutoria-$identifier.dump"
    try {
        # El archivo binario no pasa por redirección de PowerShell.
        Invoke-DockerChecked -DockerArguments @(
            'compose', 'exec', '-T', 'postgres', 'sh', '-c',
            'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl --file="$1"',
            'backup', $containerDump
        )
        Invoke-DockerChecked -DockerArguments @('cp', "${postgresId}:$containerDump", (Join-Path $backupDirectory 'database.dump'))
    }
    finally {
        # Ruta temporal literal, creada exclusivamente por esta ejecución.
        & docker compose exec -T postgres rm -f -- $containerDump
        if ($LASTEXITCODE -ne 0) { Write-Warning 'No se pudo retirar el dump temporal del contenedor.' }
    }

    $archiveCode = @'
import hashlib, json, tarfile
from datetime import datetime, timezone
from pathlib import Path
root = Path('/app/uploads/documents')
target = Path('/backup')
files = []
for path in sorted(root.rglob('*')):
    if path.is_symlink():
        raise RuntimeError('No se respaldan enlaces simbólicos.')
    if path.is_file():
        files.append({'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
with tarfile.open(target / 'documents.tar.gz', 'x:gz') as archive:
    archive.add(root, arcname='documents', recursive=True)
names = ('database.dump', 'documents.tar.gz')
manifest = {
    'format_version': 'tutoria-local-backup-v1',
    'created_at_utc': datetime.now(timezone.utc).isoformat(),
    'consistency': 'application_and_migration_services_stopped',
    'archives': [{'path': name, 'bytes': (target / name).stat().st_size,
                  'sha256': hashlib.sha256((target / name).read_bytes()).hexdigest()} for name in names],
    'documents': files,
    'excluded': ['environment_secrets', 'embedding_model_weights', 'source_code', 'docker_images'],
    'restore_test_status': 'not_tested'
}
with (target / 'manifest.json').open('x', encoding='utf-8', newline='\n') as output:
    json.dump(manifest, output, ensure_ascii=False, indent=2)
    output.write('\n')
'@
    Invoke-DockerChecked -DockerArguments @(
        'run', '--rm', '--network', 'none', '--volumes-from', "${backendId}:ro",
        '--mount', "type=bind,source=$backupDirectory,target=/backup",
        '--entrypoint', 'python', $backendImage, '-c', $archiveCode
    )
    $manifest = Get-Content -LiteralPath (Join-Path $backupDirectory 'manifest.json') -Raw | ConvertFrom-Json
    foreach ($entry in $manifest.archives) {
        $archivePath = Join-Path $backupDirectory $entry.path
        $actualHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -ne $entry.sha256) { throw 'La huella del respaldo no coincide.' }
    }
    Write-Host "Respaldo completo con hashes verificados: $backupDirectory"
    Write-Host 'Incluye DB y documentos. La restauración debe comprobarse por separado.'
}
finally {
    Pop-Location
}
