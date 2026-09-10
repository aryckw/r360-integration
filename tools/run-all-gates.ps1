# Run all four R360 gates in dependency order.
#
# The integration gate proves the composition; it deliberately does not run the other
# three, because a gate that ran its dependencies could report green for a repository
# whose own gate was never invoked. This script is the honest way to get the whole
# answer, and it stops at the first failure rather than continuing to a misleading
# summary.
#
#   .\tools\run-all-gates.ps1

$ErrorActionPreference = "Stop"

try { docker version --format '{{.Server.Version}}' | Out-Null }
catch { Write-Error "Docker is not running. Start Docker Desktop."; exit 1 }

$workspace = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$gates = @(
    @{ Name = "r360-contracts";   Command = { docker compose run --rm gate } },
    @{ Name = "r360-rf-evidence"; Command = { docker compose run --rm gate } },
    @{ Name = "r360-reasoning";   Command = { docker compose run --rm gate } },
    @{ Name = "r360-integration"; Command = { docker compose -f compose/docker-compose.yml run --rm gate } }
)

foreach ($gate in $gates) {
    $path = Join-Path $workspace $gate.Name
    if (-not (Test-Path $path)) {
        Write-Error "$($gate.Name) is not checked out at $path"
        exit 1
    }
    Write-Host ""
    Write-Host "=== $($gate.Name) ===" -ForegroundColor Cyan
    Push-Location $path
    try {
        & $gate.Command
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "$($gate.Name) GATE FAILED" -ForegroundColor Red
            exit $LASTEXITCODE
        }
    }
    finally { Pop-Location }
}

Write-Host ""
Write-Host "ALL FOUR GATES PASSED" -ForegroundColor Green
