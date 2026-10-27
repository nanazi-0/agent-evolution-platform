$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run scripts/setup.ps1 first.' }
Push-Location $root
try {
    & $python evolutionctl.py run --config configs/demo.toml
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $python evolutionctl.py audit-verify
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally { Pop-Location }

