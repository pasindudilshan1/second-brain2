# Second Brain - Claude Operating Rules

## Primary Skill

Use `$extract-key-ideas` when the user asks to extract ideas from articles, score article ideas, connect similar articles, create Obsidian visualization links, or build article-writing angles from saved sources.

Do not use Python for key-idea extraction. Read the Markdown articles and create the notes directly.

## Source And Output Boundaries

- Treat `raw/articles/` as source material.
- Write generated article notes to `wiki/article-notes/`.
- Write each reusable key idea to its own file in `wiki/key-ideas/`.
- Write article similarity and same-idea links to `wiki/maps/core-connections.md`.
- Write article-writing angles to `wiki/maps/writing-board.md`.
- Keep `wiki/index.md` and `wiki/log.md` current.

## Allowed Support Scripts

Use scripts only for support tasks:

```bash
python sync_drive_articles.py
python sync_drive_articles.py --limit 5
python cleanup_second_brain.py --apply
```

Do not run `extract_key_ideas.py`, `extract_keywords.py`, TF-IDF extraction, visualization scripts, or any other script to decide article ideas or generate visualizations.

## Article Note Requirements

Each processed article must have exactly five key ideas. Each idea must include:
- Obsidian link to a separate key idea page.
- Score from 0 to 100 based on that article's content.
- Brief evidence paraphrase.

Link articles together when they share the same or substantially similar key idea.
