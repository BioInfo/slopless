# Subagent Model Selection

When using the Agent tool, always pass the `model` parameter explicitly.

## The output cap is per response, and the model does not change it

**Every subagent is capped at 8,000 output tokens per response, thinking included.** Every
agent type, every model, no setting. `CLAUDE_CODE_MAX_OUTPUT_TOKENS` raises the main loop
and does not apply to subagents.

This is the opposite of the obvious mitigation. Routing a long job to a bigger model buys
nothing, and at high reasoning effort the thinking alone can exceed the cap, so the agent
dies on its first response before writing anything.

**Bound the payload, not the call count.**

- Chunk writes to roughly 4K tokens each.
- Any agent whose deliverable is source or data files gets incremental writes mandated in
  the opening brief: skeleton first, then appends of about 150 lines.
- Never tell a subagent to echo a large file back in its reply. Have it edit in place and
  return a summary plus a verification command.
- An agent with no write tool fails quietly here. A long report truncates into a short,
  plausible answer rather than an error, so brief it to deliver labelled chunks.

Reasoning effort is not free either. Drop it for mechanical producer work, keep it for
judgment.

## Decision rule

1. Simple search, read, lookup, bulk ops -> `haiku`
2. Code writing, analysis, multi-step reasoning -> `sonnet` (default for most work)
3. Architectural judgment, complex tradeoffs, anything written in your own voice -> `opus`

## Quick reference

| Model | Best for |
|-------|----------|
| haiku | File search, cost checks, monitoring, parallel exploration |
| sonnet | Code generation, batch edits, test writing, document creation |
| opus | Architecture decisions, research synthesis, complex planning |
