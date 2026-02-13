---
name: session-close
description: Writes an enriched diary entry with outcome, key files, and duration, then triggers memory sweep for session context capture.
version: 1.0.0
tags: [session, close, diary, sweep]
---

# session-close

Creates a rich diary entry and triggers the session-memory bridge.

## When to Use

- End of a focused work session
- User says "close session", "wrap up", "end session"
- Before switching to a different project

## What It Does

1. Gathers session context (metadata, git diff, recent commits)
2. Asks user for outcome summary
3. Writes enriched entry to SESSION-LOG.md
4. Triggers memory sweep (appends session-end marker to daily log)
5. Updates session intent if not already set

## Key Behaviors

- Richer entries than the automatic Stop hook
- All file paths are workspace-relative
- Memory sweep captures session context but doesn't auto-promote
- Stop hook still fires separately

## References

- [Protocol](../../rules/ark-session.md)
