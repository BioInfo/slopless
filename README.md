<p align="center">
  <img src="banner.png" alt="Slopless" width="100%">
</p>

<p align="center">
  <a href="https://github.com/BioInfo/slopless/stargazers"><img src="https://img.shields.io/github/stars/BioInfo/slopless?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/BioInfo/slopless/network/members"><img src="https://img.shields.io/github/forks/BioInfo/slopless?style=flat&color=blue" alt="Forks"></a>
  <a href="https://github.com/BioInfo/slopless/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Claude_Code-compatible-blueviolet" alt="Claude Code"></a>
  <a href="#"><img src="https://img.shields.io/badge/principles-78-informational" alt="Principles"></a>
  <a href="#"><img src="https://img.shields.io/badge/banned_words-100%2B-red" alt="Banned Words"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#the-method">The Method</a> &bull;
  <a href="#the-config">The Config</a> &bull;
  <a href="#the-hooks">The Hooks</a> &bull;
  <a href="#the-anti-slop-system">Anti-Slop</a> &bull;
  <a href="#read-this-before-you-copy-anything">Read First</a>
</p>

---

Production-tested Claude Code configuration from 18 months of daily use across 50+ projects. Not a tutorial. Not a summary. These are the actual files, generated from a live setup and sanitized for sharing.

Two layers, useful at different depths.

**The method.** 78 numbered principles for working with an agent that can be wrong confidently. Cite them in a review or a design doc without adopting any of the tooling. Every one was bought by a specific failure.

**The config.** The files you copy into `~/.claude/`. Rules, hooks, settings, statusline.

## Read this before you copy anything

The most useful thing in this repo may be the reason to copy less of it than you expect.

In July 2026 Anthropic [removed over 80% of Claude Code's own system prompt](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) for Opus 5 and Fable 5, with no measurable loss on their coding evals. Their finding was that they had been overconstraining the model, and that on this generation the constraints cost more than they bought. Their guidance now: let the model use judgement, design interfaces instead of writing examples, and load context progressively rather than stuffing it all into one file.

There is a matching result in the other direction. Anthropic's April 2026 postmortem cost about 3% across evals by **adding a single brevity instruction** to that same system prompt. The instruction told Claude to keep responses short. What it actually suppressed was caveats: the model still found the problems and then judged them below the stated bar, so output got shorter, cleaner, and more confident while the warning you needed went missing.

Both results point the same way. **A standing rule is expensive and it is not free to add.** So:

- Prefer a hook to a rule. A hook fires; a paragraph hopes.
- Prefer a skill to a paragraph in `CLAUDE.md`. Skills load when relevant.
- Spend your `CLAUDE.md` budget on **gotchas a reader could not infer from the repo**, not on restating good practice.
- Audit for contradictions. Overlapping, conflicting instructions across your system prompt, skills and `CLAUDE.md` make the model burn reasoning reconciling them before it starts.
- Run `/doctor` in a Claude Code session. Anthropic built it to rightsize exactly these files.

Take the pieces here that solve a problem you actually have. Copying all of it wholesale is the failure mode this section is about.

## Quick Start

```bash
git clone https://github.com/BioInfo/slopless.git
cd slopless

# Pick and choose. Do not copy all of it by reflex.
cp rules/writing-voice.md ~/.claude/rules/     # anti-slop writing system
cp -r hooks/ ~/.claude/hooks/                  # the two hard guards
cp statusline.sh ~/.claude/statusline.sh && chmod +x ~/.claude/statusline.sh
```

`settings.json` is included as a reference, not a recommendation. It grants `Bash(*)`, `Write(*)` and `mcp__*` with `defaultMode: acceptEdits`, which suits a personal machine and is a poor fit for a managed work laptop. Read the `permissions` block before adopting any of it.

## The Method

| File | What it is |
|---|---|
| `PRINCIPLES.md` | All 78 principles, one line each. The reference card. |
| `METHOD.md` | The full canon, grouped into ten sections, with the reasoning. |
| `PREFLIGHT.md` | The checklists. What to run before you act, before you believe a result, before a claim leaves the session, before you publish. |

One sentence holds most of it:

> **An instrument that cannot fail certifies whatever you point it at.**

That is the shape of nearly every expensive mistake here. A dry run that prints nothing and exits zero. A freshness check reading a timestamp its own producer wrote. A test that type-checks a field nobody reads. A scan whose zero result was never positive-controlled. In each case the check ran, passed, and told you nothing, which is worse than no check because now you believe something.

The second sentence is about documents like this one:

> **Passive text loses to habit. A principle with no artifact has no enforcement.**

Which is why the hooks below matter more than the rules.

## The Config

```
PRINCIPLES.md          # 78 principles, one line each
METHOD.md              # the full canon
PREFLIGHT.md           # the checklists
rules/
  writing-voice.md     # anti-AI-slop writing system (100+ banned patterns)
  subagent-models.md   # the subagent output cap and what to do about it
  quality-gates.md     # verify before presenting, incremental over full
  operational.md       # port conflicts, API error recovery, failure diagnosis
hooks/
  block-rm-rf.py       # hard deny on rm -rf
  block-kill-pgid.py   # hard deny on the kill -9 -$PGID footgun
  exec_unwrap.py       # shared: unwraps ssh / sh -c so guards see the payload
  test_public_guards.py # controls for both guards, in both directions
settings.json          # reference only, read the permissions block
statusline.sh          # 2-line statusline with model, git, tokens, cost, context
```

## The Hooks

A rule is advice. A hook is a mechanism. These two are hard denies on `PreToolUse`, and they exist because both mistakes are unrecoverable.

**`block-rm-rf.py`** denies `rm -rf` in every spelling: `-rf`, `-fr`, `-Rf`, `-r -f`, `--recursive --force`, and after a `&&` or `;` or `|`.

**`block-kill-pgid.py`** denies `kill -9 -<pgid>`. The failure it prevents: on an orphaned process the PGID resolves to `1`, and `sudo kill -9 -1` kills every process on the machine. It is scoped to `kill` and deliberately does not match `pkill`, which would fire on every ordinary `pkill -f`.

**`exec_unwrap.py`** is the piece most guards are missing. A `PreToolUse` hook that reads only the outer command string never sees the payload inside a wrapper, so `ssh host "rm -rf /data"` and `sh -c 'kill -9 -1'` walk straight past a guard that looks correct. Both guards here unwrap first and scan the innermost payload.

**`test_public_guards.py`** runs 42 directed checks in both directions, then replays your own shell history through both gates. That second part is the one people skip: running only the deny cases proves a gate catches something and says nothing about what it wrongly catches, and an over-firing gate gets switched off, which lands in the same place as no gate at all. A fixture measures recall. Only real traffic measures precision.

```bash
python3 hooks/test_public_guards.py          # full, includes the traffic sweep
python3 hooks/test_public_guards.py --quick  # directed checks only
```

Wire them in `settings.json` under `hooks.PreToolUse` with matcher `Bash`.

## The Anti-Slop System

`rules/writing-voice.md` prevents AI-detectable writing through three layers.

**Banned words and phrases**, in twelve categories: LLM verbs (delve, leverage, utilize), hollow intensifiers (crucial, robust, seamless), abstract poetry (tapestry, journey, landscape), stock openings, performed reactions, faux-depth closers, mechanical transitions, and the rest.

**Structural anti-patterns.** Forced contrasts ("not only X, but Y"), rhetorical question scaffolding, reflexive rule-of-three, uniform paragraph length, dramatic upswings at paragraph ends, manufactured parallelism.

**Authenticity rules**, drawn from AI-text-detection research. Vary sentence length aggressively, at least one under 8 words and one over 20 per paragraph. Vary paragraph length from 1 to 7 sentences. Ground every assertion in something concrete. Pick words by connotation rather than probability.

The file is built to be forked: replace the voice section with your own patterns, keep the banned lists and anti-patterns, which are not personal.

## Model Routing

`rules/subagent-models.md` covers a gotcha that costs people a lot of time: **every subagent is capped at 8,000 output tokens per response, thinking included, on every model.** There is no setting for it, and `CLAUDE_CODE_MAX_OUTPUT_TOKENS` does not apply to subagents.

The obvious mitigation is the wrong one. Routing a long job to a bigger model buys no headroom, and at high reasoning effort the thinking alone can blow the cap, so the agent dies on its first response before writing anything. Bound the payload instead: chunk writes to roughly 4K tokens, mandate incremental appends for file deliverables, and never ask a subagent to echo a large file back in its reply.

| Model | Best for |
|-------|----------|
| Haiku | File search, monitoring, lookups |
| Sonnet | Code generation, batch edits, analysis |
| Opus | Architecture decisions, complex planning |

## The Statusline

```
◆ Opus5 │ ~/apps/myproject on main +2 !1 │ ▲ 45 ▼ 12
▓▓▓▓▓▓▓░░░░░░░░ 47% │ $0.83 │ 124.5k │ ⏱ 12m 34s │ ⏳ 2h15m
```

Line 1 is model, agent, vim mode, directory, git branch and status, lines changed. Line 2 is the context bar (green to yellow to red), cost, tokens, duration, and the 5-hour block timer. Git info is cached for 5 seconds, all JSON parsing is a single `jq` call, and it renders correctly in Warp.

## How this repo stays current

It is generated from a live `~/.claude`, not maintained by hand. A build script applies a reviewable list of transforms, then runs a deny-list scan that **fails the build** rather than stripping and continuing, because a silent strip produces a clean-looking artifact. The scanner is positive-controlled against planted strings on every run, the principle index is validated against the canon's own numbering, and the shipped guards must pass their controls after transformation before anything is written.

It still went four months stale once, which is why there is now a drift check as well.

## Philosophy

**Ship your config, not advice.** Actual files from a working setup.

**Hooks over rules.** A hook that fires beats a paragraph that hopes. Where a principle can be code, it should be code, because code is the only layer that cannot forget.

**Controls in both directions.** A gate tested only on the cases it should catch is half a control.

**Fewer standing instructions than you think.** See [the section above](#read-this-before-you-copy-anything). The vendor cut 80% of theirs.

## Contributing

Found a word or pattern that should be banned? Open an issue or PR. The list grows through real corrections.

## License

MIT

---

<p align="center">
  <sub>Built by <a href="https://x.com/builderleader">@builderleader</a></sub>
</p>
