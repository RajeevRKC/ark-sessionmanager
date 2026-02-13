---
description: Write enriched diary entry and close session context
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
---

# /session:close

Write a rich diary entry to SESSION-LOG.md with outcome and key files, then trigger memory sweep.

## Instructions

1. **Gather session context**:
   - Read `~/.claude/sessions/active.json` for current session metadata
   - Run `git diff --stat HEAD~5..HEAD` to find recently changed files
   - Run `git log --oneline -5` for recent commit messages

2. **Ask the user**: "Brief summary of what you accomplished this session?" (1-2 sentences)

3. **Build enriched diary entry**:
   - Callsign and time range from active session data
   - Branch and model from active session data
   - **Intent**: From active session (if set via `/session:intent`)
   - **Outcome**: From user's answer
   - **Key files**: Top 5 most-changed files from git diff (workspace-relative paths)
   - **Duration**: Calculated from session start time

4. **Write to SESSION-LOG.md**:
   - Path: `.claude/tracker/sessions/SESSION-LOG.md`
   - Group under today's date header
   - Insert at top of today's section (newest first)

5. **Trigger memory sweep**:
   - If `memory/daily/` exists, append `[session-end]` marker to today's daily log
   - Include callsign, duration, intent, and outcome

6. **Update active session**: Set intent from outcome if not already set

7. **Confirm**: Show the written diary entry

## Entry Format

```markdown
### a3f7b2c1 | 14:33-15:10 | feat/blue-carbon | Opus 4.6
**Duration**: 37 min
**Intent**: Implement blue carbon sequestration calculator
**Outcome**: Completed calculator module, tests passing
**Key files**: `src/calculators/blue_carbon.py`, `tests/test_blue_carbon.py`
**Notes**: Found issue with tidal zone coefficients
```

## Notes
- Creates richer entries than the automatic Stop hook
- Use before ending a session for better cross-machine context
- All file paths must be workspace-relative (no absolute paths)
- The Stop hook still fires -- it checks if entry already exists
