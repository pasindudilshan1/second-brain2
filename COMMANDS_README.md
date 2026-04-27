# Commands Guide

This file explains how to use the project commands in plain language.

## What These Commands Are

The files in `.claude/commands/` are slash-command prompts for the agent layer.

They are not terminal commands.

Use them inside your agent chat like this:

```text
/extract 5
/insights AI in finance
/query Which ideas appear most often?
```

If slash commands are not available, use the skill directly:

```text
Use $extract-key-ideas to process second-brain/raw/articles/6-finance-challenges-cfos-are-facing-today.md.
```

## Before You Start

Use this repo from the project root:

```text
C:\Users\USER\Documents\second-brain
```

Main source and output folders:

- Source articles: `second-brain/raw/articles/`
- Article notes: `second-brain/wiki/article-notes/`
- Key ideas: `second-brain/wiki/key-ideas/`
- Maps: `second-brain/wiki/maps/`

## Quick Start

If you want the simplest workflow, use this order:

1. `/sync-and-analyze 5`
2. `/insights`
3. `/visualize`
4. `/syncwiki`
5. `/query your question here`

If your articles are already local, skip sync and start with:

1. `/extract 5`
2. `/insights`
3. `/visualize`

## Command List

### `/extract`

Purpose: Read saved articles and turn them into article notes, key-idea pages, and map pages.

What it does:

- Reads from `second-brain/raw/articles/`
- Extracts exactly 5 key ideas per article
- Scores each idea from 0 to 100
- Updates article notes, key ideas, maps, index, and log

How to use it:

```text
/extract
/extract 5
/extract second-brain/raw/articles/6-finance-challenges-cfos-are-facing-today.md
```

Use it when:

- You already have article files in `raw/articles`
- You want to process one article
- You want to process a small batch

Expected outputs:

- `second-brain/wiki/article-notes/`
- `second-brain/wiki/key-ideas/`
- `second-brain/wiki/maps/core-connections.md`
- `second-brain/wiki/maps/writing-board.md`
- `second-brain/wiki/index.md`
- `second-brain/wiki/log.md`

Example usage:

```text
/extract 3
```

Meaning: Process 3 non-empty articles and generate the wiki network for them.

### `/ingest`

Purpose: Ingest saved articles into the Obsidian knowledge network.

`/ingest` is very similar to `/extract`.

Use it when you think in terms of "bring these articles into the system" rather than "extract ideas from them."

How to use it:

```text
/ingest
/ingest 10
/ingest second-brain/raw/articles/ai-as-finance-pain-reliever-tabs-cfo.md
```

Example usage:

```text
/ingest 10
```

Meaning: Process 10 unprocessed non-empty articles from `raw/articles/`.

### `/sync-and-analyze`

Purpose: Pull Markdown files from Google Drive, then analyze them with the extraction skill.

What it does:

1. Runs `python sync_drive_articles.py`
   - If you pass a number, it should run `python sync_drive_articles.py --limit N`
2. Uses `$extract-key-ideas`
3. Updates the wiki outputs

How to use it:

```text
/sync-and-analyze
/sync-and-analyze 5
/sync-and-analyze second-brain/raw/articles/the-ai-first-cfo-building-high-performance-finance-teams-in-2026.md
```

Use it when:

- Your newest article files are in Google Drive
- You want sync plus analysis in one step

Example usage:

```text
/sync-and-analyze 5
```

Meaning: Sync up to 5 newest new or updated markdown files from Google Drive, then analyze only those synced files.

### `/insights`

Purpose: Build writing ideas from the wiki that already exists.

What it does:

- Reviews article notes
- Reviews key idea pages
- Reviews connection maps
- Suggests themes, clusters, and writing angles

How to use it:

```text
/insights
/insights AI in accounting
/insights CFO volatility
/insights second-brain/raw/articles/6-finance-challenges-cfos-are-facing-today.md
```

Use it when:

- You want article ideas
- You want to know the strongest patterns
- You want a synthesis before writing

Example usage:

```text
/insights AI in accounting
```

Meaning: Summarize the strongest AI-related idea clusters and suggest writing angles from the wiki.

### `/syncwiki`

Purpose: Upload the generated wiki folder to Google Drive and sync later changes.

What it does:

- Runs `python sync_drive_wiki.py`
- Uses `second-brain/wiki/` by default
- On the first run, creates or finds a remote `wiki` folder in Drive
- Uploads new files and updates changed files on later runs
- Leaves remote-only files untouched unless you run the script manually with `--delete-removed`

How to use it:

```text
/syncwiki
/syncwiki second-brain/wiki
```

Use it when:

- Extraction and mapping are already done
- You want the generated wiki backed up or shared through Google Drive
- You want later runs to sync only wiki updates

Example usage:

```text
/syncwiki
```

Meaning: Sync the current `second-brain/wiki/` folder to the configured Google Drive location.

### `/query`

Purpose: Ask a question and get an answer based only on the wiki.

What it does:

- Reads `wiki/index.md`
- Reads the most relevant wiki pages
- Synthesizes an answer
- Cites claims using wiki page names

How to use it:

```text
/query Which ideas connect CFO leadership and AI adoption?
/query What are the biggest hiring themes in the current wiki?
/query Which pages mention regulatory pressure most often?
```

Use it when:

- You want a wiki-grounded answer
- You want to compare themes already in the vault
- You want to avoid rereading many pages manually

Example usage:

```text
/query Which key ideas are strongest across the current wiki?
```

Meaning: Read the existing wiki and answer from the pages already generated.

### `/visualize`

Purpose: Show how to inspect the network in Obsidian Graph View.

What it does:

- Explains the graph workflow
- Gives you the recommended graph filter
- Does not run Python

How to use it:

```text
/visualize
```

Recommended filter:

```text
path:second-brain/wiki/key-ideas OR path:second-brain/wiki/article-notes OR path:second-brain/wiki/maps
```

Use it when:

- You want to explore the wiki visually
- You want to see which idea pages are central hubs

### `/log`

Purpose: Add a timestamped note to the wiki log.

What it does:

- Appends a note to `wiki/log.md`
- Checks whether related existing pages should mention that note
- Does not create brand-new pages

How to use it:

```text
/log Processed a batch of AI and CFO articles today.
/log Need to compare regulatory-change pages against hiring-theme pages.
```

Use it when:

- You want to track progress
- You want to capture a research note
- You want a dated trail of decisions

Example usage:

```text
/log The April batch shows AI adoption and talent shortage appearing together often.
```

### `/lint`

Purpose: Run a wiki health check.

What it checks:

- Broken wiki links
- Orphan pages
- Missing frontmatter
- Stale pages
- Contradictions between pages

How to use it:

```text
/lint
```

Important:

- This command reports issues first
- It should not fix anything until you confirm

Use it when:

- The wiki feels messy
- You want to audit link quality
- You want to check consistency before writing

## Best Command For Each Task

- Need new content from Drive: `/sync-and-analyze`
- Articles already local: `/extract` or `/ingest`
- Want to push the generated wiki to Drive: `/syncwiki`
- Need writing ideas: `/insights`
- Need answers from the wiki: `/query`
- Need graph instructions: `/visualize`
- Need a progress note: `/log`
- Need a quality check: `/lint`

## Example Workflows

### Workflow 1: Fresh start from Drive

```text
/sync-and-analyze 5
/syncwiki
/insights
/visualize
```

### Workflow 2: Process one specific article

```text
/extract second-brain/raw/articles/6-finance-challenges-cfos-are-facing-today.md
/query What are the 5 ideas from this article?
```

### Workflow 3: Write a new article from the wiki

```text
/insights AI in finance
/query Which article notes best support that thesis?
```

### Workflow 4: Audit the wiki before a bigger batch

```text
/lint
/log Preparing to clean weak links before the next ingest batch.
```

## Terminal Scripts vs Slash Commands

Use slash commands for analysis and synthesis.

Use Python scripts only for support tasks:

```powershell
python sync_drive_articles.py
python sync_drive_articles.py --limit 5
python sync_drive_wiki.py
python sync_drive_wiki.py --delete-removed
python cleanup_second_brain.py
python cleanup_second_brain.py --apply
python cleanup_second_brain.py --reset-wiki
python cleanup_second_brain.py --reset-wiki --apply
python verify_graph_connections.py
python verify_graph_connections.py --fix
```

Simple rule:

- Use slash commands to think
- Use Python scripts to maintain files

## If Slash Commands Are Not Available

Use direct prompts like these:

```text
Use $extract-key-ideas to process 5 new articles from second-brain/raw/articles/.
```

```text
Use $extract-key-ideas to process second-brain/raw/articles/ai-as-finance-pain-reliever-tabs-cfo.md.
```

```text
Use second-brain/wiki/maps/writing-board.md and second-brain/wiki/key-ideas/ to suggest three article angles about AI adoption in finance.
```

## Notes

- Key-idea extraction should come from reading the article text, not from Python extraction scripts.
- Each processed article should produce exactly 5 key ideas.
- Raw article files should stay in `second-brain/raw/articles/`.
- Generated knowledge should stay in `second-brain/wiki/`.
