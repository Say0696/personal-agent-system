[CmdletBinding(SupportsShouldProcess)]
param([string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }))
$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $CodexHome 'personal-agent-system\install-manifest.json'
if (-not (Test-Path $manifestPath)) { Write-Host 'No installation manifest found.'; exit 0 }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
foreach ($name in $manifest.installed) {
  $dst = Join-Path $CodexHome "skills\$name"
  if ($PSCmdlet.ShouldProcess($dst, 'Remove installed skill')) { Remove-Item -LiteralPath $dst -Recurse -Force -ErrorAction SilentlyContinue }
}
Write-Host 'Installed skills removed. Local memory was preserved.'
