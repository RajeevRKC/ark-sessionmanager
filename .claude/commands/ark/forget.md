---
description: Mark memory entries matching a query as superseded
args: query - What to forget (search term)
allowed-tools: Read, Write, Edit, Grep, Glob
---

# /ark:forget

Mark memory entries matching a query as superseded. Does not delete -- preserves history.

Query to forget: $ARGUMENTS

## What To Do

### 1. Search for Matching Entries

Search across all memory tiers:
- CLAUDE.local.md
- memory/registers/*.md
- memory/daily/*.md

### 2. Show Matches

```
Found [N] entries matching "[query]":

1. [CLAUDE.local.md] "Prefers dark mode for all mockups"
2. [registers/preferences.md] "Dark mode preference (confidence: high)"
3. [daily/2026-01-10.md] "[14:00] User said they prefer dark mode"
```

### 3. Confirm with User

```
Mark these as superseded? This won't delete them -- they'll be annotated.

[a]ll / select by number / [c]ancel
```

### 4. Execute

For each confirmed entry:

**In registers**: Mark as superseded with date:
```markdown
## [superseded: 2026-02-05]
- **claim**: Prefers dark mode for all mockups
- **superseded_by**: User requested removal via /ark:forget
- **original_date**: 2026-01-10
```

**In CLAUDE.local.md**: Remove the entry entirely (working memory = current facts only).

**In daily logs**: Add a note but don't modify the original entry (historical record):
```
[HH:MM] [superseded] "Prefers dark mode" -- marked as no longer current via /ark:forget
```

### 5. Confirm

```
Superseded [N] entries for "[query]".
Memory updated across [N] files.
```
