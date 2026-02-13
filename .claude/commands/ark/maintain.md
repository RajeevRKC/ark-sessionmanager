---
description: Combined memory status, promotion, pruning, and health check
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# /ark:maintain

One command for all memory maintenance: status, promotion, pressure-based demotion, stale entry review, and health check.

## What To Do

### 1. Status Overview

Report current memory health:

```
ark:maintain -- memory health
==================================

Working memory: [N] words (target: 1500)
Registers: [N] files, [N] total entries
Daily logs: [N] files (last 30 days)
Archive: [N] files

Recent context loaded:
  - CLAUDE.local.md (auto)
  - .claude/rules/ark-session.md (auto)
  - [list any registers loaded this session]
```

### 2. Promotion Review

Scan daily logs from the last 7 days for entries that could be promoted:

- Decisions (under `## Decisions`)
- Corrections (under `## Corrections`)
- Commitments (under `## Commitments`)
- Open loops (under `## Open Loops`)

Present candidates:

```
Promotion candidates (last 7 days):

1. [daily/2026-02-12.md] Decision
   "Chose FastAPI over Django for the carbon calculator API"
   -> [p]romote to registers/decisions.md / [s]kip

2. [daily/2026-02-13.md] Commitment
   "Deploy v2 by end of February"
   -> [p]romote to registers/open-loops.md / [s]kip
```

When promoting, assign an 8-char hex ID to the entry. If the entry is untagged, generate and assign the ID inline.

### 3. Pressure-Based Demotion (if over budget)

If working memory exceeds 1500 words:

Score working entries (excluding pinned):
```
score = 1.0 * word_count + 0.1 * days_since_last_verified
```

Present top candidates needed to bring under budget:

```
Working memory over budget (1723 words, need to free 223):

1. [CLAUDE.local.md] 23 words, last verified 45 days ago
   "Dave prefers concise error messages and no unnecessary logging"
   -> [k]eep / [p]in / [d]emote / [a]rchive / [m]ark superseded

2. [CLAUDE.local.md] 18 words, last verified 30 days ago
   "Current deployment target is AWS us-east-1"
   -> [k]eep / [p]in / [d]emote / [a]rchive / [m]ark superseded
```

**No ID precondition.** If an entry lacks an ID, assign one before processing.

Actions:
- **keep**: No file changes, mark as reviewed
- **pin**: Entry excluded from future demotion candidates
- **demote**: Move from CLAUDE.local.md to `registers/_inbox.md`
- **archive**: Move to `memory/archive/ARCHIVE.md`
- **mark superseded**: Entry will be archived on next maintain

### 4. Stale Entry Review

Find register entries not verified in 30+ days:

```
Stale entries (not verified in 30+ days):
  1. [registers/tech-stack.md] Last verified: 2025-12-01
     "Using Postgres 15 in production"
     -> [v]erify / [u]pdate / [a]rchive
```

### 5. Open Loop Review

Check `memory/registers/open-loops.md` for items that are past due or resolved.

### 6. Daily Log Archival

If daily logs older than 30 days exist, suggest archiving to `memory/archive/daily/`.

### 7. Summary

```
ark:maintain -- complete
==========================

Working memory: [before] -> [after] words (target: 1500)

Actions taken:
  Promoted: [N]
  Kept (reviewed): [N]
  Pinned: [N]
  Demoted: [N]
  Archived: [N]
  Superseded: [N]

Stale entries verified: [N]
Open loops reviewed: [N]
```
