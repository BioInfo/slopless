# Security Rules

- No force push. No `rm -rf` (use `trash` or safer alternatives). Ask before bulk ops.
- Never commit secrets, API keys, or credentials.
- Store API keys in a secrets manager (pass, Keychain, Vault), not plaintext files.
- Never store API keys in `.env` files committed to git or hardcoded in scripts.
- No exposed secrets in code reviews.
- Input validation at system boundaries.
