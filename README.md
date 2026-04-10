# Slopless

Production-tested configuration for Claude Code. Drop-in `CLAUDE.md` and rules that make Claude write better code and more human text.

Built from 18 months of daily Claude Code use across 50+ projects, 134 skills, and 8 autonomous agents.

## What's in the box

```
CLAUDE.md                        # Core behavioral guidelines
rules/
  writing-voice.md               # Anti-AI-slop writing system
  subagent-models.md             # Model routing (haiku/sonnet/opus)
  quality-gates.md               # Verify before presenting
  security.md                    # Safety constraints
  operational.md                 # Port conflicts, error recovery
  data-processing.md             # Dedup, timestamps, batching
  recovery.md                    # Backup and recovery procedures
```

## Quick Start

**Global (all projects):**
```bash
cp CLAUDE.md ~/.claude/CLAUDE.md
cp -r rules/ ~/.claude/rules/
```

**Per-project:**
```bash
cp CLAUDE.md ./CLAUDE.md
```

## What each file does

### CLAUDE.md

Core behavioral guidelines that prevent the most common Claude Code mistakes:
- Don't add features beyond what was asked
- Don't create abstractions for one-time operations
- Don't add error handling for impossible scenarios
- Make surgical changes, touch only what you must
- Read files before stating facts about them
- Never commit secrets

### rules/writing-voice.md

The anti-slop system. A comprehensive banned word list plus structural rules that prevent AI-detectable writing patterns:

- 100+ banned LLM-ism words and phrases across 12 categories
- Structural anti-patterns (forced contrasts, rhetorical Q&A, uniform paragraph length)
- Authenticity rules based on AI detection research (burstiness, lexical diversity, specificity)
- Post-draft scanning checklist
- Customizable voice section (replace with your own style)

### rules/subagent-models.md

How to route work across Claude's model tiers. Haiku for lookups, Sonnet for code, Opus for architecture. Includes output token limits that will silently truncate your results if you pick the wrong model.

### rules/quality-gates.md

Verification discipline: verify data before presenting, verify infrastructure before documenting, default to incremental operations.

### rules/security.md

Safety constraints: no force push, no `rm -rf`, secrets in a manager not plaintext, input validation at boundaries.

### rules/operational.md

Prevent port conflicts, recover from API auth errors, diagnose failures before retrying.

## Philosophy

**1. Rules over hope.** Don't hope Claude will write clean code. Tell it what clean means. Be specific about what to avoid.

**2. Banned patterns > positive examples.** It's more effective to ban "delve" and "leverage" than to say "write naturally." LLMs need negative constraints more than positive ones.

**3. Layer your config.** Global `CLAUDE.md` for universal rules. Per-project `CLAUDE.md` for project-specific patterns. `~/.claude/rules/` for behavioral files that auto-load every session.

**4. Verify, don't trust.** Claude will confidently state that a file contains something it doesn't. The quality gates force verification before presentation.

## Customization

The writing voice file is designed to be forked. The top section (voice pillars, register ladder, lexicon) should be replaced with your own patterns. The bottom section (banned words, anti-patterns, authenticity rules) is universal and should be kept as-is.

## Background

These rules evolved from daily production use of Claude Code. The banned words list started at 20 entries and grew to 100+ through iterative corrections. Each rule exists because Claude repeatedly made that specific mistake without it.

The authenticity rules are based on published research on AI text detection, linguistic analysis of human vs LLM text burstiness, and practical experience with what gets flagged by readers and detection tools.

## License

MIT
