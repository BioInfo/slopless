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

## Incremental Over Full

Default to incremental operations everywhere:
- Indexing: incremental (only changed files), not full reindex
- Syncs: rsync with checksums, not full copy
- Builds: incremental builds, not clean builds
- Only use full/clean when explicitly requested or when data is corrupted
