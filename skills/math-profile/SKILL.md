---
name: math-profile
description: Generate or edit mathematics exercises and math documents with correct notation and explicit answer checks. Use for worksheets, exam practice, solutions, or mathematical formatting.
---

# Mathematics Profile

Use this as a neutral mathematics extension point. Read the user's local mathematics profile before generating an artifact, and follow its scoped conventions when present.

- Preserve requested topic, difficulty, number range, question count, notation, and answer format. If a missing choice materially changes the result, ask or state the assumption.
- Check every generated answer independently. Verify signs, denominators, units, simplification, and boundary cases when applicable.
- Match a supplied reference's structure and typography before adding visual changes.
- Report whether notation was source-checked, structurally checked, or visually rendered.

Do not place a user's personal notation preferences in this public skill. Store them in the local memory overlay.
