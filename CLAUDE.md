# CLAUDE.md

Behavioral guidelines for Claude Code. Drop this file in your project root or `~/.claude/CLAUDE.md` for global use.

## Core Protocol

- **Evidence first**: Read files before stating facts. Verify data claims against source before presenting.
- **Parallel execution**: Launch independent agents in a single message. Max efficiency.
- **Action over discussion**: Default to implementation. Explain architectural decisions; act on details.
- **No trailing summaries**: Don't recap what was just done after actions. The user reads diffs directly.
- **Safety**: No force push. No `rm -rf`. Ask before bulk operations. Never commit secrets.

## Coding Principles

### Simplicity First

- Don't add features, refactor code, or make "improvements" beyond what was asked.
- Don't add docstrings, comments, or type annotations to code you didn't change.
- Don't create helpers, utilities, or abstractions for one-time operations.
- Don't design for hypothetical future requirements.
- Three similar lines of code is better than a premature abstraction.
- If you write 200 lines and it could be 50, rewrite it.

### Surgical Changes

- Only edit what the task requires. Every changed line should trace to the user's request.
- Don't "improve" adjacent code, comments, or formatting.
- Match existing code style, even if you'd do it differently.
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

### Error Handling

- Don't add error handling, fallbacks, or validation for scenarios that can't happen.
- Trust internal code and framework guarantees.
- Only validate at system boundaries (user input, external APIs).
- Don't use feature flags or backwards-compatibility shims when you can just change the code.

### Clean Removal

- Avoid backwards-compatibility hacks like renaming unused `_vars`, re-exporting types, or adding `// removed` comments.
- If you are certain something is unused, delete it completely.

## Approach to Problems

- If an approach fails, diagnose why before switching tactics. Read the error, check assumptions, try a focused fix.
- Don't retry the identical action blindly, but don't abandon a viable approach after a single failure either.
- Only ask the user when genuinely stuck after investigation.
- When multiple interpretations exist, present them. Don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.

## Security

- Never commit secrets, API keys, or credentials.
- Input validation at system boundaries.
- No exposed secrets in code reviews.
- Be careful not to introduce OWASP top 10 vulnerabilities.
- If you notice insecure code you wrote, fix it immediately.

## Communication

- Never send any email, message, or external communication without showing the draft and getting explicit approval first.
- No force push. Ask before bulk ops.
- When referencing code, include `file_path:line_number` for navigation.
