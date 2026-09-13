[CmdletBinding(SupportsShouldProcess)]
param([string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }), [string]$BackupStamp = '')
$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $CodexHome 'personal-agent-system\install-manifest.json'
if (-not (Test-Path $manifestPath)) { throw 'No installation manifest found.' }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
foreach ($name in $manifest.installed) {
  $dst = Join-Path $CodexHome "skills\$name"
  $pattern = if ($BackupStamp) { "$dst.backup-$BackupStamp" } else { "$dst.backup-*" }
  $backup = Get-ChildItem $pattern -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
  if (-not $backup) { Write-Host "no backup found: $name"; continue }
  if ($PSCmdlet.ShouldProcess($dst, "Restore $($backup.FullName)")) { if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }; Move-Item $backup.FullName $dst; Write-Host "restored: $name" }
}
