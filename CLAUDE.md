# ark-sessionmanager

> Unified session lifecycle + memory persistence for Claude Code.
> Memory protocol auto-loads via `.claude/rules/ark-session.md`.
> Working memory auto-loads via `CLAUDE.local.md`.

## Quick Reference

| What | Where | Loaded |
|------|-------|--------|
| Protocol + rules | `.claude/rules/ark-session.md` | Auto (every session) |
| Working memory | `CLAUDE.local.md` | Auto (every session) |
| Schema docs | `memory/SCHEMA.md` | Read on session start |
| Daily logs | `memory/daily/YYYY-MM-DD.md` | Check today + yesterday |
| Registers | `memory/registers/*.md` | On demand |
| Archive | `memory/archive/` | On search only |
| Session log | `.claude/tracker/sessions/SESSION-LOG.md` | On demand |

## Commands

| Command | Purpose |
|---------|---------|
| `/ark:init` | Scaffold the memory system |
| `/ark:write <note>` | Write to memory with gate evaluation |
| `/ark:search <query>` | Search all memory tiers |
| `/ark:maintain` | Status + promote + prune + health check |
| `/ark:forget <query>` | Mark entries as superseded |
| `/session:intent <text>` | Set session purpose |
| `/session:active` | Show active sessions |
| `/session:close` | Close session with enriched diary entry |

## Core Rules

1. **Write gate**: Does it change future behavior? If not, don't write.
2. **Daily log first**: All writes land in `memory/daily/` before promotion.
3. **Corrections propagate**: One correction updates daily log + register + CLAUDE.local.md.
4. **Never silently overwrite**: Mark old entries as `[superseded]`.
5. **1500 word limit** on CLAUDE.local.md -- demote or archive when approaching.

## Architecture

```
         HOOK LAYER (4 hooks)
    SessionStart  Stop  StatusLine  PreCompact
         |         |        |          |
         v         v        v          v
    +----------------------------------------------+
    |       src/ark_session.py (~400 lines)        |
    |                                              |
    |  SESSION ENGINE    |  MEMORY BRIDGE          |
    |  - session_start() |  - sweep_session()      |
    |  - session_stop()  |  (commands handle the   |
    |  - heartbeat()     |   rest via prompt logic)|
    |  - detect_crashes()|                         |
    +----------------------------------------------+
              |                    |
    Machine-Local Storage   Project-Local Storage
    ~/.claude/sessions/     {project}/memory/
```

## Library

Source: `src/ark_session.py`
Deploy: Copy to `~/.claude/hooks/ark_session.py`
Hooks import from same directory.

See `memory/SCHEMA.md` for complete memory system documentation.
