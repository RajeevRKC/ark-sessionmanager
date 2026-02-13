---
name: ark-forget
description: Marks memory entries matching a query as superseded without deleting them, preserving full history.
version: 1.0.0
tags: [memory, forget, supersede, cleanup]
---

# ark-forget

Marks memory entries as superseded. Preserves history, never deletes.

## When to Use

- Information is no longer current
- User says "forget that", "that's no longer true", "remove from memory"
- Correcting outdated facts across multiple tiers

## What It Does

1. Searches all memory tiers for matching entries
2. Shows matches and asks for confirmation
3. Marks entries as `[superseded: date]` in registers
4. Removes entries from CLAUDE.local.md (working memory = current only)
5. Adds superseded note to daily logs (historical record preserved)

## Key Behaviors

- Never deletes -- always marks as superseded
- Daily logs are append-only, original entries preserved
- User confirms which entries to supersede
- Can select all or individual entries

## References

- [Protocol](../../rules/ark-session.md)
