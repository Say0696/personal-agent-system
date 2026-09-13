# Local memory CLI

The manager operates on a user-local Skill overlay `rules.yaml` (default: `%CODEX_HOME%/personal-agent-system/memory/rules.yaml`, or `%USERPROFILE%/.codex/...`). The record's `owner` identifies the Skill that owns the lesson. It never uploads that file. Ordinary task and domain lessons belong here by default. Important, permanent, cross-project facts belong in the user's persistent `MEMORY.md` only after explicit confirmation; this CLI does not write that file implicitly. Every mutation atomically replaces the local file and creates a timestamped copy under `memory/backups/` beside it.

```powershell
python scripts/memory_cli.py add --scope math --rule "..." --evidence "..." --owner math-profile
python scripts/memory_cli.py search "keyword" --scope math
python scripts/memory_cli.py validate                 # schema check
python scripts/memory_cli.py validate RULE_ID --note "representative check" --evidence-file check-output.txt
python scripts/memory_cli.py apply RULE_ID --owner skill-name --change-ref "commit or file"
python scripts/memory_cli.py rollback RULE_ID --reason "new evidence"
python scripts/memory_cli.py list --status applied
python scripts/memory_cli.py restore memory/backups/rules-YYYYmmdd-HHMMSS.yaml.bak
python scripts/memory_cli.py export --output redacted-by-you.yaml --confirm-private
```

Rules are deduplicated by normalized scope and exact rule text. `validate` without an ID only checks the schema; marking a record validated additionally requires a non-empty review note and either an existing evidence file (hashed with SHA-256) or a supplied digest. This records a human or agent review, not proof that a rule is universally correct. Status transitions are guarded; use `--force` only for repairing imported data. Required fields and duplicate IDs/rules are checked before reading or writing. Every mutation writes a timestamped backup. `export` is deliberately opt-in and does not redact private content; inspect it before sharing.

Run the dependency-free tests with:

```powershell
python tests/test_memory_cli.py
```
