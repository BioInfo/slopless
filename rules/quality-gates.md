# Quality Gates

## Verify Data Before Presenting

When output includes numbers, metrics, or technical claims:
1. Read the actual source file/database, not just memory
2. If numbers differ across files, flag the discrepancy instead of picking one
3. Never present results without verifying against source

## Verify Infrastructure Before Documenting

Before writing docs that describe something as "running" or "active":
1. Check the service is actually running (systemctl, launchctl, pgrep, etc.)
2. If not running: write as "TODO: deploy" or "planned", never as active
3. Deploy the service in the same session as writing the documentation

## Never invent data to fill a gap

**No synthetic, mock, placeholder or example data unless it was asked for.** When the
real thing is unavailable, say it is unavailable.

A fabricated value is indistinguishable from a measured one at every downstream step,
and it is worse than an error because it propagates silently and confidently. Real
examples, all the same shape: a digest that emailed `INBOX SIZE: 0` for two weeks
because the collector was dead and `|| echo 0` supplied the zero (the real count was
31); a cost report headlined $7.11 against a real invoice of $0.29, because a
correction that could not read its input let the raw meter stand.

This is not a ban on test fixtures:

- Fixtures and test inputs are fine and often required. A deliberately fictional
  command in a control suite is a test input, not a fabricated result. Use
  documentation-safe values (RFC 5737 `192.0.2.0/24`, `example.com`) so a fixture
  can never be mistaken for real infrastructure.
- A default is not data. `return []` on an error path fabricates an empty result set.
  Raise, or return a value that carries its own failure.
- An illustrative number in prose must be labelled as one, or it will be cited as
  measured within two sessions.

The test: could a reader tell this value was not measured? If not, either measure it
or do not emit it.

## Incremental Over Full

Default to incremental operations everywhere:
- Indexing: incremental (only changed files), not full reindex
- Syncs: rsync with checksums, not full copy
- Builds: incremental builds, not clean builds
- Only use full/clean when explicitly requested or when data is corrupted
