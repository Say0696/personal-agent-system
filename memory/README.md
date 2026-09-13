# Local memory CLI

The manager operates on a user-local `rules.yaml` (default: `%CODEX_HOME%/personal-agent-system/memory/rules.yaml`, or `%USERPROFILE%/.codex/...`). It never uploads that file. Every mutation atomically replaces the file and creates a timestamped copy under `memory/backups/` beside it.

```powershell
python scripts/memory_cli.py add --scope math --rule "..." --evidence "..." --owner math-profile
python scripts/memory_cli.py search "keyword" --scope math
python scripts/memory_cli.py validate                 # schema check
python scripts/memory_cli.py validate RULE_ID --note "representative check"
python scripts/memory_cli.py apply RULE_ID --owner skill-name --change-ref "commit or file"
python scripts/memory_cli.py rollback RULE_ID --reason "new evidence"
python scripts/memory_cli.py list --status applied
```

Rules are deduplicated by normalized scope and exact rule text. Status transitions are guarded; use `--force` only for repairing imported data. Required fields and duplicate IDs/rules are checked before reading or writing.

Run the dependency-free tests with:

```powershell
python tests/test_memory_cli.py
```
