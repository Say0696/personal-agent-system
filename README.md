# Personal Agent System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-6%20passed-brightgreen.svg)](tests)

A local-first, privacy-preserving starter system for personal Agent Skills. It routes project tasks, retrieves matching local memory, discovers user-added Skills, and turns confirmed corrections into scoped rules that improve future work.

The repository is intentionally domain-agnostic. It ships two generic core Skills; users add mathematics, coding, writing, video, research, or any other domain locally when needed.

> 中文说明：[README.zh-CN.md](README.zh-CN.md)

## What it does

- Runs a lightweight preflight for multi-step project tasks.
- Discovers Skills from the Codex home and current project instead of using a fixed domain catalog.
- Reads only validated or applied memory records whose scope matches the task.
- Keeps personal memory outside the public repository.
- Asks for explicit consent and scope before saving a reusable preference.
- Manages memory candidates, validation, application, rollback, backups, and search.
- Installs, updates, rolls back, and uninstalls the generic core Skills on Windows.
- Checks staged or tracked content for personal paths, local memory, environment files, and common tokens.

## Architecture

```text
User task -> personal-project-router -> local memory and Skill discovery
                                      -> optional user Skill
                                      -> execution and verification
                                      -> consent -> local candidate
                                      -> validation -> applied rule
```

The core does not assume a fixed domain. Any local directory containing a `SKILL.md` can be discovered dynamically.

## Quick start on Windows

From PowerShell in the repository:

```powershell
python -m pip install -r requirements.txt
.\scripts\install.ps1
python .\scripts\route.py --json "Create a project artifact"
```

The installer copies only the two generic core Skills and creates this local file when it does not already exist:

```text
%CODEX_HOME%\personal-agent-system\memory\rules.yaml
```

Existing local memory is preserved. Add a domain Skill locally when a task needs one.

## Runtime flow

1. A multi-step task starts the router when the host supports implicit Skill selection; `scripts/route.py` is the deterministic manual entry point.
2. The router inspects the current project, project instructions, Git state, and local Skill catalog.
3. It loads only matching `validated` and `applied` local records.
4. A suitable local Skill is selected. If none exists, the user can search GitHub or `skills.sh`, inspect its actual `SKILL.md`, and decide whether to install it.
5. The task runs within the user's authorization and receives the smallest meaningful verification.
6. The result separates live evidence, source inspection, old logs, and hypotheses.
7. If a reusable correction appeared, the router asks whether to save it for this task, project, similar projects, all projects, or nowhere.

Automatic Skill loading is host-dependent. The global `AGENTS.md` protocol asks Codex to perform this preflight for project tasks; the router never silently installs, publishes, or sends external messages.

## Local memory lifecycle

Personal records are never part of the public tree. Use the local CLI:

```powershell
python scripts/memory_cli.py add --scope writing --rule "Use the requested house style" --evidence "User-confirmed preference"
python scripts/memory_cli.py list --scope writing
python scripts/memory_cli.py search "house style"
python scripts/memory_cli.py validate <id> --note "Representative task passed" --evidence-file .\evidence.txt
python scripts/memory_cli.py apply <id> --owner writing-skill --change-ref "skill:writing-skill@abc123"
python scripts/memory_cli.py rollback <id> --reason "Preference is no longer applicable"
```

Records move through guarded states:

```text
candidate -> validated -> applied
     |          |           |
  rejected   rejected   superseded / rolled_back
```

Validation requires a note and evidence file or SHA-256 digest. Writes are backed up and replaced atomically. `export` is explicit because exported memory may contain private preferences.

## Add a domain Skill locally

Create a local directory with a concise `SKILL.md`:

```text
%CODEX_HOME%\skills\my-domain-skill\SKILL.md
```

Use the Agent Skills format with a unique name and a description that says when it applies. Keep personal examples and preferences in local memory, not in a public Skill repository. The router discovers it on the next preflight.

## Update and recovery

```powershell
.\scripts\update.ps1
.\scripts\rollback.ps1
.\scripts\uninstall.ps1
```

Updates back up installed core Skill folders. Rollback restores the newest backup. Uninstall removes only Skills recorded in the install manifest and preserves local memory.

## Verification and development

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
.\scripts\check.ps1
```

The check script validates Skill structure, compiles Python scripts, runs tests, and scans tracked content for private data. Use `python scripts/privacy_check.py` for staged files or add `--all` for all tracked files.

## Privacy and design boundaries

- Public files contain generic workflows and an empty memory schema.
- Personal rules, private project facts, transcripts, credentials, and local overlays stay under the user's local Codex home.
- A correction becomes a candidate only after the user chooses to save it; silence never creates durable memory.
- Current user instructions override older memory. External Skill quality is inspected before adoption.

## FAQ

### Why is `personal-agent-system` not shown as a Skill?

`personal-agent-system` is the GitHub repository and package name. The callable Skill entrypoints inside it are `personal-project-router` and `personal-memory`. The Codex Skill list shows callable entrypoints, not repository names.

### Does the router always run automatically?

The global protocol asks Codex to run the router for project tasks. Actual implicit Skill loading depends on the host. Run `python scripts/route.py --json "<task>"` when you need a deterministic, read-only preflight.

### Where are my personal rules?

They are stored locally at `%CODEX_HOME%\\personal-agent-system\\memory\\rules.yaml`. The public repository contains only `memory/rules.example.yaml`; personal rules are ignored by Git and are never pushed automatically.

### Why are there no mathematics, coding, or document Skills in the core?

The core is domain-agnostic. Add a local Skill only when your work needs one. Any directory containing a `SKILL.md` can be discovered; the system does not require a fixed list of domains.

### Will the system become larger every time I use it?

Only confirmed, scoped rules should enter durable memory. The router loads matching `validated` and `applied` records instead of the entire memory store. One-off requests remain in the current task unless the user explicitly chooses a scope at the end.

### Does local learning update GitHub?

No. Local memory updates and public repository updates are separate. Publish only generic workflow improvements after reviewing them for privacy and portability.

## License

MIT. See [LICENSE](LICENSE).
