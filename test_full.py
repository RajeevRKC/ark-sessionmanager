#!/usr/bin/env python3
"""Full integration test suite for ark_session.py (deployed copy)."""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.claude/hooks"))
import ark_session as ark

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        tag = "[PASS]"
    else:
        failed += 1
        tag = "[FAIL]"
    suffix = f" -- {detail}" if detail else ""
    print(f"  {tag} {name}{suffix}")


print("=" * 50)
print("  ARK SESSION MANAGER -- FULL TEST SUITE")
print("  Source: ~/.claude/hooks/ark_session.py")
print("=" * 50)
print()

# --- 1. INFRASTRUCTURE ---
print("--- 1. INFRASTRUCTURE ---")
ark._ensure_dirs()
check("Sessions dir exists", ark.SESSIONS_DIR.exists())
check("Log dir exists", ark.LOG_DIR.exists())

config = ark._load_machine_config()
has_config = config is not None
mid = config.get("machine_id", "?") if config else "?"
check("Machine config loads", has_config, f"id={mid}")
check("get_machine_id()", ark.get_machine_id() != "unknown", ark.get_machine_id())

# --- 2. DYNAMIC SHORT CODES ---
print()
print("--- 2. DYNAMIC SHORT CODES (portable) ---")
test_cases = {
    "07-Carbon-Meth-Hub": "CMH",
    "64-CORTEX-GUI": "CG",
    "70-GIS-Command-Center": "GCC",
    "100-Aarksee-Component-Repository": "ACR",
    "38-Legal-Matters": "LM",
    "55-Bid-Tender-Contracts": "BTC",
    "80-Green-Sciences-Command-Center": "GSCC",
    "90-Programme-Command-Centre": "PCC",
    "my-cool-project": "MCP",
    "simple": "SIMP",
}
ark._ws_short_cache.clear()
for dirname, expected in test_cases.items():
    test_path = os.path.join(tempfile.gettempdir(), dirname)
    got = ark._resolve_workspace_short(test_path)
    check(f"{dirname} -> {got}", got == expected, f"expected {expected}")

ark._ws_short_cache.clear()
home_short = ark._resolve_workspace_short(os.path.expanduser("~"))
check("Home dir -> CMD", home_short == "CMD")

# --- 3. CALLSIGN GENERATION ---
print()
print("--- 3. CALLSIGN GENERATION ---")
ark._ws_short_cache.clear()
cs1 = ark.get_callsign("a3f7b2c1", os.path.join(tempfile.gettempdir(), "07-Carbon-Meth-Hub"))
check("Callsign format", "-a3f7" in cs1, cs1)

cs2 = ark.get_callsign("", os.path.join(tempfile.gettempdir(), "07-Carbon-Meth-Hub"))
check("Empty session ID fallback", "-0000" in cs2, cs2)

cs3 = ark.get_callsign("deadbeef", os.path.expanduser("~"))
check("Home callsign", cs3.startswith("CMD-"), cs3)

# --- 4. SESSION LIFECYCLE ---
print()
print("--- 4. SESSION LIFECYCLE ---")
fake_sid = "test-port-" + datetime.now().strftime("%H%M%S")
fake_cwd = os.path.join(tempfile.gettempdir(), "99-test-project")
fake_data = {
    "session_id": fake_sid,
    "cwd": fake_cwd,
    "model": {"display_name": "Opus 4.6", "id": "claude-opus-4-6"},
}

result = ark.session_start(fake_data)
check("session_start returns callsign", "callsign" in result, result["callsign"])
check("session_start returns session_id", result.get("session_id") == fake_sid)

active = ark._read_active()
check("Session in active registry", fake_sid in active)
check("Status is active", active.get(fake_sid, {}).get("status") == "active")

ok = ark.set_intent(fake_sid, "Portability test run")
check("set_intent returns True", ok is True)
active = ark._read_active()
check("Intent stored", active.get(fake_sid, {}).get("intent") == "Portability test run")

hb_data = {
    **fake_data,
    "context_window": {
        "current_usage": {
            "input_tokens": 75000,
            "cache_creation_input_tokens": 5000,
            "cache_read_input_tokens": 10000,
        },
        "context_window_size": 200000,
    },
}
hb = ark.session_heartbeat(hb_data)
check("Heartbeat returns callsign", hb is not None and "callsign" in hb)

ark.session_compact(fake_data)
active = ark._read_active()
check("Compact increments count", active.get(fake_sid, {}).get("compact_count", 0) == 1)

sessions = ark.get_active_sessions()
our_session = [s for s in sessions if s.get("session_id") == fake_sid]
check("get_active_sessions finds us", len(our_session) == 1)

stop_result = ark.session_stop({**fake_data, "stop_reason": "end_turn"})
check("session_stop returns callsign", "callsign" in stop_result)
check("session_stop returns duration", "duration_min" in stop_result)
check("session_stop returns intent", stop_result.get("intent") == "Portability test run")

active = ark._read_active()
check("Status changed to stopped", active.get(fake_sid, {}).get("status") == "stopped")

# --- 5. JSONL EVENT LOG ---
print()
print("--- 5. JSONL EVENT LOG ---")
today = datetime.now().strftime("%Y-%m-%d")
log_file = ark.LOG_DIR / f"{today}.jsonl"
check("JSONL log exists", log_file.exists())
if log_file.exists():
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    events = [json.loads(l) for l in lines if fake_sid in l]
    event_types = [e.get("event") for e in events]
    check("Start event logged", "start" in event_types)
    check("Compact event logged", "compact" in event_types)
    check("Stop event logged", "stop" in event_types)

# --- 6. CRASH DETECTION (cross-platform os.kill) ---
print()
print("--- 6. CRASH DETECTION (cross-platform os.kill) ---")
stale_sid = "crash-test-" + datetime.now().strftime("%H%M%S")
stale_time = (datetime.now() - timedelta(minutes=30)).isoformat()
active = ark._read_active()
active[stale_sid] = {
    "callsign": "TST-dead",
    "workspace": "test",
    "workspace_path": tempfile.gettempdir(),
    "branch": "main",
    "model": "test",
    "pid": 99999,
    "started": stale_time,
    "last_heartbeat": stale_time,
    "context_pct": 0,
    "compact_count": 0,
    "intent": "Crash test",
    "status": "active",
}
ark._write_active(active)

crashes = ark.detect_crashes()
found_ours = [c for c in crashes if c.get("session_id") == stale_sid]
check("Stale session detected as crash", len(found_ours) == 1)
if found_ours:
    check("Crash has intent", found_ours[0].get("intent") == "Crash test")

active = ark._read_active()
check("Crash status set", active.get(stale_sid, {}).get("status") == "crashed")

# --- 7. MEMORY BRIDGE (sweep_session) ---
print()
print("--- 7. MEMORY BRIDGE (sweep_session) ---")
test_ws = os.path.join(tempfile.gettempdir(), "ark-test-ws")
daily_dir = os.path.join(test_ws, "memory", "daily")
os.makedirs(daily_dir, exist_ok=True)

daily_file = os.path.join(daily_dir, f"{today}.md")
with open(daily_file, "w", encoding="utf-8") as f:
    f.write("# " + today + "\n\n## Notes\n")

ark.sweep_session(
    workspace_path=test_ws,
    callsign="TST-swp1",
    duration_min=25,
    intent="Testing sweep",
    compact_count=1,
)

content = Path(daily_file).read_text(encoding="utf-8")
check("Session-end marker in daily log", "[session-end]" in content)
check("Callsign in marker", "TST-swp1" in content)
check("Duration in marker", "25 min" in content)
check("Intent in marker", "Testing sweep" in content)
check("Compaction count in marker", "1 compaction" in content)

# No-op when memory dir missing
ark.sweep_session(
    workspace_path=os.path.join(tempfile.gettempdir(), "nonexistent-ws"),
    callsign="TST-noop",
    duration_min=5,
)
check("Sweep no-op when no memory dir", True)

# --- 8. DIARY ENTRY (SESSION-LOG.md) ---
print()
print("--- 8. DIARY ENTRY (SESSION-LOG.md) ---")
diary_ws = os.path.join(tempfile.gettempdir(), "ark-test-diary")
ark.write_diary_entry(
    workspace_path=diary_ws,
    callsign="TST-diry",
    session_id="diary-test-001",
    time_range="10:00-10:30",
    branch="main",
    model="Opus 4.6",
    intent="Diary test",
    outcome="All good",
    key_files="src/test.py",
    duration_min=30,
)

diary_path = Path(diary_ws) / ".claude" / "tracker" / "sessions" / "SESSION-LOG.md"
check("SESSION-LOG.md created", diary_path.exists())
if diary_path.exists():
    dc = diary_path.read_text(encoding="utf-8")
    check("Callsign in diary", "TST-diry" in dc)
    check("Intent in diary", "Diary test" in dc)
    check("Outcome in diary", "All good" in dc)
    check("Key files in diary", "src/test.py" in dc)
    check("Duration in diary", "30 min" in dc)

# --- 9. LOG CLEANUP ---
print()
print("--- 9. LOG CLEANUP ---")
# Create a fake old log
old_date = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d")
old_log = ark.LOG_DIR / f"{old_date}.jsonl"
old_log.write_text('{"event":"old"}\n', encoding="utf-8")
check("Old log created", old_log.exists())
ark.cleanup_old_logs()
check("Old log cleaned up", not old_log.exists())

# --- 10. PURGE STALE SESSIONS ---
print()
print("--- 10. PURGE STALE SESSIONS ---")
active = ark._read_active()
# Add 55 fake stopped sessions
for i in range(55):
    active[f"purge-test-{i:03d}"] = {
        "status": "stopped",
        "stopped": (datetime.now() - timedelta(hours=i)).isoformat(),
    }
ark._write_active(active)
before = len([s for s in ark._read_active().values() if s.get("status") in ("stopped", "crashed")])
ark._purge_stale_sessions(ark._read_active())
after = len([s for s in ark._read_active().values() if s.get("status") in ("stopped", "crashed")])
check("Purge keeps max 50 inactive", after <= 50, f"before={before} after={after}")

# --- CLEANUP ---
print()
print("--- CLEANUP ---")
active = ark._read_active()
for key in list(active.keys()):
    if key.startswith(("test-port-", "crash-test-", "purge-test-")):
        del active[key]
ark._write_active(active)
check("Test sessions removed from registry", True)

for d in [test_ws, diary_ws]:
    try:
        shutil.rmtree(d)
    except Exception:
        pass
check("Temp directories removed", True)

# --- RESULTS ---
print()
print("=" * 50)
print(f"  RESULTS: {passed} passed, {failed} failed")
print("=" * 50)

sys.exit(1 if failed > 0 else 0)
