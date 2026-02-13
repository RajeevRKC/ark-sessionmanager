# ark-sessionmanager

Unified session lifecycle + memory persistence for Claude Code. Merges the battle-tested Total Recall memory system with Session Diary into a single, streamlined package.

## What It Does

- **Session tracking**: Callsigns, crash detection, diary entries, heartbeat monitoring
- **Memory persistence**: 4-tier memory architecture with write gate, promotion, and pressure-based demotion
- **Session-memory bridge**: Session close automatically captures context in the daily log

## Install

1. Copy `src/ark_session.py` to `~/.claude/hooks/ark_session.py`
2. Copy `.claude/rules/ark-session.md` to your project's `.claude/rules/`
3. Copy `.claude/commands/` to your project's `.claude/commands/`
4. Run `/ark:init` in your project to scaffold the memory system

## Commands (8)

| Command | Purpose |
|---------|---------|
| `/ark:init` | Scaffold memory directories and templates |
| `/ark:write <note>` | Write to memory with gate evaluation |
| `/ark:search <query>` | Search across all memory tiers |
| `/ark:maintain` | Combined status + promote + prune + health |
| `/ark:forget <query>` | Mark entries as superseded |
| `/session:intent <text>` | Set session purpose (shows in diary) |
| `/session:active` | List all active sessions on this machine |
| `/session:close` | Enriched diary entry + memory sweep |

## Architecture

```
67-ark-sessionmanager/
  .claude/
    rules/ark-session.md          # Protocol (<100 lines, auto-loads)
    commands/ark/*.md              # 5 memory commands
    commands/session/*.md          # 3 session commands
    skills/                       # 8 matching SKILL.md files
  src/
    ark_session.py                # Core library (~400 lines)
  templates/                      # Memory scaffolding templates
    CLAUDE.local.md               # Working memory template
    SCHEMA.md                     # Memory schema docs
    registers/                    # 7 register templates
  docs/
    architecture.md               # Technical deep-dive
    migration.md                  # From Total Recall / Session Diary
```

## Migration

See `docs/migration.md` for step-by-step migration from Total Recall or Session Diary.

Key points:
- Existing `^tr` IDs are accepted alongside new `^[hex]{8}` format
- Memory files are compatible -- no data migration needed
- Commands map directly: `/recall-write` -> `/ark:write`, etc.
