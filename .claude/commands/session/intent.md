---
description: Set session purpose for diary and crash context
args: intent_text - Brief description of what you're working on
allowed-tools: Read, Write, Bash
---

# /session:intent

Quick intent capture for the current session. Updates the session registry with what you're working on.

Intent: $ARGUMENTS

## Instructions

1. **Get the intent text** from the argument. If no argument, ask: "What are you working on this session?"

2. **Write intent to active session**:
   - Read `~/.claude/sessions/active.json`
   - Find the entry matching the current session ID (most recent active)
   - Update its `intent` field with the provided text
   - Write back to `active.json`

3. **Confirm**: `Intent set: "[intent_text]"`

## Notes
- Intent is a one-liner -- keep under 80 characters
- Propagates to diary entry on session stop
- Shows in toast notification on session close
- Shows in crash context if session crashes
