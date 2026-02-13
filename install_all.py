#!/usr/bin/env python3
"""Bulk installer -- scaffolds Ark Session memory system in all major workspaces."""

import os
import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "D:/My-Applications"))
TEMPLATE_DIR = Path(__file__).parent / "templates"
RULES_SRC = Path(__file__).parent / ".claude" / "rules" / "ark-session.md"

WORKSPACES = [
    "01-CineCrafter-Portal",
    "07-Carbon-Meth-Hub",
    "38-Legal-Matters",
    "40-Office-Team",
    "42-IT-Adviser",
    "52-Win-Claude",
    "54-Business-DevCon",
    "55-Bid-Tender-Contracts",
    "64-CORTEX-GUI",
    "65-ark-codewrap",
    "70-GIS-Command-Center",
    "80-Green-Sciences-Command-Center",
    "90-Programme-Command-Centre",
    "95-Mandan-Operations-Hub",
    "100-Aarksee-Component-Repository",
]

TODAY = datetime.now().strftime("%Y-%m-%d")

DAILY_TEMPLATE = f"""# {TODAY}

## Decisions

## Corrections

## Commitments

## Open Loops

## Notes
"""

# Directories to create inside each workspace
DIRS = [
    "memory/daily",
    "memory/registers",
    "memory/archive/projects",
    "memory/archive/daily",
]

# Template files to copy (source relative to TEMPLATE_DIR -> destination relative to workspace)
TEMPLATE_MAP = {
    "CLAUDE.local.md": "CLAUDE.local.md",
    "SCHEMA.md": "memory/SCHEMA.md",
    "registers/_index.md": "memory/registers/_index.md",
    "registers/people.md": "memory/registers/people.md",
    "registers/projects.md": "memory/registers/projects.md",
    "registers/decisions.md": "memory/registers/decisions.md",
    "registers/preferences.md": "memory/registers/preferences.md",
    "registers/tech-stack.md": "memory/registers/tech-stack.md",
    "registers/open-loops.md": "memory/registers/open-loops.md",
}

GITIGNORE_LINE = "CLAUDE.local.md"


def install_workspace(ws_path: Path) -> dict:
    """Scaffold memory system in a single workspace. Returns stats."""
    stats = {"name": ws_path.name, "created": [], "skipped": [], "errors": []}

    # 1. Create directories
    for d in DIRS:
        target = ws_path / d
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            stats["errors"].append(f"mkdir {d}: {e}")

    # 2. Copy template files (skip existing)
    for src_rel, dst_rel in TEMPLATE_MAP.items():
        src = TEMPLATE_DIR / src_rel
        dst = ws_path / dst_rel
        if dst.exists():
            stats["skipped"].append(dst_rel)
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            stats["created"].append(dst_rel)
        except Exception as e:
            stats["errors"].append(f"copy {dst_rel}: {e}")

    # 3. Create today's daily log (skip if exists)
    daily_file = ws_path / "memory" / "daily" / f"{TODAY}.md"
    if daily_file.exists():
        stats["skipped"].append(f"memory/daily/{TODAY}.md")
    else:
        try:
            daily_file.write_text(DAILY_TEMPLATE, encoding="utf-8")
            stats["created"].append(f"memory/daily/{TODAY}.md")
        except Exception as e:
            stats["errors"].append(f"daily log: {e}")

    # 4. Copy protocol rules file (skip if exists)
    rules_dst = ws_path / ".claude" / "rules" / "ark-session.md"
    if rules_dst.exists():
        stats["skipped"].append(".claude/rules/ark-session.md")
    else:
        try:
            rules_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RULES_SRC, rules_dst)
            stats["created"].append(".claude/rules/ark-session.md")
        except Exception as e:
            stats["errors"].append(f"rules: {e}")

    # 5. Update .gitignore
    gitignore = ws_path / ".gitignore"
    try:
        existing = ""
        if gitignore.exists():
            existing = gitignore.read_text(encoding="utf-8")
        if GITIGNORE_LINE not in existing:
            with open(gitignore, "a", encoding="utf-8") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write(f"{GITIGNORE_LINE}\n")
            stats["created"].append(".gitignore (updated)")
        else:
            stats["skipped"].append(".gitignore (already has entry)")
    except Exception as e:
        stats["errors"].append(f".gitignore: {e}")

    return stats


def main():
    print("=" * 60)
    print("  ARK SESSION -- BULK MEMORY SYSTEM INSTALLER")
    print(f"  Workspace root: {WORKSPACE_ROOT}")
    print(f"  Date: {TODAY}")
    print("=" * 60)
    print()

    total_created = 0
    total_skipped = 0
    total_errors = 0
    installed = []
    not_found = []

    for ws_name in WORKSPACES:
        ws_path = WORKSPACE_ROOT / ws_name
        if not ws_path.is_dir():
            not_found.append(ws_name)
            continue

        stats = install_workspace(ws_path)
        nc = len(stats["created"])
        ns = len(stats["skipped"])
        ne = len(stats["errors"])
        total_created += nc
        total_skipped += ns
        total_errors += ne

        status = "OK" if ne == 0 else "ERRORS"
        print(f"  [{status}] {ws_name}: {nc} created, {ns} skipped, {ne} errors")
        if ne > 0:
            for err in stats["errors"]:
                print(f"        ERROR: {err}")
        installed.append(ws_name)

    if not_found:
        print()
        print("  NOT FOUND:")
        for nf in not_found:
            print(f"    - {nf}")

    print()
    print("=" * 60)
    print(f"  RESULTS: {len(installed)} workspaces scaffolded")
    print(f"  Files created: {total_created}")
    print(f"  Files skipped: {total_skipped}")
    print(f"  Errors: {total_errors}")
    print("=" * 60)


if __name__ == "__main__":
    main()
