[CmdletBinding()]
param([switch]$SkipPytest)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$validator = Join-Path $HOME '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
if (Test-Path $validator) {
  Get-ChildItem (Join-Path $PSScriptRoot '..\skills') -Directory | ForEach-Object { python $validator $_.FullName }
}
$pyFiles = @((Join-Path $PSScriptRoot 'memory_cli.py'), (Join-Path $PSScriptRoot 'privacy_check.py'), (Join-Path $PSScriptRoot 'route.py'))
python -m py_compile $pyFiles
if (-not $SkipPytest) { python -m pytest -q }
python (Join-Path $PSScriptRoot 'privacy_check.py') --all
Write-Host 'Checks complete.'
