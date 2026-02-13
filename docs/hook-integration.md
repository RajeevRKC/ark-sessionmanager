# Hook Integration Guide

How to wire ark-sessionmanager hooks into your Claude Code environment.

## Prerequisites

1. `ark_session.py` deployed to `~/.claude/hooks/ark_session.py`
2. Existing hooks: `gsd-session-start.py`, `stop-notification.py`, `statusline.py`, `pre-compact.py`

## Hook Architecture

```
Hook Event         -> Hook Script              -> ark_session.py function
-----------           -----------                 -------------------------
SessionStart       -> gsd-session-start.py     -> session_start(data)
Stop               -> stop-notification.py     -> session_stop(data)
StatusLine         -> statusline.py            -> session_heartbeat(data)
PreCompact         -> pre-compact.py           -> session_compact(data)
```

Each existing hook dynamically imports `ark_session.py` from `~/.claude/hooks/` and calls the appropriate function. The hooks are fail-open -- if the library is missing, they continue without session tracking.

## Import Pattern

All hooks use the same import pattern:

```python
try:
    from pathlib import Path as _Path
    _lib_path = _Path(os.path.expanduser("~/.claude/hooks/ark_session.py"))
    if _lib_path.exists():
        import importlib.util
        _spec = importlib.util.spec_from_file_location("ark_session", _lib_path)
        _ark = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_ark)

        result = _ark.session_start(input_data)  # or session_stop, etc.
except Exception:
    pass  # Fail-open: session tracking is optional
```

## Migration from session-diary.py

The hooks currently import `session-diary.py`. To switch to `ark_session.py`:

1. Deploy: `cp src/ark_session.py ~/.claude/hooks/ark_session.py`
2. Update import name in hooks: `session_diary` -> `ark_session`
3. Update file name in hooks: `session-diary.py` -> `ark_session.py`
4. The API is identical -- same function signatures, same return types

### Function Mapping

| Hook | Old call | New call |
|------|----------|----------|
| SessionStart | `session_diary.session_start(data)` | `ark_session.session_start(data)` |
| Stop | `session_diary.session_stop(data)` | `ark_session.session_stop(data)` |
| StatusLine | `session_diary.session_heartbeat(data)` | `ark_session.session_heartbeat(data)` |
| PreCompact | `session_diary.session_compact(data)` | `ark_session.session_compact(data)` |

## Session-Memory Bridge

The key new feature: `session_stop()` now calls `sweep_session()` after writing the diary entry. This appends a `[session-end]` marker to today's daily log (`memory/daily/YYYY-MM-DD.md`) if the memory system is initialized.

The marker includes:
- Callsign
- Duration in minutes
- Intent (if set)
- Compaction count

This is a **capture-only** operation. It does not auto-promote anything. The user controls promotion via `/ark:maintain`.

## Crash Recovery with Memory Context

When `session_start()` detects crashed sessions (stale heartbeat + dead PID), the crash info now includes enough context for memory recovery:

```python
crash_info = {
    "session_id": "...",
    "callsign": "CMH-a3f7",
    "workspace": "07-Carbon-Meth-Hub",
    "branch": "feat/blue-carbon",
    "intent": "Fix tidal coefficients",
    "last_heartbeat": "2026-02-14T10:30:00",
    "started": "2026-02-14T09:15:00",
}
```

The SessionStart hook injects this as additional context, so the new session can check if the crashed session left unsaved memory.

## Hook Configuration Template

For `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/gsd-session-start.py 2>nul"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/stop-notification.py 2>nul"
          }
        ]
      }
    ],
    "StatusLine": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/statusline.py 2>nul"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/pre-compact.py 2>nul"
          }
        ]
      }
    ]
  }
}
```

## Testing

1. Start a session: verify callsign appears in status line
2. Set intent: `/session:intent Testing the new system`
3. Check active: `/session:active`
4. Stop session: verify diary entry in SESSION-LOG.md
5. Check daily log: verify `[session-end]` marker if memory system is initialized
6. Crash recovery: start a new session, verify previous crash is detected
