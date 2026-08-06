#!/usr/bin/env python3
"""PreToolUse/Bash hard-deny for process-GROUP kills: `kill ... -<PGID>`.

Canon P44. This is a GUARD, not a nudge, and the distinction is the whole point
(P68): the rule already existed in prose, in an always-on rules file, loaded into
every session on every machine, and it did not prevent the incident.

WHAT IT COST (2026-07-12, live shared H100 box):

    for p in $(pgrep -f filler); do sudo kill -9 -$(ps -o pgid= -p $p); done

The target had reparented to init, so `ps -o pgid=` returned **1**, and
`sudo kill -9 -1` means "kill every process I can signal". The box lost another
lane's 12-hour training run, the warm-brain container, nvidia-persistenced (so
the container could not even recreate its runtime), and every tmux session.

WHAT IT BLOCKS:
  - kill -9 -1234          (literal negative pid = process group)
  - sudo kill -9 -$PGID    (unresolved: the value is exactly what bites you)
  - kill -9 -$(ps -o pgid= -p $p)
  - kill -- -1234
  - the real incident shape: `; do sudo kill -9 -$(...)`  <- shell keywords ok

WHAT IT DOES NOT BLOCK (deliberately; see block-rm-rf.py's docstring for why
this matters -- an earlier substring guard there hard-denied any command that
merely *mentioned* the dangerous string):
  - kill -9 1234          (explicit pid: THE FORM WE WANT. "The group is an
                           inference, the pids are a fact.")
  - kill -9 $PIDS
  - pkill -f foo          (`\\bkill\\b` does not match inside "pkill")
  - grep "kill -9 -1" ... / echo "... kill -9 -$PGID ..." / writing these docs
    (quote-aware: a match inside a quoted string is a mention, not a command)

FAIL-OPEN on any parse error. Never wedge Bash.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from exec_unwrap import unwrap
except Exception:
    # Degrade to the old scope rather than wedging Bash. See exec_unwrap.py.
    def unwrap(c):
        return [c]

try:
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "") or ""
except Exception:
    sys.exit(0)  # fail-open

# `kill` at a command position. Allow benign prefixes AND shell keywords, because
# the incident itself lived inside `for ...; do sudo kill ...; done` and a strict
# [;&|] anchor would have sailed straight past it.
KILL_AT_CMD_POS = re.compile(
    r"(?:^|[\n;&|(`])\s*"
    r"(?:(?:sudo|xargs|do|then|else|nohup|time|command|eval|exec)\s+(?:-\S+\s+)*)*"
    r"\bkill\b",
)
# NOT re.I, deliberately. A real shell `kill` is lowercase; `KILL` and `Kill` are
# constants and enum members. Case-insensitivity made `(KILL, 'ssh h "kill -9 -1"')`
# in a Python literal read as a command at a `(` boundary, and the guard denied
# this project's own write-up of the incident it guards. Found 2026-08-06 by the
# gate blocking a doc edit. Signal names stay reachable: `kill -KILL -1` still
# matches on the lowercase command, and -KILL is parsed as the signal it is.

# Tokens that mean "the target is a process GROUP, or is unresolved and might be".
NEG_LITERAL = re.compile(r"^-\d+$")          # -1234, and the fatal -1
NEG_UNRESOLVED = re.compile(r"^-[\$\`]")     # -$PGID, -${x}, -$(...), -`...`


def inside_quotes(text: str, idx: int) -> bool:
    """True if position idx sits inside a quoted string (a mention, not a call)."""
    single = double = 0
    i = 0
    while i < idx:
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "'" and double % 2 == 0:
            single += 1
        elif c == '"' and single % 2 == 0:
            double += 1
        i += 1
    return (single % 2 == 1) or (double % 2 == 1)


def targets_a_group(argstr: str) -> bool:
    tokens = argstr.split()
    seen_signal = False
    seen_ddash = False
    for i, tok in enumerate(tokens):
        if NEG_UNRESOLVED.match(tok):
            # `-$PGID` / `-$(...)`: the value is unknown here, and an orphan
            # resolves it to 1. This is the exact incident. Always block.
            return True
        if tok == "--":
            seen_ddash = True
            continue
        if NEG_LITERAL.match(tok):
            # A leading `-9`/`-15` is a SIGNAL, not a target. Anything negative
            # after the signal (or after `--`) is a process group.
            if seen_signal or seen_ddash or i > 0:
                return True
            seen_signal = True
            continue
        if tok.startswith("-"):
            seen_signal = True  # -TERM, -s, -KILL
            continue
    return False


def hits(text: str) -> bool:
    for m in KILL_AT_CMD_POS.finditer(text):
        if inside_quotes(text, m.start()):
            continue  # a mention in a string, not an invocation
        rest = re.split(r"[;&|\n)]", text[m.end():], 1)[0]
        if targets_a_group(rest):
            return True
    return False


# Scan the command AND every inner command an executor would really run. The
# quote-exemption above is what made `ssh devbox "kill -9 -1234"` look like a
# mention: at the outer level it IS quoted. Unwrapped, the inner command is bare
# and gets caught, while `echo "kill -9 -1"` stays exempt because echo is not an
# executor. See exec_unwrap.py.
for _candidate in unwrap(command):
    if hits(_candidate):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "BLOCKED: process-group kill (canon P44).\n\n"
                    "A `kill` with a negative target signals a process GROUP. On an "
                    "ORPHAN the pgid resolves to 1, and `kill -9 -1` kills every "
                    "process on the machine. This took out a shared box on 2026-07-12: "
                    "another lane's 12-hour training run, the container, "
                    "nvidia-persistenced, and every tmux session.\n\n"
                    "Do this instead:\n"
                    "  1. PGID=$(ps -o pgid= -p <pid> | tr -d ' ')\n"
                    "  2. Assert it: [ \"$PGID\" != 1 ] && [ \"$PGID\" != 0 ]\n"
                    "  3. List the members:  ps -eo pid,pgid,cmd | awk -v g=$PGID '$2==g'\n"
                    "  4. Kill the PIDs EXPLICITLY. The group is an inference; "
                    "the pids are a fact.\n\n"
                    "Supervised process? Killing it does nothing (the unit respawns it). "
                    "Stop AND disable the unit, then verify no process remains.\n"
                    "Killing a wrapper does not kill its children: they orphan to PPID 1 "
                    "and keep writing the files you meant to protect. Verify by cmdline."
                ),
            }
        }))
        sys.exit(2)

sys.exit(0)
