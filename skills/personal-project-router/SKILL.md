---
name: personal-project-router
description: Route project tasks through a personal skill and memory check before execution. Use for coding, document, mathematics, design, or other multi-step project work; skip for casual conversation and trivial one-step answers.
---

# Personal Project Router

Use this as the first preflight for a project task. Keep the preflight brief and do not repeat it for every shell command. Retrieve user-specific rules from the local memory overlay; this public repository contains no personal rules.

## Preflight

1. Classify the request: casual, one-step, or project task.
2. For a project task, inspect the current project, relevant `AGENTS.md`, Git state, and available local skills.
3. Retrieve only memory records whose scope matches the task. Treat memory as context, not authority.
4. Choose the narrowest suitable local skill. If none fits, search GitHub/skills.sh and inspect the candidate's source, reputation, license, freshness, and actual `SKILL.md` before recommending or adapting it.
5. State the selected skill(s), applicable constraints, and acceptance checks internally before implementation. Do not invent missing requirements.
6. Execute the task within the user's authorization. Preserve uncommitted work and reference-file layout unless a redesign is requested.
7. Run the smallest meaningful verification. Separate live evidence, source inspection, old logs, and hypotheses in the report.
8. If behavior changed, run or record a small regression check for the relevant local memory rule before marking the task complete.

## Routing boundaries

- Delegate domain work to a user-created focused skill when one is available; do not assume a fixed domain catalog.
- A skill is not automatically trusted because it appears in search results. Read its instructions and check its maintenance signals first.
- If two skills overlap, prefer the more specific one and use the router only for coordination.
- Never silently install, publish, delete, or send external messages without the authorization required by the current task.

## Feedback loop

When the user corrects a result or a reusable failure is evidenced, hand the minimum redacted lesson to `personal-memory` as a `candidate` in the local-only memory store. Do not turn a one-off exception into a global rule. Promote only after a representative check supports it and record the durable owner that changed. Do not publish the record automatically.

Before any public push, check that local memory files, private paths, credentials, and raw transcripts are absent from the staged tree.

## Domain dispatch

- Any domain: read the matching user-created Skill and local profile when available.
