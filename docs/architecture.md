# Architecture

## Overview

ark-sessionmanager is a unified session lifecycle + memory persistence system for Claude Code. It merges two previously independent systems:

- **Total Recall** (memory persistence): 4-tier architecture, write gate, promotion, pressure-based demotion
- **Session Diary** (session lifecycle): Callsigns, crash detection, diary entries, heartbeat monitoring

## Design Principles

1. **Single library**: One Python file (`ark_session.py`) handles all session operations
2. **Prompt-driven memory**: Memory commands are Claude Code slash commands (prompt files), not Python code
3. **Fail-open**: All operations degrade gracefully if components are missing
4. **Machine-local sessions**: Session state in `~/.claude/sessions/` (never committed)
5. **Project-local memory**: Memory files in `{project}/memory/` (committed per project)

## Component Architecture

```
                     HOOK LAYER (4 hooks, Python)
         SessionStart    Stop    StatusLine    PreCompact
              |           |          |             |
              v           v          v             v
         +-------------------------------------------------+
         |          ark_session.py (~400 lines)            |
         |                                                  |
         |  SESSION ENGINE       |  MEMORY BRIDGE          |
         |  - session_start()    |  - sweep_session()      |
         |  - session_stop()     |                         |
         |  - session_heartbeat()|                         |
         |  - session_compact()  |                         |
         |  - detect_crashes()   |                         |
         |  - set_intent()       |                         |
         |  - get_active()       |                         |
         +-------------------------------------------------+
                      |                    |
        Machine-Local Storage     Project-Local Storage
        ~/.claude/sessions/       {project}/memory/
        - active.json             - daily/, registers/, archive/
        - log/*.jsonl             CLAUDE.local.md
                                  SESSION-LOG.md
```

## Memory Tiers

```
Conversation (ephemeral)
    |
    v  WRITE GATE
    |
Daily Log (memory/daily/YYYY-MM-DD.md)
    |
    v  PROMOTION
    |
Registers (memory/registers/*.md)
    |
    v  DISTILLATION
    |
Working Memory (CLAUDE.local.md)
    |
    v  EXPIRY
    |
Archive (memory/archive/)
```

## Session-Memory Bridge

The key architectural innovation. When `session_stop()` fires:

1. Write diary entry to `SESSION-LOG.md` (as before)
2. Call `sweep_session()` to append a `[session-end]` marker to today's daily log
3. Marker includes: callsign, duration, intent, compaction count

This captures session context in the memory system without auto-promoting. The user controls what's permanent via `/ark:maintain`.

## ID System

- **New format**: `^[0-9a-f]{8}` (8 hex chars, ~4.3 billion collision space)
- **Legacy format**: `^tr[0-9a-f]{10}` (accepted, never generated)
- **Scope**: Single-line list items in CLAUDE.local.md, registers, archive
- **NOT tagged**: Daily log entries, multi-line blocks, placeholders, code blocks

## Dynamic Workspace Short Codes

Previous system used a hardcoded map of workspace names to 3-4 char codes. New system derives codes dynamically:

1. Strip leading number prefix (e.g., "07-" from "07-Carbon-Meth-Hub")
2. Take initials of remaining hyphen-separated words
3. Uppercase, max 4 chars
4. Special case: home directory -> "CMD"

Examples:
- `07-Carbon-Meth-Hub` -> `CMH`
- `64-CORTEX-GUI` -> `CG`
- `70-GIS-Command-Center` -> `GCC`

## What Was Cut (~1050 lines saved)

| Feature | Lines | Why |
|---------|-------|-----|
| /recall-init-ids command | ~240 | IDs assigned on write/promote |
| /recall-context command | ~160 | Folded into /ark:maintain |
| /recall-log command | ~30 | Merged into /ark:write --quick |
| /recall-promote command | ~160 | Merged into /ark:maintain |
| /recall-status command | ~180 | Merged into /ark:maintain |
| Recall nudges | ~50 | Removed entirely |
| metadata.json timestamps | ~80 | Derive from file dates |
| snoozed_until field | ~30 | Pin + demote cover the cases |
| Hardcoded WORKSPACE_SHORT | ~25 | Dynamic resolution |
| Shell hooks (.sh) | ~100 | Python-only (Windows-first) |
