"""
Shared executor unwrapping for PreToolUse/Bash guards.

WHY THIS MODULE EXISTS
----------------------
Every Bash guard on this fleet anchors its pattern on a command boundary
(`^`, `\n`, `;`, `&`, `|`, `(`). None of those match a command name that follows
a quote, so `ssh devbox "kill -9 -1234"` matched nothing and was allowed.

`voice-bash-gate.py` had this exact hole and it was fixed there on 2026-08-05,
after the compiled pattern was run against two real WhatsApp sends and matched
neither. **The fix was never propagated to the two HARD guards**, and they are
the ones where a miss is unrecoverable. Measured 2026-08-06, before this module:

    ssh devbox "kill -9 -1234"          -> ALLOWED by block-kill-pgid.py
    ssh devbox "rm -rf /data"           -> ALLOWED by block-rm-rf.py
    exe ssh marcus-1 "sudo kill -9 -1" -> ALLOWED by both
    sh -c "kill -9 -1234"            -> ALLOWED by both
    kill -9 -1234                    -> denied (the local form, the only one covered)

The incident that bought canon P44 happened on a shared remote box. From a
session on this Mac, the only way to reach that box is an ssh wrapper, so the
guard written to prevent that incident did not cover the transport that caused
it.

WHY PEEL EXECUTORS RATHER THAN WIDEN THE BOUNDARY
-------------------------------------------------
The first repair in `voice-bash-gate.py` widened the boundary to admit any
quote, and its own control caught that as too blunt: `echo 'rm -rf /x'` names a
dangerous command as DATA and must stay allowed. An executor actually runs what
it quotes; `echo` and `printf` do not. That distinction is the discriminator,
and it is what keeps the deny and allow directions both honest.

CONTRACT
--------
`unwrap(cmd)` returns `[cmd]` plus every inner command an executor would really
run. A caller scans all of them. It never raises; on any internal error it
returns `[cmd]`, which is exactly today's behaviour, so a fault here degrades a
guard to its old scope rather than wedging Bash.
"""
import re

EXEC_RX = re.compile(
    r"""(?:^|[\n;&|(]\s*)(?:ssh|exe\s+ssh)\s+\S+\s+(?:-\S+\s+)*"""
    r"""(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)')"""
    r"""|(?:^|[\n;&|(]\s*)(?:ba|z|d|k)?sh\s+-c\s+"""
    r"""(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)')""",
    re.S,
)


def _inside_quotes(text, idx):
    """True if position idx sits inside a quoted string.

    Copied in shape from block-kill-pgid.py, which already used it to tell a
    mention from an invocation. It is needed here for the same reason and it was
    missing on the first cut of this module: the boundary class includes `(`, so
    a Python tuple in a heredoc, `(KILL, 'ssh devbox "kill -9 -1"')`, looked like a
    command boundary and the payload got peeled and denied.

    Caught within minutes of shipping, by the guard refusing to let this
    project's own write-up be written. A gate that blocks the documentation of
    the incident it guards is over-firing, and an over-firing gate gets muted.
    """
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


def unwrap(cmd):
    """[cmd] plus every inner command an executor would actually run.

    The inner capture is escape-aware. A non-greedy `(.+?)` with a backreference
    stops at the first ESCAPED quote, which silently truncated the payload in the
    voice gate until its own control caught it.

    A match that itself sits inside a quoted string is data, not an executor.
    `ssh h "rm -rf /x"` peels; `echo "ssh h \\"rm -rf /x\\""` and a Python literal
    holding the same text do not.
    """
    out = [cmd]
    try:
        for m in EXEC_RX.finditer(cmd):
            start = m.start()
            # Skip the leading boundary character the pattern consumed.
            while start < len(cmd) and cmd[start] in "\n;&|( \t":
                start += 1
            if _inside_quotes(cmd, start):
                continue
            inner = next((g for g in m.groups() if g), None)
            if inner:
                out.append(inner.replace('\\"', '"').replace("\\'", "'"))
    except Exception:
        return [cmd]
    return out
