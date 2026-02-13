#!/usr/bin/env python3
"""
Ark Session Manager -- Core Module
====================================
Unified session lifecycle + memory bridge for Claude Code.

Machine-local storage: ~/.claude/sessions/
Portable diary: {workspace}/.claude/tracker/sessions/SESSION-LOG.md
Memory bridge: {workspace}/memory/daily/ (append on session close)

Refactored from session-diary.py (v1). Removes hardcoded workspace map,
adds dynamic resolution from machine.local.yaml, adds sweep_session()
memory bridge.

Author: MasterMindMandan
Date: 2026-02-14
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# -- Configuration ----------------------------------------------------------

SESSIONS_DIR = Path(os.path.expanduser("~/.claude/sessions"))
LOG_DIR = SESSIONS_DIR / "log"
ACTIVE_FILE = SESSIONS_DIR / "active.json"
MACHINE_CONFIG = Path(os.path.expanduser("~/.claude/machine.local.yaml"))

HEARTBEAT_THROTTLE_SECONDS = 60
CRASH_THRESHOLD_MINUTES = 10
JSONL_MAX_DAYS = 30

# Cache for workspace short codes (resolved once per process)
_ws_short_cache = {}


# -- Internal helpers -------------------------------------------------------

def _ensure_dirs():
    """Create session directories if they don't exist."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _read_active():
    """Read active sessions registry. Returns dict."""
    try:
        if ACTIVE_FILE.exists():
            return json.loads(ACTIVE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _write_active(data):
    """Write active sessions registry with fail-open semantics."""
    _ensure_dirs()
    try:
        ACTIVE_FILE.write_text(
            json.dumps(data, indent=2, default=str), encoding="utf-8"
        )
    except Exception:
        pass


def _write_jsonl_event(event):
    """Append event to daily JSONL log."""
    _ensure_dirs()
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{today}.jsonl"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")
    except Exception:
        pass


def _load_machine_config():
    """Load machine.local.yaml for workspace root. Returns dict or None."""
    if not MACHINE_CONFIG.exists():
        return None
    try:
        # Minimal YAML parsing -- avoid external dependency
        content = MACHINE_CONFIG.read_text(encoding="utf-8")
        config = {}
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("workspace_root:"):
                val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                config["workspace_root"] = val
            elif stripped.startswith("id:"):
                val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                config["machine_id"] = val
        return config if config else None
    except Exception:
        return None


def _resolve_workspace_short(cwd):
    """
    Dynamic workspace short code from directory name.
    No hardcoded map -- derives from directory basename.

    Rules:
    1. Strip leading number prefix (e.g., "07-" from "07-Carbon-Meth-Hub")
    2. Take initials of remaining hyphen-separated words (max 4 chars)
    3. Uppercase the result
    4. Special case: home directory -> "CMD"
    """
    if cwd in _ws_short_cache:
        return _ws_short_cache[cwd]

    cwd_normalized = cwd.replace("\\", "/")
    basename = os.path.basename(cwd_normalized.rstrip("/"))

    # Home directory check
    home_dir = os.path.expanduser("~")
    if os.path.normpath(cwd) == os.path.normpath(home_dir):
        _ws_short_cache[cwd] = "CMD"
        return "CMD"

    # Strip leading number prefix (e.g., "07-", "100-")
    parts = basename.split("-")
    if parts and parts[0].isdigit():
        parts = parts[1:]

    if not parts:
        short = basename[:4].upper()
    else:
        # Take first letter of each word, max 4
        initials = "".join(p[0] for p in parts if p)[:4].upper()
        short = initials if len(initials) >= 2 else basename[:4].upper()

    _ws_short_cache[cwd] = short
    return short


def _get_git_branch(cwd):
    """Get current git branch, returns '-' on failure."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=2, cwd=cwd,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "-"


# -- Public API: Session Lifecycle ------------------------------------------

def get_callsign(session_id, cwd):
    """
    Generate callsign like CARB-a3f7 from session ID and workspace.

    Args:
        session_id: Claude Code session UUID
        cwd: Current working directory

    Returns:
        str: Callsign e.g. "CMH-a3f7"
    """
    short = _resolve_workspace_short(cwd)
    sid_suffix = session_id[:4] if session_id else "0000"
    return f"{short}-{sid_suffix}"


def session_start(data):
    """
    Register a new session. Called by SessionStart hook.

    Args:
        data: Hook input data (session_id, cwd, model, etc.)

    Returns:
        dict with callsign and crash_info (if any)
    """
    _ensure_dirs()

    session_id = data.get("session_id", "unknown")
    cwd = data.get("cwd", os.getcwd())
    model = data.get("model", {})
    branch = _get_git_branch(cwd)

    model_display = (
        model.get("display_name", "Claude")
        if isinstance(model, dict) else str(model)
    )

    callsign = get_callsign(session_id, cwd)
    now = datetime.now()

    active = _read_active()
    active[session_id] = {
        "callsign": callsign,
        "workspace": os.path.basename(cwd.replace("\\", "/").rstrip("/")),
        "workspace_path": cwd.replace("\\", "/"),
        "branch": branch,
        "model": model_display,
        "pid": os.getpid(),
        "started": now.isoformat(),
        "last_heartbeat": now.isoformat(),
        "context_pct": 0,
        "compact_count": 0,
        "intent": "",
        "status": "active",
    }
    _write_active(active)

    _write_jsonl_event({
        "event": "start",
        "session_id": session_id,
        "callsign": callsign,
        "workspace": os.path.basename(cwd.replace("\\", "/").rstrip("/")),
        "branch": branch,
        "model": model_display,
        "pid": os.getpid(),
        "ts": now.isoformat(),
    })

    crash_info = detect_crashes()
    cleanup_old_logs()

    return {
        "callsign": callsign,
        "session_id": session_id,
        "crash_info": crash_info,
    }


def session_stop(data):
    """
    Close a session. Called by Stop hook.

    Writes diary entry to SESSION-LOG.md and triggers memory sweep.

    Args:
        data: Hook input data

    Returns:
        dict with session summary
    """
    session_id = data.get("session_id", "unknown")
    stop_reason = data.get("stop_reason", "completed")
    cwd = data.get("cwd", os.getcwd())
    now = datetime.now()

    active = _read_active()
    session = active.get(session_id, {})

    started_str = session.get("started", now.isoformat())
    try:
        started = datetime.fromisoformat(started_str)
        duration_min = int((now - started).total_seconds() / 60)
    except Exception:
        duration_min = 0

    callsign = session.get("callsign", get_callsign(session_id, cwd))
    intent = session.get("intent", "")
    branch = session.get("branch", "-")
    model = session.get("model", "Claude")
    compact_count = session.get("compact_count", 0)

    if session_id in active:
        active[session_id]["status"] = "stopped"
        active[session_id]["stopped"] = now.isoformat()
        active[session_id]["duration_min"] = duration_min
        active[session_id]["stop_reason"] = stop_reason
        _write_active(active)

    _write_jsonl_event({
        "event": "stop",
        "session_id": session_id,
        "callsign": callsign,
        "reason": stop_reason,
        "duration_min": duration_min,
        "compact_count": compact_count,
        "ts": now.isoformat(),
    })

    # Write diary entry to workspace SESSION-LOG.md
    try:
        start_dt = datetime.fromisoformat(started_str)
        time_range = f"{start_dt.strftime('%H:%M')}-{now.strftime('%H:%M')}"
    except Exception:
        time_range = f"?-{now.strftime('%H:%M')}"

    ws_path = session.get("workspace_path", cwd)
    write_diary_entry(
        workspace_path=ws_path,
        callsign=callsign,
        session_id=session_id,
        time_range=time_range,
        branch=branch,
        model=model,
        intent=intent,
        duration_min=duration_min,
    )

    # Session-Memory Bridge: sweep session context into daily log
    sweep_session(
        workspace_path=ws_path,
        callsign=callsign,
        duration_min=duration_min,
        intent=intent,
        compact_count=compact_count,
    )

    return {
        "callsign": callsign,
        "duration_min": duration_min,
        "intent": intent,
    }


def session_heartbeat(data):
    """
    Update heartbeat and context percentage. Throttled to once per 60s.
    Called by StatusLine hook.

    Args:
        data: Hook input data with context_window info

    Returns:
        dict with callsign (or None if no session found)
    """
    session_id = data.get("session_id", "")
    if not session_id:
        return None

    active = _read_active()
    session = active.get(session_id)
    if not session or session.get("status") != "active":
        return None

    now = datetime.now()

    try:
        last_hb = datetime.fromisoformat(
            session.get("last_heartbeat", "2000-01-01")
        )
        if (now - last_hb).total_seconds() < HEARTBEAT_THROTTLE_SECONDS:
            return {"callsign": session.get("callsign", ""), "throttled": True}
    except Exception:
        pass

    ctx_pct = -1
    ctx_window = data.get("context_window", {})
    usage = ctx_window.get("current_usage", {})
    size = ctx_window.get("context_window_size", 0)
    if usage and size > 0:
        tokens = (
            usage.get("input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
        )
        ctx_pct = int(tokens * 100 / size)

    session["last_heartbeat"] = now.isoformat()
    if ctx_pct >= 0:
        session["context_pct"] = ctx_pct
    active[session_id] = session
    _write_active(active)

    return {"callsign": session.get("callsign", ""), "throttled": False}


def session_compact(data):
    """
    Log compaction event. Called by PreCompact hook.

    Args:
        data: Hook input data
    """
    session_id = data.get("session_id", "unknown")

    active = _read_active()
    session = active.get(session_id, {})
    count = session.get("compact_count", 0) + 1

    if session_id in active:
        active[session_id]["compact_count"] = count
        _write_active(active)

    _write_jsonl_event({
        "event": "compact",
        "session_id": session_id,
        "count": count,
        "ts": datetime.now().isoformat(),
    })


def detect_crashes():
    """
    Find stale active sessions (>10min no heartbeat).
    Cross-checks PID on Windows. Marks stale as crashed.

    Returns:
        list of crash info dicts, or empty list
    """
    active = _read_active()
    crashes = []
    now = datetime.now()
    threshold = timedelta(minutes=CRASH_THRESHOLD_MINUTES)

    for sid, session in list(active.items()):
        if session.get("status") != "active":
            continue

        try:
            last_hb = datetime.fromisoformat(
                session.get("last_heartbeat", "2000-01-01")
            )
            if (now - last_hb) <= threshold:
                continue

            pid = session.get("pid")
            pid_alive = False
            if pid:
                try:
                    import subprocess
                    result = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                        capture_output=True, text=True, timeout=3,
                    )
                    pid_alive = str(pid) in result.stdout
                except Exception:
                    pass

            if not pid_alive:
                active[sid]["status"] = "crashed"
                active[sid]["crashed_at"] = now.isoformat()

                crashes.append({
                    "session_id": sid,
                    "callsign": session.get("callsign", ""),
                    "workspace": session.get("workspace", ""),
                    "branch": session.get("branch", ""),
                    "intent": session.get("intent", ""),
                    "last_heartbeat": session.get("last_heartbeat", ""),
                    "started": session.get("started", ""),
                })

                _write_jsonl_event({
                    "event": "crash",
                    "session_id": sid,
                    "callsign": session.get("callsign", ""),
                    "workspace": session.get("workspace", ""),
                    "last_heartbeat": session.get("last_heartbeat", ""),
                    "ts": now.isoformat(),
                })
        except Exception:
            continue

    if crashes:
        _write_active(active)

    _purge_stale_sessions(active)
    return crashes


def set_intent(session_id, intent_text):
    """
    Set intent for a session. Called by /session:intent command.

    Args:
        session_id: Current session ID
        intent_text: Intent description

    Returns:
        bool: True if session found and updated
    """
    active = _read_active()
    if session_id in active:
        active[session_id]["intent"] = intent_text
        _write_active(active)
        return True
    return False


def get_active_sessions():
    """
    Get all active sessions for display.

    Returns:
        list of active session dicts with session_id included
    """
    active = _read_active()
    results = []
    for sid, session in active.items():
        if session.get("status") == "active":
            results.append({**session, "session_id": sid})
    return results


def get_machine_id():
    """Get machine ID from machine.local.yaml."""
    config = _load_machine_config()
    return config.get("machine_id", "unknown") if config else "unknown"


# -- Public API: Memory Bridge ----------------------------------------------

def sweep_session(workspace_path, callsign, duration_min, intent="",
                  compact_count=0):
    """
    Session-Memory Bridge: append a session-end marker to today's daily log.

    This captures session metadata in the memory system without auto-promoting.
    The user controls what gets promoted via /ark:maintain.

    Args:
        workspace_path: Absolute path to workspace root
        callsign: Session callsign (e.g. "CMH-a3f7")
        duration_min: Session duration in minutes
        intent: Session intent text
        compact_count: Number of compactions during session
    """
    ws_path = Path(workspace_path.replace("\\", "/"))
    daily_dir = ws_path / "memory" / "daily"

    # Only write if the memory system is initialized
    if not daily_dir.exists():
        return

    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = daily_dir / f"{today}.md"
    now_time = datetime.now().strftime("%H:%M")

    # Build session marker
    parts = [f"[{now_time}] [session-end] {callsign} | {duration_min} min"]
    if intent:
        parts[0] += f' | intent: "{intent}"'
    if compact_count > 0:
        parts[0] += f" | {compact_count} compactions"

    entry = "\n".join(parts) + "\n"

    try:
        if daily_file.exists():
            existing = daily_file.read_text(encoding="utf-8")
            # Append under Notes section, or at end
            if "## Notes" in existing:
                idx = existing.index("## Notes") + len("## Notes")
                while idx < len(existing) and existing[idx] == "\n":
                    idx += 1
                content = existing[:idx] + "\n" + entry + existing[idx:]
            else:
                content = existing.rstrip("\n") + "\n\n" + entry
            daily_file.write_text(content, encoding="utf-8")
        # If daily file doesn't exist, skip -- don't create files during sweep
    except Exception:
        pass


# -- Internal: Diary + Cleanup ---------------------------------------------

def write_diary_entry(workspace_path, callsign, session_id, time_range,
                      branch, model, intent="", outcome="", key_files="",
                      notes="", duration_min=0):
    """
    Append entry to workspace SESSION-LOG.md (portable, git-tracked).
    Branch name serves as cross-machine correlation key.
    """
    ws_path = Path(workspace_path.replace("\\", "/"))
    diary_dir = ws_path / ".claude" / "tracker" / "sessions"
    diary_file = diary_dir / "SESSION-LOG.md"

    try:
        diary_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    sid_short = session_id[:8] if len(session_id) > 8 else session_id

    lines = []
    lines.append(f"### {sid_short} | {time_range} | {branch} | {model}")
    if duration_min > 0:
        lines.append(f"**Duration**: {duration_min} min")
    if intent:
        lines.append(f"**Intent**: {intent}")
    if outcome:
        lines.append(f"**Outcome**: {outcome}")
    if key_files:
        lines.append(f"**Key files**: {key_files}")
    if notes:
        lines.append(f"**Notes**: {notes}")
    lines.append("")
    entry_text = "\n".join(lines)

    try:
        existing = ""
        if diary_file.exists():
            existing = diary_file.read_text(encoding="utf-8")

        if not existing.strip():
            content = f"# Session Log\n\n## {today}\n\n{entry_text}"
        else:
            date_header = f"## {today}"
            if date_header in existing:
                idx = existing.index(date_header) + len(date_header)
                while idx < len(existing) and existing[idx] == "\n":
                    idx += 1
                content = existing[:idx] + "\n" + entry_text + existing[idx:]
            else:
                if "# Session Log" in existing:
                    title_end = existing.index(
                        "\n", existing.index("# Session Log")
                    ) + 1
                else:
                    title_end = 0
                content = (
                    existing[:title_end]
                    + f"\n## {today}\n\n{entry_text}"
                    + existing[title_end:]
                )

        diary_file.write_text(content, encoding="utf-8")
    except Exception:
        pass


def cleanup_old_logs():
    """Delete JSONL log files older than 30 days."""
    if not LOG_DIR.exists():
        return
    cutoff = datetime.now() - timedelta(days=JSONL_MAX_DAYS)
    for log_file in LOG_DIR.glob("*.jsonl"):
        try:
            date_str = log_file.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                log_file.unlink()
        except Exception:
            continue


def _purge_stale_sessions(active):
    """Remove old stopped/crashed sessions beyond last 50."""
    inactive = [
        (sid, s) for sid, s in active.items()
        if s.get("status") in ("stopped", "crashed")
    ]
    if len(inactive) > 50:
        inactive.sort(
            key=lambda x: x[1].get(
                "stopped", x[1].get("crashed_at", "")
            )
        )
        for sid, _ in inactive[:-50]:
            del active[sid]
        _write_active(active)


# -- Self-Test --------------------------------------------------------------

def _self_test():
    """Run basic self-tests."""
    print("Ark Session Manager -- Self Test")
    print("=" * 40)

    # Test directory creation
    _ensure_dirs()
    assert SESSIONS_DIR.exists(), "Sessions dir not created"
    assert LOG_DIR.exists(), "Log dir not created"
    print("[PASS] Directory creation")

    # Test dynamic workspace short code generation
    cs1 = _resolve_workspace_short("D:/My-Applications/07-Carbon-Meth-Hub")
    assert len(cs1) >= 2 and cs1 == cs1.upper(), f"Bad short: {cs1}"
    print(f"[PASS] Dynamic short: 07-Carbon-Meth-Hub -> {cs1}")

    cs2 = _resolve_workspace_short("D:/My-Applications/64-CORTEX-GUI")
    print(f"[PASS] Dynamic short: 64-CORTEX-GUI -> {cs2}")

    cs3 = _resolve_workspace_short("D:/My-Applications/70-GIS-Command-Center")
    print(f"[PASS] Dynamic short: 70-GIS-Command-Center -> {cs3}")

    cs4 = _resolve_workspace_short(os.path.expanduser("~"))
    assert cs4 == "CMD", f"Expected CMD, got {cs4}"
    print(f"[PASS] Home dir -> {cs4}")

    # Test callsign generation
    callsign = get_callsign("a3f7b2c1", "D:/My-Applications/07-Carbon-Meth-Hub")
    assert "-a3f7" in callsign, f"Bad callsign: {callsign}"
    print(f"[PASS] Callsign: {callsign}")

    # Test active registry read/write
    test_data = {"test_session": {"status": "active", "callsign": "TEST-0000"}}
    _write_active(test_data)
    read_back = _read_active()
    assert read_back.get("test_session", {}).get("callsign") == "TEST-0000"
    print("[PASS] Active registry read/write")

    # Test JSONL event writing
    _write_jsonl_event({"event": "test", "ts": datetime.now().isoformat()})
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{today}.jsonl"
    assert log_file.exists(), "JSONL log not created"
    print("[PASS] JSONL event logging")

    # Test machine config loading
    config = _load_machine_config()
    if config:
        print(f"[PASS] Machine config: id={config.get('machine_id', '?')}")
    else:
        print("[SKIP] Machine config not found (optional)")

    # Clean up test data
    active = _read_active()
    active.pop("test_session", None)
    _write_active(active)

    print("=" * 40)
    print("All tests passed.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _self_test()
    else:
        print("Ark Session Manager module. Use --test for self-test.")
        print(f"Sessions dir: {SESSIONS_DIR}")
        print(f"Active file:  {ACTIVE_FILE}")
