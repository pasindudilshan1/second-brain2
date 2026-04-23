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

If `$ARGUMENTS` gives a batch size, process that many non-empty articles after sync. If no argument is given, process a small new/unprocessed batch and report exactly which files were handled.
