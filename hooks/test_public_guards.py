#!/usr/bin/env python3
"""Controls for the two portable hard gates: block-rm-rf.py and block-kill-pgid.py.

This is the sibling of test_hard_gates.py, scoped to the gates that carry no
local configuration. test_hard_gates.py also covers injection-guard.py, whose
allow-list names real infrastructure, so it cannot be published and neither can
its fixtures. This file exists so the two portable gates ship WITH their
controls rather than on trust.

It runs in both directions. Running only the DENY cases proves a gate catches
and says nothing about what it wrongly catches, and an over-firing gate gets
muted, which ends in the same place as no gate.

It also replays the caller's own shell history through both gates when that
history is available. A fixture guards recall; only real traffic measures
precision. When no history is present the sweep says so and is skipped, rather
than printing nothing and passing.

A control that cannot run FAILS here.

Run:  python3 test_public_guards.py
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys

HOOKS = os.path.dirname(os.path.abspath(__file__))
RM = os.path.join(HOOKS, "block-rm-rf.py")
KILL = os.path.join(HOOKS, "block-kill-pgid.py")
CORPUS = os.path.expanduser("~/.claude/projects/*/*.jsonl")

FAILURES: list[str] = []
RUN = 0


def check(name, cond, detail=""):
    global RUN
    RUN += 1
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


def verdict(hook, command):
    """deny | ask | allow."""
    payload = json.dumps(
        {"hook_event_name": "PreToolUse", "tool_name": "Bash",
         "tool_input": {"command": command}}
    )
    p = subprocess.run([sys.executable, hook], input=payload, text=True,
                       capture_output=True, timeout=20)
    out = p.stdout.strip()
    if not out:
        return "allow"
    try:
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"]
    except Exception:
        return "allow"


# ── A control that cannot run must fail, loudly ──────────────────────────────
for path in (RM, KILL):
    if not os.path.exists(path):
        print(f"FATAL: {path} not found. This control cannot run, so it fails.")
        sys.exit(2)

print("positive control: the runner can observe each verdict at all")
check("runner sees deny", verdict(RM, "rm -rf /tmp/x") == "deny")
check("runner sees allow", verdict(RM, "ls -la") == "allow")
print()

print("block-rm-rf: must DENY")
for cmd in [
    "rm -rf /tmp/build",
    "rm -fr /tmp/build",
    "rm -Rf /tmp/build",
    "rm -rfv /tmp/build",
    "sudo rm -rf /var/cache",
    "rm -r -f /tmp/x",
    "rm -f -r /tmp/x",
    "rm --recursive --force /tmp/x",
    "cd /tmp && rm -rf build",
    "make clean; rm -rf dist",
    "find . -name node_modules | xargs rm -rf",
]:
    check(f"deny: {cmd[:44]}", verdict(RM, cmd) == "deny")
print()

print("block-rm-rf: must ALLOW (precision)")
for cmd in [
    "ls -la",
    "rm file.txt",
    "rm -f stale.lock",
    "rm -r emptydir",
    "trash ~/Downloads/old",
    "git rm -r --cached .",
    "grep -rf patterns.txt src/",
    "echo 'do not rm -rf anything' >> NOTES.md",
    "docker system prune -f",
]:
    check(f"allow: {cmd[:44]}", verdict(RM, cmd) == "allow")
print()

print("block-kill-pgid: must DENY")
for cmd in [
    "kill -9 -1",
    "sudo kill -9 -1",
    "kill -9 -$PGID",
    "kill -9 -${PGID}",
    "kill -TERM -1",
]:
    check(f"deny: {cmd[:44]}", verdict(KILL, cmd) == "deny")
print()

# Documented scope: the gate matches `kill`, not `pkill`, because \bkill\b would
# otherwise fire on every `pkill -f foo`. So `pkill -g` is out of scope BY
# DESIGN. Asserting it here as an allow records the boundary rather than
# leaving a reader to assume coverage the gate does not have.
print("block-kill-pgid: must ALLOW (precision, and the documented scope edge)")
for cmd in [
    "kill 1234",
    "kill -9 1234",
    "kill -TERM 4321",
    "pkill -f myserver",
    "pkill -9 -g 0",  # out of scope by design: `kill` is matched, `pkill` is not
    "kill -0 $$",
    "echo 'kill -9 -1 is the footgun' >> NOTES.md",
]:
    check(f"allow: {cmd[:44]}", verdict(KILL, cmd) == "allow")
print()

# The bypass that made both gates decorative until 2026-08-06: a guard reading
# only the outer command string never sees the payload inside ssh or sh -c.
print("wrapper bypass: a guard must read INSIDE ssh / sh -c")
for hook, cmd in [
    (RM, 'ssh devbox "rm -rf /data"'),
    (RM, "sh -c 'rm -rf /data'"),
    (RM, 'ssh devbox "cd /srv && rm -rf cache"'),
    (KILL, 'ssh devbox "kill -9 -1"'),
    (KILL, "sh -c 'kill -9 -1'"),
]:
    check(f"deny wrapped: {cmd[:40]}", verdict(hook, cmd) == "deny")
print()

print("wrapper bypass: must not over-fire on benign wrapped commands")
for hook, cmd in [
    (RM, 'ssh devbox "ls -la /data"'),
    (RM, "sh -c 'rm stale.lock'"),
    (KILL, 'ssh devbox "kill 1234"'),
]:
    check(f"allow wrapped: {cmd[:40]}", verdict(hook, cmd) == "allow")
print()

# ── Real-traffic sweep. Precision cannot be measured on fixtures alone. ──────
# Skipped under --quick: it spawns two subprocesses per command, which is far
# too slow to sit inside a build. The build runs the directed checks; the sweep
# belongs in a manual run or a periodic health check.
QUICK = "--quick" in sys.argv
SWEEP_CAP = 800

print("real-traffic sweep (precision on the caller's own history)")
files = [] if QUICK else glob.glob(CORPUS)
if QUICK:
    print("  SKIP --quick (directed checks above still ran)")
elif not files:
    print("  SKIP no session history found at ~/.claude/projects/*/*.jsonl")
    print("       (this measures precision on real commands; fixtures above still ran)")
else:
    seen: set[str] = set()
    for f in files[:200]:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"Bash"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    for item in json.dumps(rec).split('"command":')[1:]:
                        cmd = item.strip()[1:].split('"')[0]
                        if cmd and len(cmd) < 400:
                            seen.add(cmd)
        except OSError:
            continue
        if len(seen) > SWEEP_CAP:
            break
    trips = {"block-rm-rf": [], "block-kill-pgid": []}
    swept = list(seen)[:SWEEP_CAP]
    for cmd in swept:
        if verdict(RM, cmd) == "deny":
            trips["block-rm-rf"].append(cmd)
        if verdict(KILL, cmd) == "deny":
            trips["block-kill-pgid"].append(cmd)
    dropped = max(0, len(seen) - len(swept))
    print(f"  swept {len(swept)} real commands from {len(files[:200])} session files"
          + (f" ({dropped} beyond the {SWEEP_CAP} cap not swept)" if dropped else ""))
    for gate, hits in trips.items():
        print(f"  {gate}: {len(hits)} trip(s)")
        for h in hits[:5]:
            print(f"      {h[:100]}")
    print("  This is a measurement, not an assertion. A gate that trips on ordinary")
    print("  traffic is a precision bug even when every directed case above passes.")
print()

if FAILURES:
    print(f"FAILED: {', '.join(FAILURES)}")
    sys.exit(1)
print(f"{RUN}/{RUN} directed checks passed")
