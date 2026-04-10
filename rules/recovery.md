# Data Recovery & Backup

When you need to recover lost files:

1. **Check ALL backup sources in parallel:**
   - Time Machine / local snapshots
   - Git backup branches
   - Cloud sync (iCloud, OneDrive, Dropbox, Obsidian Sync)
   - Application-specific backups

2. **Understand backup lag**: Time Machine can have ~2 day lag. A backup labeled "Jan 25" may contain data from ~Jan 23.

3. **Recovery priority**: Git branches > Time Machine > Cloud sync > Application backups

4. **Disk space**: APFS snapshots hold space until backup completes. Don't panic delete.
