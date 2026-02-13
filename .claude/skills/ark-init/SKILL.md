---
name: ark-init
description: Scaffolds the Ark Session memory system in a project with 4-tier architecture, register templates, and working memory.
version: 1.0.0
tags: [memory, session, scaffold, setup]
---

# ark-init

Initializes the Ark Session memory system in the current project.

## When to Use

- Setting up a new project that needs persistent memory
- User says "initialize memory", "set up recall", "scaffold memory"
- Project has no `memory/` directory yet

## What It Does

1. Creates `memory/` directory structure (daily, registers, archive)
2. Creates `CLAUDE.local.md` at project root (working memory template)
3. Creates `memory/SCHEMA.md` (system documentation)
4. Creates 7 register files from templates
5. Creates today's daily log
6. Adds `CLAUDE.local.md` to `.gitignore`

## Key Behaviors

- Never overwrites existing files
- Uses templates from ark-sessionmanager if available
- Outputs a summary of what was created

## References

- [Protocol](../../rules/ark-session.md)
- [Schema Template](../../../templates/SCHEMA.md)
