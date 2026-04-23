---
description: Extract five scored key ideas from saved articles using the project skill
argument-hint: optional article path, folder, or batch size
---

Use `$extract-key-ideas`.

Extract exactly five scored key ideas from saved Markdown articles without using Python for extraction.

Process:
1. Read the target article(s) from `second-brain/raw/articles/`.
2. Create or update article idea notes in `second-brain/wiki/article-notes/`.
3. Create or update separate key idea files in `second-brain/wiki/key-ideas/`.
4. Update `second-brain/wiki/maps/core-connections.md` with same-idea article links.
5. Update `second-brain/wiki/maps/writing-board.md`.
6. Update `second-brain/wiki/index.md` and `second-brain/wiki/log.md`.

If `$ARGUMENTS` names a file, process that file. If it gives a number, process that many non-empty articles. If no argument is given, process a small new/unprocessed batch and report the files handled.
