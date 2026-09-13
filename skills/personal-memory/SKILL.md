---
name: personal-memory
description: Maintain scoped, evidence-backed personal rules for recurring work. Use after a user correction, reusable failure, validated success, or explicit memory review.
---

# Personal Memory

Store small, reusable records rather than transcripts. There are two destinations:

1. **Skill-local overlay (default):** ordinary task or domain lessons, kept under a user-local overlay for the matching Skill. These rules help that Skill and are not automatically global.
2. **Persistent memory:** important, permanent, cross-project facts explicitly approved by the user for `MEMORY.md`. Keep this destination rare and concise.

Keep both destinations outside the public repository. Each structured record must include:

- `scope`: domain or project boundary;
- `rule`: future behavior in one sentence;
- `evidence`: correction, source, focused test, or repeated episode;
- `status`: `candidate`, `validated`, `applied`, `rejected`, `superseded`, or `rolled_back`;
- `examples`: one or two concrete cases when they prevent ambiguity;
- `owner`: the skill, instruction file, script, or project rule that owns it;
- `last_verified`: date of the latest check.

## Precedence

Resolve conflicts in this order: current user request, system/developer instructions, project instructions, validated local memory, then generic skills and external references. A memory record can guide a task only when its scope matches; it cannot override a newer explicit request.

## Lifecycle

1. Capture a minimal redacted candidate.
2. Check whether it applies beyond the original task and conflicts with any current rule.
3. Define a representative task that could disprove it.
4. Validate with that task or focused check.
5. Apply to exactly one durable owner and record the change reference.
6. Re-run the representative task. Roll back or supersede the rule when evidence changes.

## Consent and scope

Saving a new personal rule requires an explicit user choice at the end of the task. Offer the destination first: matching Skill-local overlay (recommended) or persistent `MEMORY.md` (only for important permanent cross-project information). Then offer scope: current task, current project, similar projects, or all projects. Silence means do not save. Store the narrowest scope the user selects; a later request can widen it. A correction is evidence for a candidate, not automatic permission to create durable memory.

Do not store secrets, raw transcripts, private payloads, or unverified guesses. Keep project facts scoped to the project. When evidence is insufficient, use `open-question` rather than pretending to remember. Never commit or upload the user's local memory file; public releases contain only the empty schema and generic lifecycle.

For repeatable Skill-local operations, use `scripts/memory_cli.py` with a user-local `--file` path. The public repository ships the manager and schema, not personal records. Do not use the CLI to write persistent `MEMORY.md` unless the user explicitly requested that destination and the format has been checked first.
