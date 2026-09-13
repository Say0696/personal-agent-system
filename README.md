# Personal Agent System

A personal, evolving skill system for Codex: route each project task through a local-first skill check, retrieve domain-specific memory, preserve reference formatting, and turn verified corrections into reusable rules.

## Structure

- `skills/personal-project-router` — task preflight, skill discovery, routing, evidence, and feedback capture.
- `skills/personal-memory` — scoped memory records with candidate/validated/applied states.
- `skills/math-profile` — mathematics-specific output and verification rules.
- `skills/document-fidelity` — reference-preserving document workflow.
- `skills/computer-development` — software and computer-project workflow.
- `references/skill-registry.yaml` — installed and recommended skill inventory.
- `memory/rules.example.yaml` — empty schema for user-specific local rules. Personal records are deliberately excluded from this repository.
- `scripts/memory_cli.py` — local-only memory capture, listing, and status changes.
- `scripts/privacy_check.py` — staged-tree check before a public push.
- `scripts/route.py` — read-only task classification and local skill/memory routing.
- `scripts/install.ps1`, `scripts/update.ps1`, `scripts/uninstall.ps1` — Windows lifecycle helpers.
- `scripts/route.py` — read-only project preflight and domain skill router.
- `scripts/install.ps1` / `update.ps1` / `uninstall.ps1` — install, backup-and-update, and remove skills.

## Install and route

From PowerShell in the repository:

```powershell
.\scripts\install.ps1
python .\scripts\route.py "Create a mathematics worksheet"
python .\scripts\route.py --json "Fix the code and run tests"
```

The installer copies generic skills and creates a blank local memory file at `$CODEX_HOME/personal-agent-system/memory/rules.yaml` without overwriting an existing one. The router is read-only: it never installs skills, changes memory, or publishes content. `update.ps1` backs up installed skills before updating; `uninstall.ps1` removes only skills recorded in its manifest and preserves personal memory.

## Installation

Copy the skill directories you want into your Codex skills directory, normally `%USERPROFILE%\\.codex\\skills`. Add the repository's generic `AGENTS.md` to the project where you use it. Keep your personal global protocol and memory overlay outside this public repository.

Install Python dependencies for the local scripts with `python -m pip install -r requirements.txt`. Install `requirements-dev.txt` when running the test suite.

The router remains implicitly discoverable when the host supports implicit selection. It does not replace the host's skill selection or override system, developer, user, or project instructions.

## Growth model

New lessons start as `candidate`. A lesson becomes `validated` only after a representative task or focused check supports it. It becomes `applied` only after one named durable owner changes. Each record keeps scope, evidence, examples, verification time, and rollback information.

## Design principles

- Search local skills first; search GitHub/skills.sh only when the local catalog has no suitable match.
- Inspect a candidate skill's source, reputation, license, freshness, and actual instructions before recommending it.
- Do not invent missing requirements. Ask or mark uncertainty when evidence is insufficient.
- Treat a reference file's layout as a constraint; inspect before editing and preserve it unless the user requests redesign.
- Use true mathematical notation in generated artifacts, such as `\\frac{a}{b}` for a stacked fraction.
- Report evidence separately from hypotheses and old logs.

## Status

Version 0.2.0. This repository is intentionally a blank starter. A user grows a private local overlay from demonstrated corrections; personal requirements are not published here.

See [PUBLISHING.md](PUBLISHING.md) for the release workflow and source patterns used.
