# ark-sessionmanager

## Vision
Unified session lifecycle + memory persistence for Claude Code. Merges Total Recall (memory) and Session Diary (session lifecycle) into a single, streamlined package.

## Goals
1. Single library (`ark_session.py`) handles both session tracking and memory bridge
2. 8 commands (down from 14) cover all memory and session operations
3. Protocol rule file under 100 lines (loads every session)
4. Dynamic workspace short codes (no hardcoded maps)
5. Session-memory bridge: session close triggers daily log sweep

## Non-Goals
- Plugin distribution format (standalone only)
- Recall nudges (removed)
- Separate init-ids command (IDs assigned on write/promote)
- Metadata timestamps file (derive from file modification dates)

## Success Criteria
- Library self-test passes on Windows 11
- Protocol is under 100 lines
- All 8 commands work end-to-end
- Session stop writes both diary and daily log entry
- Backward compatible with existing ^tr ID format
