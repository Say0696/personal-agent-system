# Memory records

This directory contains the public schema only. User-specific records belong in a local-only `rules.yaml`, which is ignored by Git. The router should retrieve records matching the current task scope; records are not a transcript and are not a substitute for current project inspection.

Start from `rules.example.yaml`. Keep the personal file under the local Codex home (for example `%USERPROFILE%\\.codex\\personal-agent-system\\memory\\rules.yaml`) or another ignored local directory. Never upload that file to the public repository.

Use the lifecycle from `skills/personal-memory/SKILL.md`: capture as `candidate`, validate with a representative check, apply to one durable owner, and supersede or roll back when evidence changes.
