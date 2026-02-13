---
description: Scaffold the Ark Session memory system in this project
allowed-tools: Read, Write, Bash, Glob
---

# /ark:init

Initialize the memory system in the current project. Creates directory structure and templates. Skips existing files.

## What To Do

### 1. Create Directory Structure

```
memory/
  SCHEMA.md
  daily/
  registers/
    _index.md
    people.md
    projects.md
    decisions.md
    preferences.md
    tech-stack.md
    open-loops.md
  archive/
    projects/
    daily/
```

Plus at project root: `CLAUDE.local.md` (working memory, gitignored).

### 2. Copy Templates

Copy template contents from the ark-sessionmanager templates directory. If a file already exists, skip it (never overwrite).

Template source: find ark-sessionmanager in the workspace or use inline defaults.

**CLAUDE.local.md**: Working memory template with sections for Active Context, Project State, Critical Preferences, Key Decisions, People Context, Open Loops, Session Continuity. ~1500 word limit.

**memory/SCHEMA.md**: Full schema documentation covering 4-tier architecture, write gate, routing table, contradiction protocol, correction handling, entry IDs, maintenance cadences.

**Register files**: Each with header comment explaining when to load and entry format.

### 3. Create Today's Daily Log

Create `memory/daily/[today].md`:

```markdown
# YYYY-MM-DD

## Decisions

## Corrections

## Commitments

## Open Loops

## Notes
```

### 4. Update .gitignore

Add `CLAUDE.local.md` to `.gitignore` if not already present (contains personal memory).

### 5. Output Summary

```
ark:init -- memory system scaffolded

Created:
  CLAUDE.local.md             (working memory -- auto-loaded)
  memory/SCHEMA.md            (schema docs)
  memory/daily/[date].md      (today's daily log)
  memory/registers/           (6 domain registers + index)
  memory/archive/             (for completed/superseded items)

Protocol: .claude/rules/ark-session.md (auto-loaded)

Quick start:
  /ark:write <note>    Save to memory (daily log first)
  /ark:search <query>  Find in memory
  /ark:maintain        Check memory health
```
