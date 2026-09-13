[CmdletBinding()]
param(
  [string]$SourceRoot = '',
  [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
  [switch]$Force
)
$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $SourceRoot) { $SourceRoot = Split-Path -Parent $scriptRoot }
$skillsTarget = Join-Path $CodexHome 'skills'
$localRoot = Join-Path $CodexHome 'personal-agent-system'
New-Item -ItemType Directory -Force -Path $skillsTarget, (Join-Path $localRoot 'memory'), (Join-Path $localRoot 'scripts') | Out-Null
$requirements = Join-Path $SourceRoot 'requirements.txt'
if (Test-Path $requirements) { Write-Host "Python dependency declaration: $requirements (install with 'python -m pip install -r requirements.txt')" }
$installed = @()
Get-ChildItem (Join-Path $SourceRoot 'skills') -Directory | ForEach-Object {
  $src = $_.FullName; $dst = Join-Path $skillsTarget $_.Name
  if ((Test-Path $dst) -and -not $Force) { Write-Host "skip existing: $($_.Name)"; return }
  if (Test-Path $dst) { Remove-Item -LiteralPath $dst -Recurse -Force }
  Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
  $installed += $_.Name
}
Copy-Item (Join-Path $SourceRoot 'scripts\route.py') (Join-Path $localRoot 'scripts\route.py') -Force
if (-not (Test-Path (Join-Path $localRoot 'memory\rules.yaml'))) {
  Copy-Item (Join-Path $SourceRoot 'memory\rules.example.yaml') (Join-Path $localRoot 'memory\rules.yaml')
}
@{ source = (Resolve-Path $SourceRoot).Path; installed = $installed; installed_at = (Get-Date).ToUniversalTime().ToString('o') } |
  ConvertTo-Json | Set-Content (Join-Path $localRoot 'install-manifest.json') -Encoding UTF8
Write-Host "Installed $($installed.Count) skills into $skillsTarget"
Write-Host "Personal memory: $(Join-Path $localRoot 'memory\rules.yaml')"
