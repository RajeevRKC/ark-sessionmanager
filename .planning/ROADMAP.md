# Roadmap

## Milestone 1: v1.0 -- Unified Session + Memory Manager

### Phase 1: Foundation
- [x] Project scaffold + directory structure
- [x] Core library `src/ark_session.py`
- [x] Protocol rules `.claude/rules/ark-session.md`
- [x] All templates (CLAUDE.local.md, SCHEMA.md, 7 registers)
- [x] GSD files (PROJECT.md, ROADMAP.md, STATE.md)
- [x] CLAUDE.md + README.md

### Phase 2: Commands + Skills
- [x] 5 memory commands (ark/init, write, search, maintain, forget)
- [x] 3 session commands (session/intent, active, close)
- [x] 8 matching SKILL.md files

### Phase 3: Integration + Hooks
- [x] Hook configuration template
- [x] Session-memory bridge wiring (sweep_session)
- [x] Crash recovery with memory context
- [x] Hook integration documentation

### Phase 4: Polish + Migration
- [x] docs/architecture.md
- [x] docs/migration.md
- [x] Backward compatibility validation
- [x] Deploy ark_session.py to ~/.claude/hooks/
