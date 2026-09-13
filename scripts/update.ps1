[CmdletBinding()]
param(
  [string]$SourceRoot = '',
  [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' })
)
$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $SourceRoot) { $SourceRoot = Split-Path -Parent $scriptRoot }
$manifestPath = Join-Path $CodexHome 'personal-agent-system\install-manifest.json'
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss')
if (Test-Path $manifestPath) {
  $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
  foreach ($name in $manifest.installed) {
    $dst = Join-Path $CodexHome "skills\$name"
    if (Test-Path $dst) { Copy-Item $dst "$dst.backup-$stamp" -Recurse -Force }
  }
}
& (Join-Path $scriptRoot 'install.ps1') -SourceRoot $SourceRoot -CodexHome $CodexHome -Force
Write-Host "Update complete; prior skill folders (when present) were backed up with suffix $stamp."
