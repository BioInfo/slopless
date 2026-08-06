#!/usr/bin/env python3
"""PreToolUse/Bash hard-deny for `rm -rf` (use `trash`).

Matches `rm` invoked AS A COMMAND (at a command boundary) with recursive+force
flags. Anchoring on command position is the whole point: the old substring
check (`'rm -rf' in command`) hard-DENIED any command that merely *contained*
the text "rm -rf" — `grep "rm -rf"`, `echo "...rm -rf..."`, a heredoc/learnings
note discussing it — none of which delete anything. This version still blocks
real invocations (rm -rf, rm -fr, rm -Rf, sudo rm -rf, `&& rm -rf`, rm -r -f,
rm --recursive --force, find|xargs rm -rf) while letting string mentions pass.

FAIL-OPEN on parse error (never wedge Bash). This is the hard-deny layer;
injection-guard.py is the ask-layer sibling.
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

# Command boundary: start-of-string, newline, or after ; & | ( (covers && ||).
# Optional benign prefixes (sudo / xargs[-flags]). Then rm with recursive+force
# in any of the common spellings.
RM_RF = re.compile(
    r"(?:^|[\n;&|(])\s*"
    r"(?:sudo\s+)?(?:xargs\s+(?:-\S+\s+)*)?(?:sudo\s+)?"
    r"\brm\s+"
    r"(?:"
        r"-[a-z]*r[a-z]*f[a-z]*"               # -rf, -Rf, -rfv, -vrf ...
        r"|-[a-z]*f[a-z]*r[a-z]*"              # -fr, -vfr ...
        r"|-r[a-z]*\s+-[a-z]*f"                # -r -f  (separate)
        r"|-f[a-z]*\s+-[a-z]*r"                # -f -r  (separate)
        r"|--recursive\b[^\n;&|]*?--force\b"   # --recursive ... --force
        r"|--force\b[^\n;&|]*?--recursive\b"   # --force ... --recursive
    r")",
    re.I,
)

if any(RM_RF.search(c) for c in unwrap(command)):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "rm -rf is not allowed. Use the `trash` command instead for "
                "safe deletion."
            ),
        }
    }))
    sys.exit(2)

sys.exit(0)
