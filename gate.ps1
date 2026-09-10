# r360-reasoning gate wrapper. The gate runs in a container; the host has no make,
# no protoc and no C++ toolchain. Agent and CI issue the identical command.
#
#   .\gate.ps1            run the full gate
#   .\gate.ps1 shell      interactive shell in the same image
#   .\gate.ps1 <target>   run one make target in the gate image

param([string]$Target = "gate")

$ErrorActionPreference = "Stop"

try { docker version --format '{{.Server.Version}}' | Out-Null }
catch { Write-Error "Docker is not running. Start Docker Desktop."; exit 1 }

switch ($Target) {
    "gate"  { docker compose -f compose/docker-compose.yml run --rm gate }
    "shell" { docker compose -f compose/docker-compose.yml run --rm shell }
    "build" { docker compose -f compose/docker-compose.yml build }
    default { docker compose -f compose/docker-compose.yml run --rm gate make $Target }
}
exit $LASTEXITCODE
