$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    python -m venv (Join-Path $root '.venv')
}
& $venvPython (Join-Path $root 'evolutionctl.py') doctor
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'No third-party Python dependencies are required; runtime is isolated in .venv.'
