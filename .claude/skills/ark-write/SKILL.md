---
name: ark-write
description: Writes notes to memory with a 5-criteria write gate. Default destination is the daily log with optional promotion to registers.
version: 1.0.0
tags: [memory, write, daily-log, gate]
---

# ark-write

Writes a note to memory, applying the write gate before storing.

## When to Use

- User wants to save information to memory
- User says "remember this", "note that", "write to memory"
- Use `--quick` flag to bypass the write gate for raw capture

## What It Does

1. Evaluates the note against the 5-criteria write gate
2. Writes to `memory/daily/YYYY-MM-DD.md` as timestamped entry
3. Suggests promotion to registers if the note seems durable
4. Checks for contradictions with existing memory
5. Assigns IDs when promoting to registers or CLAUDE.local.md

## Write Gate (5 Criteria)

1. Changes future behavior?
2. Commitment with consequences?
3. Decision with rationale?
4. Stable fact that will matter again?
5. User said "remember this"?

## Key Behaviors

- Daily log is always the first destination
- Promotion is suggested, not automatic (user decides)
- Corrections and deadlines bypass the suggestion step
- Contradiction check runs before writing

## References

- [Protocol](../../rules/ark-session.md)
