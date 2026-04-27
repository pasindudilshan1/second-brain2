---
description: Sync the generated wiki folder to Google Drive
argument-hint: optional wiki folder path
---

Run only the wiki sync as a script:

```bash
python sync_drive_wiki.py
```

Default local folder:
- `second-brain/wiki/`

Expected behavior:
- On the first run, create or find a remote `wiki` folder in Google Drive
- Upload the full local wiki folder structure
- On later runs, upload only new files and update changed files
- Report remote-only files instead of deleting them by default

If `$ARGUMENTS` gives a folder path:
- Run `python sync_drive_wiki.py <path>`
- Sync that folder instead of the default `second-brain/wiki/`

First-run configuration:
- If the remote wiki folder already exists, set `WIKI_DRIVE_FOLDER_ID`
- Otherwise set `WIKI_DRIVE_PARENT_FOLDER_ID` so the script can create or find the remote `wiki` folder
- The resolved remote wiki folder ID is cached for later runs

Use this after extraction and mapping are done, for example after `/extract` or `/sync-and-analyze`.
