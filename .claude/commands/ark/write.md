---
description: Write a note to memory with gate evaluation
args: note - The note to write. Use --quick to bypass the write gate.
allowed-tools: Read, Write, Edit, Grep
---

# /ark:write

Write a note to memory, applying the write gate. Default destination: daily log.

The user's note: $ARGUMENTS

## Quick Mode

If arguments contain `--quick`: skip the write gate, append directly to today's daily log under Notes. Confirm and return.

## Write Gate Protocol

Before writing, evaluate:

1. **Does it change future behavior?** (preference, boundary, recurring pattern) -> WRITE
2. **Is it a commitment with consequences?** (deadline, deliverable, follow-up) -> WRITE
3. **Is it a decision with rationale?** (why X over Y, worth preserving) -> WRITE
4. **Is it a stable fact that will matter again?** (not transient, not obvious) -> WRITE
5. **Did the user explicitly say "remember this"?** -> ALWAYS WRITE

If NONE are true, tell the user why it didn't pass the gate. Suggest `--quick` for raw capture.

## Write to Daily Log

ALL writes go to `memory/daily/YYYY-MM-DD.md` first. Create the file if it doesn't exist:

```markdown
# YYYY-MM-DD

## Decisions

## Corrections

## Commitments

## Open Loops

## Notes
```

Append a timestamped entry under the appropriate section:
```
[HH:MM] note text here
```

## Suggest Promotion

After writing, if the note seems durable, **suggest** where it could be promoted:

```
Written to memory/daily/2026-02-05.md:
  [14:32] User prefers bullet points over prose for summaries

This looks like a lasting preference. Want me to also promote it to:
  -> memory/registers/preferences.md
  -> CLAUDE.local.md (if it should affect every session)
```

The user decides. If yes, write to the register with metadata:
```markdown
- **claim**: [the fact/preference/decision]
- **confidence**: high | medium | low
- **evidence**: [how we know]
- **last_verified**: [today's date]
```

## Direct Promotion Exceptions

These skip the "suggest" step and promote directly (but still write to daily log):

1. **Explicit corrections** -- update register immediately, mark old as `[superseded: date]`
2. **Explicit "remember this"** -- write to appropriate register
3. **Deadline/commitment** -- always goes to `registers/open-loops.md` AND daily log

## Contradiction Check

Before writing, check existing memory for related claims:
1. Check CLAUDE.local.md
2. Check relevant register (if promoting)

If contradiction found, show user and ask to confirm update.

## ID Assignment on Promotion

When writing to CLAUDE.local.md or a register, assign a durable ID:

1. Generate: 8 random lowercase hex characters
2. Append ` ^[id]` to end of single-line list items
3. Check for collisions against existing IDs in the destination file

## Confirm

```
Noted in memory/daily/[date].md: [one-line summary]
```
