---
name: personal-memory
description: Maintain scoped, evidence-backed personal rules for recurring work. Use after a user correction, reusable failure, validated success, or explicit memory review.
---

# Personal Memory

Store small, reusable records rather than transcripts. Keep them in a user-local file outside the public repository. Each record must include:

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

Do not store secrets, raw transcripts, private payloads, or unverified guesses. Keep project facts scoped to the project. When evidence is insufficient, use `open-question` rather than pretending to remember. Never commit or upload the user's local memory file; public releases contain only the empty schema and generic lifecycle.
