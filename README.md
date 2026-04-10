<p align="center">
  <img src="banner.png" alt="Slopless" width="100%">
</p>

<p align="center">
  <a href="https://github.com/BioInfo/slopless/stargazers"><img src="https://img.shields.io/github/stars/BioInfo/slopless?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/BioInfo/slopless/network/members"><img src="https://img.shields.io/github/forks/BioInfo/slopless?style=flat&color=blue" alt="Forks"></a>
  <a href="https://github.com/BioInfo/slopless/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Claude_Code-compatible-blueviolet" alt="Claude Code"></a>
  <a href="#"><img src="https://img.shields.io/badge/banned_words-100%2B-red" alt="Banned Words"></a>
  <a href="#"><img src="https://img.shields.io/badge/hooks-5_production-orange" alt="Hooks"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#whats-included">What's Included</a> &bull;
  <a href="#the-hooks">The Hooks</a> &bull;
  <a href="#the-anti-slop-system">Anti-Slop System</a> &bull;
  <a href="#the-statusline">The Statusline</a>
</p>

---

Production-tested Claude Code configuration from 18 months of daily use across 50+ projects. Not a tutorial. Not a summary. These are the actual config files, sanitized for sharing.

Every rule exists because Claude repeatedly made that specific mistake without it.

## Quick Start

```bash
git clone https://github.com/BioInfo/slopless.git
cd slopless

# Copy what you want (pick and choose)
cp CLAUDE.md ~/.claude/CLAUDE.md              # Behavioral guidelines
cp -r rules/ ~/.claude/rules/                  # Auto-loaded rule files
cp settings.json ~/.claude/settings.json       # Hooks, permissions, env vars
cp statusline.sh ~/.claude/statusline.sh       # 2-line neon statusline
chmod +x ~/.claude/statusline.sh
```

> **Warning**: `settings.json` includes broad permissions (`Bash(*)`, `Write(*)`, `mcp__*`). Review the `permissions` block before copying if you don't run in `--dangerously-skip-permissions` mode.

## What's Included

```
CLAUDE.md              # Core behavioral rules (coding, communication, problem solving)
settings.json          # Hooks, env vars, permissions, plugins
statusline.sh          # 2-line statusline with model, git, tokens, cost, context bar
rules/
  writing-voice.md     # Anti-AI-slop writing system (100+ banned patterns)
  subagent-models.md   # Model routing with output token limits
  quality-gates.md     # Verify before presenting, incremental over full
  operational.md       # Port conflicts, API error recovery, failure diagnosis
```

## The Hooks

The `settings.json` hooks are the highest-signal part of this repo. Five hooks that run automatically:

### 1. Auto-Lint on Every Edit

Every time Claude edits a file, the appropriate linter/formatter runs automatically:

```
JS/TS  → eslint --fix + prettier
Python → ruff check --fix + ruff format
Go     → gofmt
Rust   → rustfmt
JSON/CSS/HTML → prettier
```

No more "can you format that?" or discovering lint errors after 20 edits.

### 2. Context Reinject After Compaction

When Claude auto-compacts your conversation (at 50% context usage, configurable), it loses key instructions. This hook re-injects your project state (`CONTINUITY.md`) and `CLAUDE.md` rules back into context so Claude doesn't forget your constraints mid-session.

### 3. Current Year in Web Searches

Claude's training data cutoff means it searches for last year's information by default. This `PreToolUse` hook automatically appends the current year to any web search query that doesn't already contain a year or temporal keyword (`latest`, `recent`, `current`).

### 4. Timestamp on Every Prompt

Injects the current date and time as a system message on every prompt. Claude always knows what day and time it is.

### 5. Pre-Compaction Warning

Signals Claude that compaction is about to happen, so it can prepare to preserve key state.

## The Anti-Slop System

`rules/writing-voice.md` prevents AI-detectable writing through three layers:

### Layer 1: Banned Words (100+)

Twelve categories of words and phrases statistically overrepresented in LLM output:

| Category | Examples |
|----------|----------|
| LLM-ism verbs | delve, leverage, harness, utilize, streamline, unlock |
| LLM-ism intensifiers | crucial, vital, paramount, groundbreaking, game-changing |
| Abstract/poetic | tapestry, labyrinth, journey, narrative, nuanced |
| Stock openings | "I hope this email finds you well", "Great question" |
| Hollow enthusiasm | "I'd be happy to", "resonated", "keeps me up at night" |
| Faux-depth closers | "food for thought", "worth sitting with" |
| Mechanical transitions | furthermore, moreover, additionally, consequently |
| Hollow emphasis | "is real", "the whole game", "are exactly" |
| Performed reactions | "stopped me cold", "hit me", "struck me" |
| Algorithmic scaffolding | "The short version:", "Here's why..." |
| Faux-precision hedges | "genuinely", "I truly think" |
| Reaching for metaphors | "useful lens", "sits at the intersection of" |

### Layer 2: Structural Anti-Patterns

Detectable AI writing structures:

- **Forced contrasts** ("Not only X, but Y")
- **Rhetorical Q&A** ("So what does this mean? It means...")
- **Rule-of-three** (always listing exactly three things)
- **Uniform paragraph length** (every paragraph 3-4 sentences)
- **Paragraph-ending profundity** (dramatic upswings at paragraph ends)
- **Manufactured parallelism** (forced symmetry in consecutive sentences)

### Layer 3: Authenticity Rules

Research-backed techniques from AI text detection literature:

- **Burstiness**: Mix sentences under 8 words with sentences over 20 words
- **Paragraph variance**: Range from 1 to 7 sentences, never uniform
- **Specificity**: Ground every assertion in a concrete detail
- **Lexical diversity**: Use unexpected but precise word choices ("brittle" not "fragile")
- **No reflexive Unicode**: Arrows and decorative bullets in prose are AI tells
- **Post-draft scan**: Mandatory checklist before presenting any output

### Customization

The voice file is designed to be forked:

```
rules/writing-voice.md
  ├── Voice section (CUSTOMIZE) ── Your style, register, patterns
  ├── Banned Words (KEEP) ──────── Universal LLM-ism detection
  ├── Anti-Patterns (KEEP) ─────── Structural AI tells
  └── Authenticity (KEEP) ──────── Research-backed human-pass rules
```

## The Statusline

A 2-line statusline that shows everything you need at a glance:

```
◆ Opus4.6 │ ~/apps/myproject on main +2 !1 │ ▲ 45 ▼ 12
▓▓▓▓▓▓▓░░░░░░░░ 47% │ $0.83 │ 124.5k │ ⏱ 12m 34s │ ⏳ 2h15m
```

**Line 1**: Model (color-coded) + agent name + vim mode + directory + git branch/status + lines changed

**Line 2**: Context window bar (color shifts green→yellow→red) + cost + tokens + duration + 5-hour block timer

Features:
- Git info cached for 5s (no lag from git commands)
- Single `jq` call for all JSON parsing
- Warp terminal compatible
- Color-coded model indicator (Opus=purple, Sonnet=blue, Haiku=green)
- Context bar turns red at 80% usage

## Model Routing

`rules/subagent-models.md` prevents a common gotcha: picking the wrong model for subagent tasks and getting silently truncated output.

| Model | Max Output | Best For |
|-------|-----------|----------|
| Haiku | 8,192 tokens | File search, monitoring, lookups |
| Sonnet | 16,384 tokens | Code generation, batch edits, analysis |
| Opus | 32,000 tokens | Architecture decisions, complex planning |

## Key Settings Explained

| Setting | Value | Why |
|---------|-------|-----|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 128000 | Max output per response |
| `CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE` | 50 | Compact at 50% context (default is higher, loses more) |
| `CLAUDE_CODE_SUBAGENT_MODEL` | haiku | Cheap default for subagents, override per-task |
| `includeGitInstructions` | false | Saves ~1K tokens of default git instructions |
| `cleanupPeriodDays` | 36500 | Never auto-delete session history (100 years) |
| `USE_BUILTIN_RIPGREP` | 1 | Uses Claude's built-in ripgrep instead of system rg |

## Philosophy

**Ship your config, not advice.** This repo contains actual files from a production setup. Not a blog post about what you could do. The files you'd copy into `~/.claude/`.

**Banned patterns > positive examples.** "Don't use delve" works better than "write naturally." LLMs respond to negative constraints.

**Hooks > rules.** A hook that auto-lints on every edit is worth more than a rule that says "keep code formatted." Automate the behavior you want.

**Verify, don't trust.** Claude will confidently state that a file contains something it doesn't. The quality gates force verification before presentation.

## Contributing

Found a word or pattern that should be banned? Open an issue or PR. The banned list grows through real-world corrections. If Claude keeps producing a phrase that reads as AI-generated, it belongs here.

## License

MIT

---

<p align="center">
  <sub>Built by <a href="https://x.com/BioInfo">@BioInfo</a></sub>
</p>
