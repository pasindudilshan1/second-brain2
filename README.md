# Second Brain

This project turns saved Markdown articles into an Obsidian knowledge network for research, synthesis, and article writing.

The workflow is simple:

1. Put source articles in `second-brain/raw/articles/`.
2. Use the Claude command layer or the `extract-key-ideas` skill to read those articles.
3. Generate one article note per source, one reusable key-idea page per theme, and map pages for graph navigation and writing.
4. Open the vault in Obsidian to explore clusters, connections, and writing angles.

Important: Python is for support tasks only, such as Drive sync, cleanup, and graph verification. Python is not used to decide the five key ideas.

## What This System Produces

- Immutable source files in `second-brain/raw/articles/`
- Generated article notes in `second-brain/wiki/article-notes/`
- Reusable key-idea pages in `second-brain/wiki/key-ideas/`
- Connection maps in `second-brain/wiki/maps/`
- A writing board for turning research into original content

## Repo Root vs Obsidian Vault

There are two important paths in this project:

- Repo root: `C:\Users\USER\Documents\second-brain`
- Obsidian vault: `C:\Users\USER\Documents\second-brain\second-brain`

Run agent commands and Python scripts from the repo root.

Open the nested `second-brain/` folder as your Obsidian vault.

## Folder Layout

```text
C:\Users\USER\Documents\second-brain\
|-- .claude\
|   |-- commands\                  # Claude slash commands
|   `-- skills\extract-key-ideas\  # extraction skill
|-- second-brain\                  # Obsidian vault
|   |-- raw\
|   |   `-- articles\              # source markdown articles
|   `-- wiki\
|       |-- article-notes\         # one generated note per article
|       |-- key-ideas\             # one generated page per reusable idea
|       `-- maps\                  # connection maps and writing board
|-- README.md
|-- DRIVE_SYNC_SETUP.md
|-- sync_drive_articles.py
|-- cleanup_second_brain.py
`-- verify_graph_connections.py
```

## Requirements

- Obsidian
- Claude Code or another agent that can follow the project command files and extraction skill
- Python 3.10+ for support scripts
- Optional: Google Drive API credentials if you want automatic Drive sync

If you want Drive sync, install dependencies:

```powershell
py -m pip install -r requirements-drive-sync.txt
```

## End-to-End Workflow

### 1. Add source articles

Put `.md` or `.markdown` article files in:

```text
second-brain/raw/articles/
```

You can do this in two ways:

- Manual import: save or export articles as Markdown and copy them into `second-brain/raw/articles/`
- Google Drive sync: run `python sync_drive_articles.py`

Source files are treated as raw material. Do not manually rewrite them after import unless you are explicitly cleaning clutter.

### 2. Process the articles into notes and ideas

Main command options:

| Command | What it does | Example |
|---|---|---|
| `/ingest` | Ingests saved articles into the wiki network | `/ingest 5` |
| `/extract` | Extracts exactly five scored key ideas per article | `/extract 5` |
| `/sync-and-analyze` | Syncs from Drive, then processes a batch | `/sync-and-analyze 5` |
| `/insights` | Summarizes strongest themes and writing angles | `/insights AI in accounting` |
| `/visualize` | Explains how to inspect the network in Obsidian | `/visualize` |

If slash commands are not available, use the skill directly:

```text
Use $extract-key-ideas to process second-brain/raw/articles/6-finance-challenges-cfos-are-facing-today.md.
```

Extraction rules:

- The agent reads the article content directly
- Each processed article gets exactly 5 key ideas
- Each idea gets a 0-100 score based on how strongly the article supports it
- Reusable ideas are written to separate files in `second-brain/wiki/key-ideas/`
- Related articles are linked through shared idea pages and map pages

### 3. Review the generated outputs

After processing, you should see updates here:

```text
second-brain/wiki/article-notes/
second-brain/wiki/key-ideas/
second-brain/wiki/maps/core-connections.md
second-brain/wiki/maps/writing-board.md
second-brain/wiki/index.md
second-brain/wiki/log.md
```

What each output means:

- `article-notes/`: one note per source article with five ideas, evidence, related articles, and a drafting angle
- `key-ideas/`: one page per reusable concept across multiple articles
- `maps/core-connections.md`: theme clusters and article-to-article links
- `maps/writing-board.md`: thesis ideas and article angles you can write from
- `index.md`: top-level catalog of the current wiki
- `log.md`: append-only change log of processing work

### 4. Explore the network in Obsidian

Open this folder as your vault:

```text
C:\Users\USER\Documents\second-brain\second-brain
```

Then open Graph View and use this filter:

```text
path:wiki/key-ideas OR path:wiki/article-notes OR path:wiki/maps
```

If you open the repo root as the vault instead, use:

```text
path:second-brain/wiki/key-ideas OR path:second-brain/wiki/article-notes OR path:second-brain/wiki/maps
```

Recommended pages to open first:

- `second-brain/wiki/index.md`
- `second-brain/wiki/maps/core-connections.md`
- `second-brain/wiki/maps/writing-board.md`

### 5. Turn the network into writing

Typical writing flow:

1. Open `second-brain/wiki/maps/writing-board.md`
2. Pick a strong thesis or cluster
3. Open the linked key-idea page
4. Open the strongest linked article notes
5. Draft an original article using those notes as evidence

Useful prompt:

```text
Use second-brain/wiki/maps/writing-board.md and the linked key-idea pages to outline an original article about AI adoption in finance. Use only the generated wiki notes as source context.
```

### 6. Maintain the vault

Support scripts:

```powershell
python cleanup_second_brain.py
python cleanup_second_brain.py --apply
python verify_graph_connections.py
python verify_graph_connections.py --fix
python sync_drive_articles.py
```

What they do:

- `cleanup_second_brain.py`: previews clutter removal by default; `--apply` actually deletes empty placeholders, exact duplicates, and cache folders
- `verify_graph_connections.py`: checks backlinks and relationship coverage, then writes `second-brain/wiki/maps/graph-connections-report.md`
- `sync_drive_articles.py`: downloads new or updated Markdown files from Google Drive into `second-brain/raw/articles/`

## Real Examples

### Example 1: Process one specific article

Command:

```text
/extract second-brain/raw/articles/6-finance-challenges-cfos-are-facing-today.md
```

Expected outputs:

- `second-brain/wiki/article-notes/article--6-finance-challenges-cfos-are-facing-today.md`
- updated idea pages such as `second-brain/wiki/key-ideas/cfo-strategic-leadership.md`
- updated `second-brain/wiki/maps/core-connections.md`
- updated `second-brain/wiki/maps/writing-board.md`

Example result from the generated article note:

```markdown
## Five Key Ideas

1. [[cfo-strategic-leadership|CFO strategic leadership expansion]] - score: 92/100
   Evidence: Finance now sits at the intersection of cost control, digital adoption, compliance, security, and strategic planning.
```

### Example 2: Process a small batch

Command:

```text
/ingest 5
```

What happens:

- The agent selects 5 non-empty articles from `second-brain/raw/articles/`
- It creates or updates 5 article notes
- It merges overlapping ideas into shared key-idea pages
- It refreshes the map pages and wiki index

### Example 3: Sync from Google Drive and analyze

Command:

```text
/sync-and-analyze 5
```

What happens:

1. `python sync_drive_articles.py` pulls new or changed Markdown files from the configured Drive folder
2. The extraction skill processes 5 synced articles
3. The wiki and Obsidian graph become richer with new notes and links

### Example 4: Ask the system for writing direction

Command:

```text
/insights AI in accounting
```

Expected result:

- strongest idea clusters on the topic
- article notes worth opening first
- possible thesis statements
- source-backed angles for your next article

## Drive Sync Setup

Short version:

1. Install Drive dependencies with `py -m pip install -r requirements-drive-sync.txt`
2. Create a Google Cloud service account
3. Download the JSON key file
4. Save it as `credentials.json` in the repo root, or set `GOOGLE_APPLICATION_CREDENTIALS`
5. Share the target Drive folder with the service account email
6. Set `DRIVE_FOLDER_ID`
7. Run `python sync_drive_articles.py`

Detailed instructions are in `DRIVE_SYNC_SETUP.md`.

Notes:

- The sync script downloads only direct child Markdown files
- Nested folders are not traversed
- Existing local files are preserved unless the remote copy is newer

## Output Format Rules

The system is designed around these rules:

- Each processed article must produce exactly 5 key ideas
- Each reusable idea lives in its own Markdown file
- Raw articles stay in `second-brain/raw/articles/`
- Generated knowledge stays in `second-brain/wiki/`
- Obsidian wiki links such as `[[idea-slug|Readable Label]]` are used throughout
- Evidence should be paraphrased from the source, not invented

## Optional Utility Commands

The `.claude/commands/` folder also includes some utility commands:

- `/query`: answer a question using the existing wiki
- `/log`: append a timestamped note to the wiki log
- `/lint`: run a health check for broken links, orphan pages, missing frontmatter, and stale pages

These are useful after the main ingestion workflow is already working.

## Troubleshooting

### No articles are being processed

Check that:

- `second-brain/raw/articles/` contains non-empty `.md` files
- the files are readable Markdown, not login pages or bot-challenge pages
- you are pointing the command at the correct path

### Claude says the Python extractor is missing

That is expected. This repo no longer uses a Python extractor for idea generation.

Use:

```text
Use $extract-key-ideas to process the articles.
```

### Obsidian graph is too crowded

Use the filtered graph view:

```text
path:wiki/key-ideas OR path:wiki/article-notes OR path:wiki/maps
```

Then open `second-brain/wiki/maps/core-connections.md` or `second-brain/wiki/maps/writing-board.md` as your starting point instead of browsing the full graph blindly.

### Google Drive sync fails

Check:

- `credentials.json` exists or `GOOGLE_APPLICATION_CREDENTIALS` is set
- the Drive folder is shared with the service account email
- `DRIVE_FOLDER_ID` is correct
- the folder contains direct child Markdown files

### The wiki links feel incomplete

Run:

```powershell
python verify_graph_connections.py
```

Then review:

```text
second-brain/wiki/maps/graph-connections-report.md
```

## Recommended Daily Workflow

If you use this repo regularly, this is the simplest routine:

```text
/sync-and-analyze 5
/insights
```

Then in Obsidian:

1. Open `wiki/maps/writing-board.md`
2. Inspect the strongest cluster
3. Open the linked article notes
4. Draft your own original piece
