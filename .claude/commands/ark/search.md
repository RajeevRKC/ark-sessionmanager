---
description: Search across all memory tiers for relevant information
args: query - What to search for
allowed-tools: Read, Grep, Glob
---

# /ark:search

Search across all memory tiers for relevant information.

Query: $ARGUMENTS

## Search Protocol

Search in this order (narrow to wide):

### 1. Working Memory (CLAUDE.local.md)
Already loaded -- check if the answer is here first.

### 2. Registers (memory/registers/*.md)
Search all register files for content matching the query.

### 3. Recent Daily Logs (memory/daily/)
Search the last 14 days of daily logs. Start with most recent.

### 4. Archive (memory/archive/)
Only search here if nothing found in tiers 1-3, or if the query explicitly asks about historical/past items.

## How to Search

Use Grep across the memory directory for matching content. Search for relevant terms, synonyms, and related phrases.

## Output Format

Present results grouped by source, most relevant first:

```
Found [N] relevant entries:

[registers/decisions.md] (confidence: high)
  2026-01-15: Chose JWT over session cookies for stateless scaling

[registers/tech-stack.md] (confidence: high)
  Auth: JWT tokens with 24h expiry, refresh via /auth/refresh

[daily/2026-02-01.md]
  [14:32] Discussed adding OAuth2 for third-party integrations, decided to defer
```

## If Nothing Found

```
No matching entries found in memory.

Searched: CLAUDE.local.md, [N] registers, [N] daily logs, [N] archive files.
```

Suggest `/ark:write` to capture the information if the user has it.

## Rules

- Show actual content, not just file names
- Include confidence levels when available
- Show dates and timestamps for daily log entries
- If a result is marked `[superseded]`, note that and show current entry
- Do NOT fabricate results -- only return what's in the files
