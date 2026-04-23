---
description: Ingest saved articles into the Obsidian key-idea network
argument-hint: optional article path or batch size
---

Use `$extract-key-ideas`.

Read source Markdown from `second-brain/raw/articles/` and create the article-note, key-idea, same-idea map, writing-board, index, and log outputs described by the skill.

Do not use Python to extract ideas. If `$ARGUMENTS` gives a file, process that file. If it gives a number, process that many non-empty unprocessed articles.
