# Migration Guide

## From Total Recall

### Memory Files (No Migration Needed)

Your existing memory files are fully compatible:

| Location | Status |
|----------|--------|
| `CLAUDE.local.md` | Works as-is |
| `memory/daily/*.md` | Works as-is |
| `memory/registers/*.md` | Works as-is |
| `memory/archive/` | Works as-is |
| `memory/SCHEMA.md` | Replace with new version (optional) |
| `memory/.recall/metadata.json` | Optional, can be deleted (maintain no longer requires it) |

### Entry IDs (Backward Compatible)

- Old format `^tr[0-9a-f]{10}` is accepted everywhere
- New entries get `^[0-9a-f]{8}` format
- No need to re-tag existing entries
- `/ark:maintain` handles both formats

### metadata.json

The sidecar metadata file (`memory/.recall/metadata.json`) is no longer required. The maintain command handles untagged entries inline. You can:

1. Keep it (won't cause issues)
2. Delete it (maintain works without it)
3. It will be silently ignored

### Command Mapping

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `/recall-init` | `/ark:init` | Same behavior |
| `/recall-write <note>` | `/ark:write <note>` | Same write gate |
| `/recall-log <note>` | `/ark:write --quick <note>` | Bypasses gate |
| `/recall-search <query>` | `/ark:search <query>` | Same behavior |
| `/recall-promote` | `/ark:maintain` | Merged into maintain |
| `/recall-status` | `/ark:maintain` | Status is part of maintain |
| `/recall-maintain` | `/ark:maintain` | No ID precondition |
| `/recall-forget <query>` | `/ark:forget <query>` | Same behavior |
| `/recall-init-ids` | (removed) | IDs assigned on write/promote |
| `/recall-context` | `/ark:maintain` | Context shown in status |

### Protocol Rule

Replace `.claude/rules/total-recall.md` with `.claude/rules/ark-session.md`:

1. Copy `ark-session.md` to your project's `.claude/rules/`
2. Delete or rename `total-recall.md`
3. Both can coexist temporarily (no conflicts)

### Step-by-Step

1. Deploy library: `cp src/ark_session.py ~/.claude/hooks/ark_session.py`
2. Copy rule: `cp .claude/rules/ark-session.md {project}/.claude/rules/`
3. Copy commands: `cp -r .claude/commands/ark {project}/.claude/commands/`
4. Copy session commands: `cp -r .claude/commands/session {project}/.claude/commands/`
5. Test: Run `/ark:maintain` in your project
6. Clean up: Remove old `total-recall.md` when satisfied

## From Session Diary

### Session Files (No Migration Needed)

| Location | Status |
|----------|--------|
| `~/.claude/sessions/active.json` | Works as-is |
| `~/.claude/sessions/log/*.jsonl` | Works as-is |
| `.claude/tracker/sessions/SESSION-LOG.md` | Works as-is |

### Hook Updates

The hooks need to import `ark_session` instead of `session_diary`:

**In each hook file**, change:
```python
# Old
_diary_path = _Path(os.path.expanduser("~/.claude/hooks/session-diary.py"))
_spec = importlib.util.spec_from_file_location("session_diary", _diary_path)
_sd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sd)
result = _sd.session_start(input_data)

# New
_lib_path = _Path(os.path.expanduser("~/.claude/hooks/ark_session.py"))
_spec = importlib.util.spec_from_file_location("ark_session", _lib_path)
_ark = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ark)
result = _ark.session_start(input_data)
```

### API Compatibility

All functions have identical signatures and return types:

| Function | Signature | Returns |
|----------|-----------|---------|
| `session_start(data)` | Same | Same dict |
| `session_stop(data)` | Same | Same dict (+ now calls sweep_session) |
| `session_heartbeat(data)` | Same | Same dict |
| `session_compact(data)` | Same | None |
| `set_intent(session_id, text)` | Same | bool |
| `get_active_sessions()` | Same | Same list |

### New: sweep_session()

`session_stop()` now additionally calls `sweep_session()`. This is transparent -- it only writes to `memory/daily/` if the directory exists. If your project doesn't use the memory system, nothing changes.

### Workspace Short Codes

The hardcoded `WORKSPACE_SHORT` map is replaced by dynamic resolution. Your callsigns will change:

| Old | New | Why |
|-----|-----|-----|
| `CARB-a3f7` | `CMH-a3f7` | "Carbon-Meth-Hub" initials |
| `CRTX-7f21` | `CG-7f21` | "CORTEX-GUI" initials |
| `GIS-c8d5` | `GCC-c8d5` | "GIS-Command-Center" initials |

This is cosmetic only. Session tracking works the same regardless of callsign format.

### Command Mapping

| Old Command | New Command |
|-------------|-------------|
| `/session:intent <text>` | `/session:intent <text>` (same) |
| `/session:active` | `/session:active` (same) |
| `/session:log` | `/session:active --log` (merged) |
| `/session:close` | `/session:close` (same) |

## Combined Migration (Both Systems)

If your project uses both Total Recall and Session Diary:

1. Deploy `ark_session.py` to `~/.claude/hooks/`
2. Update hook imports (session-diary.py -> ark_session.py)
3. Copy `ark-session.md` rule to project
4. Copy ark and session commands to project
5. Remove old `total-recall.md` rule
6. Remove old recall-* commands
7. Remove old session-diary.py (after confirming hooks work)
8. Test: `/ark:maintain`, `/session:active`, `/session:close`

Data migration is not needed. All existing files are compatible.
