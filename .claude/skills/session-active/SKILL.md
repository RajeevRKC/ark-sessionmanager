---
name: session-active
description: Shows all running Claude Code sessions on this machine with callsigns, duration, and context usage.
version: 1.0.0
tags: [session, active, monitor, status]
---

# session-active

Displays all active Claude Code sessions on the current machine.

## When to Use

- User asks "what sessions are running", "show active sessions"
- Need to identify which terminal is which
- Use `--log` flag to see session diary instead

## What It Does

1. Reads `~/.claude/sessions/active.json`
2. Filters to active sessions
3. Displays table with callsign, workspace, branch, duration, context usage
4. With `--log`: shows SESSION-LOG.md diary entries

## Key Behaviors

- Shows machine ID from machine.local.yaml
- Calculates duration from session start time
- Context percentage from last heartbeat update

## References

- [Protocol](../../rules/ark-session.md)
