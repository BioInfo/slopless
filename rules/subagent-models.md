# Subagent Model Selection

When using the Agent tool, always pass the `model` parameter explicitly.

## Model Output Limits

- **haiku**: 8,192 tokens max output (hard model ceiling)
- **sonnet**: 16,384 tokens max output
- **opus**: 32,000 tokens max output

If a task will produce long output (audits, large code generation, comprehensive analysis),
use `sonnet` or `opus` even if the task type would normally route to haiku.

## Decision Rule

1. Simple search/read/lookup/bulk ops -> `haiku` (keep output requests short/focused)
2. Code writing, analysis, multi-step reasoning -> `sonnet` (default for most work)
3. Architectural judgment, complex tradeoffs -> `opus` (sparingly)

## Quick Reference

| Model | Best For |
|-------|----------|
| haiku | File search, cost checks, monitoring, parallel exploration |
| sonnet | Code generation, batch edits, test writing, document creation |
| opus | Architecture decisions, research synthesis, complex planning |
