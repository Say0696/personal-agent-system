# Publishing

This repository follows patterns observed in public Agent Skills projects:

- Anthropic's public skills repository keeps each skill self-contained with a concise `SKILL.md` and optional resources.
- Vercel's agent-skills repository publishes a clear catalog, installation command, and usage triggers.
- Agent Playbook documents portable installation, explicit invocation, validation, and the boundary between declarative hooks and proven host behavior.

## First release from Windows

After authenticating GitHub CLI:

```powershell
gh auth login
gh repo create personal-agent-system --public --source . --remote origin --push
```

Before pushing, run the Skill validator with UTF-8 enabled on Windows:

```powershell
$env:PYTHONUTF8 = '1'
$validator = "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py"
Get-ChildItem .\skills -Directory | ForEach-Object { python $validator $_.FullName }
```

The public repository must not contain credentials, raw conversation logs, private project paths, personal memory records, or unredacted tool payloads. Record portable upstream source URLs and versions in `references/skill-registry.yaml` when external skills are adopted. Keep user-specific rules in an ignored local overlay.
