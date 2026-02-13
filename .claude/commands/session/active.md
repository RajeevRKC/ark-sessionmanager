---
description: Show all running Claude Code sessions on this machine
args: Use --log to show session diary instead
allowed-tools: Read, Bash, Glob
---

# /session:active

Show all currently active Claude Code sessions, or the session diary.

Arguments: $ARGUMENTS

## Active Sessions (default)

1. **Read the active registry**: `~/.claude/sessions/active.json`
2. **Filter** to entries where `status == "active"`
3. **Calculate duration** for each (now - started)
4. **Get machine ID** from `~/.claude/machine.local.yaml`

Display:

```
ACTIVE SESSIONS (machine-id)
====================================
  CMH-a3f7  | 07-Carbon-Meth-Hub     | feat/blue-carbon | 37 min | 45% ctx
  CG-7f21   | 64-CORTEX-GUI          | main*            | 12 min | 18% ctx
  GCC-c8d5  | 70-GIS-Command-Center  | analysis         |  5 min |  8% ctx

3 active sessions
```

If no active sessions: "No active sessions."

## Session Diary (--log flag)

If arguments contain `--log`:

1. Read `.claude/tracker/sessions/SESSION-LOG.md` in current workspace
2. Display the last 10 entries

## Column Reference

| Column | Source |
|--------|--------|
| Callsign | `callsign` field |
| Workspace | `workspace` field |
| Branch | `branch` field |
| Duration | Calculated from `started` |
| Context | `context_pct` field + "% ctx" |
