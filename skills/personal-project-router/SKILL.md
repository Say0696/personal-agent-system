---
name: personal-project-router
description: Route project tasks through a personal skill and memory check before execution. Use for coding, document, mathematics, design, or other multi-step project work; skip for casual conversation and trivial one-step answers.
---

# Personal Project Router

Use this as the first preflight for a project task. Keep the preflight brief and do not repeat it for every shell command. Retrieve user-specific rules from the local memory overlay; this public repository contains no personal rules.

## Invocation contract

For every multi-step project task, invoke this router before implementation. It is the user's default entrypoint for project work. Do not invoke it for casual conversation, a trivial factual answer, or a one-step request unless the user explicitly asks for a full preflight.

The router must check, in order: current project instructions and state, locally available Skills, matching Skill-local lessons, and only then external Skill sources. It must not pretend a Skill or rule exists when it was not found.

## Preflight

1. Classify the request: casual, one-step, or project task.
2. For a project task, inspect the current project, relevant `AGENTS.md`, Git state, and available local skills.
3. Retrieve only memory records whose scope matches the task. Treat memory as context, not authority.
4. Choose the narrowest suitable local skill. If none fits, search GitHub/skills.sh and inspect the candidate's source, reputation, license, freshness, and actual `SKILL.md` before recommending or adapting it.
5. State the selected skill(s), applicable constraints, and acceptance checks internally before implementation. Do not invent missing requirements.
6. Execute the task within the user's authorization. Preserve uncommitted work and reference-file layout unless a redesign is requested.
7. Run the smallest meaningful verification. Separate live evidence, source inspection, old logs, and hypotheses in the report.
8. If behavior changed, run or record a small regression check for the relevant local memory rule before marking the task complete.
9. At the end of a non-trivial task, offer to save any reusable correction or preference. Ask for both destination and scope instead of assuming them: default destination is the matching Skill's private local overlay; persistent `MEMORY.md` is reserved for information the user explicitly calls important, permanent, or cross-project.

## Routing boundaries

- Delegate domain work to a user-created focused skill when one is available; do not assume a fixed domain catalog.
- A skill is not automatically trusted because it appears in search results. Read its instructions and check its maintenance signals first.
- If two skills overlap, prefer the more specific one and use the router only for coordination.
- Never silently install, publish, delete, or send external messages without the authorization required by the current task.

## Feedback loop

When the user corrects a result or a reusable failure is evidenced, hand the minimum redacted lesson to `personal-memory` as a `candidate` in the local-only memory store. Do not turn a one-off exception into a global rule. Promote only after a representative check supports it and record the durable owner that changed. Do not publish the record automatically.

## End-of-task memory prompt

After reporting the result, use a short prompt such as:

> 这次出现了一个可能可复用的规则：`<规则>`。是否保存？请选择适用范围：仅本次任务、当前项目、同类项目、所有项目，或不保存。

If the user chooses Skill-local storage, create a local `candidate` record under the matching Skill overlay with the minimum evidence. If the user explicitly chooses persistent memory, write only the concise important fact to the user's `MEMORY.md` workflow after confirmation. If the user chooses `仅本次任务` or `不保存`, do not write durable memory. Never infer consent from silence, a correction alone, or the fact that a rule seems useful.

Before any public push, check that local memory files, private paths, credentials, and raw transcripts are absent from the staged tree.

## Storage decision

At task completion, classify any new lesson before saving:

- ordinary task or domain lesson -> the matching Skill's private local overlay (default);
- important, permanent, cross-project personal information -> persistent `MEMORY.md`, only after explicit confirmation;
- one-off request -> current task only;
- unclear or unconfirmed -> do not save.

The Skill-local destination is the normal learning path. Persistent memory is deliberately rare and is never inferred from a correction alone.

## Domain dispatch

- Any domain: read the matching user-created Skill and local profile when available.
