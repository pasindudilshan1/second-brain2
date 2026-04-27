# Second Brain - Claude Operating Rules

## Path Rule

All paths in this file are relative to the workspace root:
`C:\Users\USER\Documents\second-brain`

The actual project folder is:
`second-brain/`

Do not treat the workspace root as the project content area.
Do not write to the root-level `wiki/` folder.
The correct wiki path is always:
`second-brain/wiki/`

## Primary Skill

Use `$extract-key-ideas` when the user asks to extract ideas from articles, score article ideas, connect similar articles, create Obsidian visualization links, or build article-writing angles from saved sources.

Do not use Python for key-idea extraction. Read the Markdown articles and create the notes directly.

## Source And Output Boundaries

- Treat `second-brain/raw/articles/` as source material.
- Write generated article notes to `second-brain/wiki/article-notes/`.
- Write each reusable key idea to its own file in `second-brain/wiki/key-ideas/`.
- Write article similarity and same-idea links to `second-brain/wiki/maps/core-connections.md`.
- Write article-writing angles to `second-brain/wiki/maps/writing-board.md`.
- Keep `second-brain/wiki/index.md` and `second-brain/wiki/log.md` current.

## Folder Map

- Project instructions: `second-brain/CLAUDE.md`
- Raw article inputs: `second-brain/raw/articles/`
- Wiki home: `second-brain/wiki/`
- Article notes: `second-brain/wiki/article-notes/`
- Key ideas: `second-brain/wiki/key-ideas/`
- Maps: `second-brain/wiki/maps/`

## Allowed Support Scripts

Use scripts only for support tasks:

```bash
python sync_drive_articles.py
python sync_drive_articles.py --limit 5
python sync_drive_wiki.py
python cleanup_second_brain.py --apply
```

Do not run `extract_key_ideas.py`, `extract_keywords.py`, TF-IDF extraction, visualization scripts, or any other script to decide article ideas or generate visualizations.

## Article Note Requirements

Each processed article must have exactly five key ideas. Each idea must include:
- Obsidian link to a separate key idea page.
- Score from 0 to 100 based on that article's content.
- Brief evidence paraphrase.

Link articles together when they share the same or substantially similar key idea.
