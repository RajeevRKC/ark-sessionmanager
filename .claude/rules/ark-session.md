# Ark Session -- Memory Protocol

> Auto-loads every session. Governs persistent memory. Follow exactly.

## Memory Active

This project uses Ark Session for persistent memory. Memory lives on disk.

### Auto-Loaded

- This file (`.claude/rules/ark-session.md`) -- protocol rules
- `CLAUDE.local.md` -- working memory (~1500 words)

### Check On Session Start

1. `memory/registers/open-loops.md` -- active follow-ups
2. `memory/daily/[today].md` -- today's log
3. `memory/daily/[yesterday].md` -- yesterday's log
4. `memory/registers/_index.md` -- what registers exist

### Dynamic Loading

- Person mentioned -> `memory/registers/people.md`
- Project discussed -> `memory/registers/projects.md`
- Past decision -> `memory/registers/decisions.md`
- "Remember when" -> search `memory/daily/`

Do NOT load everything. Pull only what's relevant.

## Write Gate (MANDATORY)

Before writing to memory:

1. Changes future behavior? -> WRITE
2. Commitment with consequences? -> WRITE
3. Decision with rationale? -> WRITE
4. Stable fact that will matter again? -> WRITE
5. User said "remember this"? -> ALWAYS WRITE

None true -> DO NOT WRITE.

Default destination: `memory/daily/YYYY-MM-DD.md`. Promotion is separate.

## Corrections (HIGHEST PRIORITY)

1. Write to daily log immediately
2. Update relevant register (mark old as `[superseded: date]`)
3. Update CLAUDE.local.md if it changes default behavior
4. Search everywhere for old claim, update all instances

## Contradictions

Never silently overwrite. Mark old as `[superseded: date]` with reason.
Write new entry referencing what it replaces. Ask user if confidence is low.

## Pre-Compaction / Session End

Before session ends or context gets long:
- Sweep for unsaved decisions, corrections, commitments, open loops
- Write to daily log with `[session-flush]` tag
- Update CLAUDE.local.md "Session Continuity" section

## Commands

| Command | Purpose |
|---------|---------|
| `/ark:init` | Scaffold memory system |
| `/ark:write <note>` | Write with gate (--quick bypasses) |
| `/ark:search <query>` | Search all tiers |
| `/ark:maintain` | Status + promote + prune + health |
| `/ark:forget <query>` | Mark entries superseded |
| `/session:intent <text>` | Set session purpose |
| `/session:active` | Show active sessions |
| `/session:close` | Close session + memory sweep |

## Key Rules

- Search memory FIRST before answering history/preference questions
- Apply write gate BEFORE writing
- Default write destination: DAILY LOG
- On corrections: UPDATE ALL INSTANCES
- Keep CLAUDE.local.md under 1500 words
- Daily logs are append-only
