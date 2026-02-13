---
name: session-intent
description: Captures session purpose for the diary and crash context. Shows in toast notifications and crash recovery.
version: 1.0.0
tags: [session, intent, diary, context]
---

# session-intent

Captures what the user is working on this session.

## When to Use

- Start of a focused work session
- User says "I'm working on", "session intent", "set intent"
- Before deep work that might crash

## What It Does

1. Takes intent text from the user
2. Updates `~/.claude/sessions/active.json` for the current session
3. Intent propagates to diary entry on session stop
4. Shows in toast notification on close
5. Shows in crash context for recovery

## Key Behaviors

- One-liner, keep under 80 characters
- Updates machine-local session registry
- Persists across the session lifetime

## References

- [Protocol](../../rules/ark-session.md)
