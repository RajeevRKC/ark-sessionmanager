# Ark Session -- Memory Schema

> Teaches Claude how the memory system works.
> Read on session start for reference. Protocol auto-loads via `.claude/rules/ark-session.md`.

## How Memory Works

Persistent memory with four tiers. Data flows upward through compression (raw -> structured -> essential -> archived) and is retrieved downward on demand.

### Auto-Loaded (Deterministic)

| File | Mechanism | Purpose |
|------|-----------|---------|
| `.claude/rules/ark-session.md` | Auto-loaded via rules/ | Memory protocol and write gate |
| `CLAUDE.local.md` | Auto-loaded by Claude Code | Working memory (~1500 words) |

### Check On Session Start

| File | Purpose |
|------|---------|
| `memory/registers/open-loops.md` | Active follow-ups and deadlines |
| `memory/daily/[today].md` | Today's daily log |
| `memory/daily/[yesterday].md` | Yesterday's daily log |
| `memory/registers/_index.md` | What registers exist |

### Search On Demand

| Location | Search When |
|----------|-------------|
| `memory/registers/people.md` | A person is mentioned |
| `memory/registers/projects.md` | A project is discussed |
| `memory/registers/decisions.md` | Past choices are questioned |
| `memory/registers/preferences.md` | Style/approach matters |
| `memory/registers/tech-stack.md` | Technical choices come up |
| `memory/archive/` | Historical context needed |

Do NOT load everything. Pull only what's relevant.

## Tier Architecture

```
Conversation (ephemeral)
    |
    v WRITE GATE: "Does this change future behavior?"
    |
Daily Log (memory/daily/YYYY-MM-DD.md)
    Raw timestamped capture. All writes land here first.
    |
    v PROMOTION: "Will this matter in 30 days?"
    |
Registers (memory/registers/*.md)
    Structured domain knowledge with metadata.
    |
    v DISTILLATION: "Essential for every session?"
    |
Working Memory (CLAUDE.local.md)
    ~1500 words. Auto-loaded. Only behavior-changing facts.
    |
    v EXPIRY: "Completed or superseded?"
    |
Archive (memory/archive/)
    Searchable history. Never auto-loaded.
```

## The Write Gate

Before writing ANYTHING to memory:

1. **Does it change future behavior?** -> WRITE
2. **Is it a commitment with consequences?** -> WRITE
3. **Is it a decision with rationale?** -> WRITE
4. **Is it a stable fact that will matter again?** -> WRITE
5. **Did the user explicitly say "remember this"?** -> ALWAYS WRITE

None true -> DO NOT WRITE.

### Default: Daily Log

All writes go to `memory/daily/YYYY-MM-DD.md` first. Promotion is separate.

### Direct Promotion Exceptions

- **Corrections** -- update register immediately, mark old as superseded
- **Explicit "remember this"** -- write to appropriate register
- **Deadlines/commitments** -- always go to open-loops.md + daily log

## Routing Table

| Trigger | Primary Destination | Also Update |
|---------|-------------------|-------------|
| "Remember" | Daily log + register | CLAUDE.local.md if behavioral |
| Correction | Supersede old + write new | ALL locations with old claim |
| Decision with rationale | Daily log, suggest decisions.md | CLAUDE.local.md if current |
| Person context | Daily log, suggest people.md | CLAUDE.local.md if active |
| Preference | Daily log, suggest preferences.md | CLAUDE.local.md if default |
| Commitment/deadline | Daily log + open-loops.md | CLAUDE.local.md always |
| Technical choice | Daily log, suggest tech-stack.md | -- |

## Contradiction Protocol

1. NEVER silently overwrite
2. Mark old entry as `[superseded: YYYY-MM-DD]` with reason
3. Write new entry referencing what it replaces
4. If confidence is low, ask user to confirm

## Correction Gate

Human corrections are highest-priority writes:

1. Write immediately to daily log
2. Update relevant register with superseded marking
3. Update CLAUDE.local.md if it changes default behavior
4. Search everywhere for old claim, update all instances

## Register Entry Schema

For durable claims in registers:

```markdown
- **claim**: [the fact, preference, or decision]
- **confidence**: high | medium | low
- **evidence**: [source -- user said, observed, corrected]
- **last_verified**: YYYY-MM-DD
```

Not every line needs full metadata. Use for claims where being wrong matters.

## Entry IDs

Entries in managed files can have durable IDs for tracking and maintenance.

### Format

```
- Some fact about the project ^a1b2c3d4
```

- Format: `^` + 8 lowercase hex characters
- Regex: `\^[0-9a-f]{8}$`
- Also accepts legacy: `^tr[0-9a-f]{10}` (backward compatible)

### What Gets an ID

- Single-line list items in CLAUDE.local.md, registers, archive
- NOT daily log entries
- NOT multi-line metadata blocks
- NOT placeholder entries

## Pressure-Based Demotion

When working memory exceeds 1500 words, `/ark:maintain` surfaces candidates scored by word cost and staleness. Users choose: keep, pin, demote, archive, or mark superseded.

## Session-Memory Bridge

When a session ends, `sweep_session()` appends a `[session-end]` marker to today's daily log with callsign, duration, and intent. This captures session context in the memory system. Promotion remains user-controlled.

## CLAUDE.local.md Limits

- Hard cap: ~1500 words
- Review: every few days
- Rule: if not relevant in 2+ weeks, demote or archive
- Every line earns its place

## Commands

| Command | Purpose |
|---------|---------|
| `/ark:init` | Scaffold the memory system |
| `/ark:write <note>` | Write with gate (--quick bypasses) |
| `/ark:search <query>` | Search all tiers |
| `/ark:maintain` | Status + promote + prune + health |
| `/ark:forget <query>` | Mark entries superseded |
| `/session:intent <text>` | Set session purpose |
| `/session:active` | Show active sessions |
| `/session:close` | Close session + memory sweep |
