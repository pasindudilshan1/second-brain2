---
description: Sync Drive articles, then analyze them with the key-idea skill
argument-hint: optional batch size or article path
---

Run only the Drive sync as a script:

```bash
python sync_drive_articles.py
```

After sync completes, use `$extract-key-ideas` to read the synced Markdown articles and create the Obsidian idea network. Do not use Python for key-idea extraction.

Expected outputs:
- `second-brain/wiki/article-notes/`
- `second-brain/wiki/key-ideas/`
- `second-brain/wiki/maps/core-connections.md`
- `second-brain/wiki/maps/writing-board.md`
- `second-brain/wiki/index.md`
- `second-brain/wiki/log.md`

If `$ARGUMENTS` gives a batch size:
- Run `python sync_drive_articles.py --limit N`
- Sync only the newest `N` new or updated markdown files from Google Drive
- Process only the files that were downloaded or updated by that sync
- If fewer than `N` files changed, process only the changed files
- If no files changed, report that and do not process unrelated local articles

If `$ARGUMENTS` gives a file path, run the normal sync and then process that file.

If no argument is given, run the normal sync and then process a small new or unprocessed batch. Report exactly which files were handled.
