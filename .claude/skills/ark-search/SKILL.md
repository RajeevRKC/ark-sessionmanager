---
name: ark-search
description: Searches across all four memory tiers (working memory, registers, daily logs, archive) for relevant information.
version: 1.0.0
tags: [memory, search, recall, find]
---

# ark-search

Searches across all memory tiers for information matching a query.

## When to Use

- User asks "do you remember", "what did we decide about", "find in memory"
- Need to check existing memory before answering history/preference questions
- Looking for past decisions, preferences, or commitments

## What It Does

1. Checks CLAUDE.local.md (already loaded)
2. Searches registers (memory/registers/*.md)
3. Searches last 14 days of daily logs
4. Searches archive (only if nothing found in tiers 1-3)

## Key Behaviors

- Returns actual content, not just file names
- Results grouped by source, most relevant first
- Shows confidence levels and timestamps
- Notes superseded entries
- Never fabricates results

## References

- [Protocol](../../rules/ark-session.md)
