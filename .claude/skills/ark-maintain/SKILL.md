---
name: ark-maintain
description: Combined memory maintenance -- status check, promotion review, pressure-based demotion, stale entry verification, and open loop review.
version: 1.0.0
tags: [memory, maintain, promote, prune, health]
---

# ark-maintain

One command for all memory maintenance operations.

## When to Use

- Periodic memory health check (weekly recommended)
- Working memory approaching 1500-word limit
- After intensive work sessions with many decisions
- User says "check memory", "memory health", "promote entries"

## What It Does

1. **Status**: Reports working memory word count, register counts, daily log counts
2. **Promotion**: Reviews last 7 days of daily logs for promotion candidates
3. **Pressure demotion**: If over 1500 words, surfaces candidates for demotion
4. **Stale review**: Finds register entries not verified in 30+ days
5. **Open loops**: Reviews open-loops.md for past-due or resolved items
6. **Log archival**: Suggests archiving daily logs older than 30 days

## Key Behaviors

- No ID precondition: handles untagged entries by assigning IDs inline
- Accepts both `^[hex]{8}` and legacy `^tr[hex]{10}` ID formats
- User chooses per-entry: keep, pin, demote, archive, mark superseded
- Pinned entries are excluded from demotion candidates

## References

- [Protocol](../../rules/ark-session.md)
- [Schema](../../../templates/SCHEMA.md)
