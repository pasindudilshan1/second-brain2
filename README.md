# Second Brain

Simple local setup guide for this project:

- Git repo: `https://github.com/pasindudilshan1/second-brain2.git`
- Main goal: save Markdown articles, turn them into connected notes, then explore them in Obsidian
- Best setup on Windows: `Git + Python + Obsidian + Claude Code`
- Optional: `Ollama` if you want to run Claude Code with local/open models

## What This Project Does

This repo helps you build a small knowledge system from articles.

You put Markdown article files into the vault.

Then the agent reads them and creates:

- one note for each article
- reusable key-idea pages
- map pages that connect related ideas
- a writing board for article ideas

This project has two important folders:

- Repo root: this folder, where the scripts and `README.md` live
- Obsidian vault: `second-brain/`

Use scripts and terminal commands from the repo root.

Open the nested `second-brain/` folder inside Obsidian.

## Folder Layout

```text
second-brain/
|-- .claude/                       # Claude commands and skill instructions
|-- second-brain/                  # Obsidian vault
|   |-- raw/articles/              # source Markdown articles
|   `-- wiki/                      # generated notes, ideas, maps
|-- sync_drive_articles.py         # Google Drive -> raw/articles sync
|-- cleanup_second_brain.py        # cleanup utility
|-- verify_graph_connections.py    # link/report utility
|-- requirements-drive-sync.txt    # Python packages for Drive sync
`-- README.md
```

## Quick Start

If you want the shortest path, follow these steps in order:

1. Install `Git for Windows`
2. Install `Python 3.10+`
3. Install `Obsidian`
4. Install `Claude Code`
5. Optional: install `Ollama`
6. Clone this repo
7. Put `credentials.json` in the repo root if you want Google Drive sync
8. Open `second-brain/` as your Obsidian vault
9. Run `/extract 5` or `/sync-and-analyze 5` inside Claude Code

## 1. Clone The Repo

Open PowerShell and run:

```powershell
cd $HOME\Documents
git clone https://github.com/pasindudilshan1/second-brain2.git second-brain
cd second-brain
```

If you want it in a different location, clone anywhere you like. Just remember that the repo root is the folder that contains `README.md`.

## 2. Install Python Packages

Python is only needed for support scripts like Google Drive sync, cleanup, and graph checks.

From the repo root run:

```powershell
py -m pip install -r requirements-drive-sync.txt
```

This installs:

- `google-auth`
- `google-auth-oauthlib`
- `google-api-python-client`

## 3. Install Claude Code

This repo is designed around the `.claude/commands/` folder and the `extract-key-ideas` skill, so `Claude Code` is the main way to use it.

### Windows install

The simplest Windows command is:

```powershell
winget install Anthropic.ClaudeCode
```

If you prefer Anthropic's installer:

```powershell
irm https://claude.ai/install.ps1 | iex
```

After install, close and reopen PowerShell, then verify:

```powershell
claude --version
claude doctor
```

To start Claude Code in this repo:

```powershell
cd C:\Users\USER\Documents\second-brain
claude
```

When Claude opens, sign in and then use project commands like:

```text
/extract 5
/sync-and-analyze 5
/insights
/visualize
```

Important:

- Native Windows Claude Code needs `Git for Windows` installed
- The free Claude.ai plan does not include Claude Code access
- If `claude` is not recognized, reopen the terminal after installation

## 4. Optional: Install Ollama

You do not need Ollama to use this repo.

Use Ollama only if you want Claude Code to run with local or Ollama-provided open models.

### What Ollama does here

Ollama does not replace the repo workflow.

It only gives Claude Code a different model backend.

The repo still uses:

- `.claude/commands/`
- `.claude/skills/`
- your local project files

### Install Ollama on Windows

Download and install Ollama from the official Windows page:

- `https://ollama.com/download/windows`

After install, reopen PowerShell and test it:

```powershell
ollama
```

Or test with a small model:

```powershell
ollama run llama3.2
```

If this works, Ollama is installed correctly.

### Use Ollama with Claude Code

First make sure `Claude Code` is already installed.

Then run:

```powershell
ollama launch claude
```

Ollama will guide you to:

- choose a model
- configure Claude Code
- launch Claude Code

If you want to choose the model directly:

```powershell
ollama launch claude --model qwen3.5
```

Good starting models for coding from Ollama's documentation:

- `qwen3.5`
- `glm-4.7-flash`

If you only want to chat with a model first, not launch Claude Code:

```powershell
ollama run llama3.2
```

## 5. Optional: Claude Desktop

If you prefer an app window instead of terminal-first usage, you can install Claude Desktop:

- official help page: `https://support.claude.com/en/articles/10065433-install-claude-desktop`

But for this repo, `Claude Code` is the better fit because the workflow uses slash commands and the `.claude/` project instructions.

## 6. Put The Credential File In The Root Folder

If someone sent you the Google credential JSON file through WhatsApp, do this carefully.

The file must end up here:

```text
C:\Users\USER\Documents\second-brain\credentials.json
```

This is the recommended location because `sync_drive_articles.py` checks the repo root first.

### Simple method using File Explorer

1. Download the JSON file from WhatsApp Web or WhatsApp Desktop to your computer
2. Open the download folder
3. Make sure the filename is exactly `credentials.json`
4. Copy the file
5. Open this folder:

```text
C:\Users\USER\Documents\second-brain
```

6. Paste the file there

### PowerShell method

If the file is in `Downloads` and is named something else, copy and rename it in one step:

```powershell
Copy-Item "$HOME\Downloads\your-file-name.json" "C:\Users\USER\Documents\second-brain\credentials.json"
```

### Very important checks

- The file must be a real `.json` file, not `.txt`
- The name should be exactly `credentials.json`
- Put the file in the repo root, not inside `.obsidian`
- Do not paste the JSON text inside `README.md` or another file
- Do not commit this file to Git

Alternative location:

- `C:\Users\USER\Documents\second-brain\second-brain\credentials.json`

But root is better and simpler.

## 7. Google Drive Sync Setup

If you want to pull articles from Google Drive into `second-brain/raw/articles/`, you need:

1. a Google service account JSON key
2. the Drive folder shared with that service account email
3. a Drive folder ID

The sync script reads credentials from:

- `credentials.json` in the repo root
- or `second-brain/credentials.json`
- or `GOOGLE_APPLICATION_CREDENTIALS`

### Set the Drive folder ID for the current PowerShell session

```powershell
$env:DRIVE_FOLDER_ID="YOUR_FOLDER_ID_HERE"
```

Then run:

```powershell
python sync_drive_articles.py
python sync_drive_articles.py --limit 5
```

What the script does:

- connects to the Drive folder
- downloads direct child `.md` and `.markdown` files
- saves them into `second-brain/raw/articles/`
- skips local files that are already up to date
- with `--limit N`, syncs only the newest `N` new or updated markdown files

Note:

- Nested folders are not scanned
- The target Drive folder must be shared with the service account email

## 8. Open The Vault In Obsidian

Open this folder as your Obsidian vault:

```text
C:\Users\USER\Documents\second-brain\second-brain
```

Do not open the repo root as the main vault unless you know why you are doing it.

Recommended graph filter:

```text
path:wiki/key-ideas OR path:wiki/article-notes OR path:wiki/maps
```

## 9. Add Or Sync Articles

You can bring article files into the project in two ways.

### Option A: Add files manually

Put your Markdown files here:

```text
second-brain/raw/articles/
```

Accepted file types:

- `.md`
- `.markdown`

### Option B: Sync from Google Drive

Run:

```powershell
python sync_drive_articles.py
python sync_drive_articles.py --limit 5
```

## 10. Process The Articles

Once articles exist in `second-brain/raw/articles/`, start Claude Code and use one of these:

```text
/extract 5
/ingest 5
/sync-and-analyze 5
/insights
/visualize
```

What these commands mean:

- `/extract 5`: process 5 local articles
- `/ingest 5`: similar to extract, but phrased as ingestion
- `/sync-and-analyze 5`: sync up to 5 newest new or updated markdown files from Drive, then process those synced files
- `/insights`: summarize patterns and writing angles
- `/visualize`: explain how to inspect the network in Obsidian

If slash commands are not available, use a direct prompt like this:

```text
Use $extract-key-ideas to process 5 new articles from second-brain/raw/articles/.
```

## 11. What Gets Created

After processing, you should see files here:

```text
second-brain/wiki/article-notes/
second-brain/wiki/key-ideas/
second-brain/wiki/maps/core-connections.md
second-brain/wiki/maps/writing-board.md
second-brain/wiki/index.md
second-brain/wiki/log.md
```

Meaning:

- `article-notes/`: one note per article
- `key-ideas/`: reusable idea pages shared across articles
- `core-connections.md`: which articles connect to which ideas
- `writing-board.md`: possible article angles and thesis ideas
- `index.md`: top-level wiki index
- `log.md`: processing history

## 12. Useful Support Scripts

Run these from the repo root:

```powershell
python sync_drive_articles.py
python sync_drive_articles.py --limit 5
python cleanup_second_brain.py
python cleanup_second_brain.py --apply
python cleanup_second_brain.py --reset-wiki
python cleanup_second_brain.py --reset-wiki --apply
python verify_graph_connections.py
python verify_graph_connections.py --fix
```

## 13. Common Problems

### `claude` is not recognized

- Close and reopen PowerShell
- Check that Claude Code finished installing
- Run `claude --version`

### `ollama` is not recognized

- Close and reopen PowerShell after installing Ollama
- Run `ollama`

### Drive sync says no credentials found

Check:

- the file is named `credentials.json`
- it is in `C:\Users\USER\Documents\second-brain`
- it is real JSON, not a renamed text file

### Drive sync connects but finds no files

Check:

- the correct Drive folder ID is set
- the folder is shared with the service account email
- the files are direct children of that folder
- the files are `.md` or `.markdown`

### Obsidian graph looks empty

Check:

- you opened `second-brain/` as the vault
- not the repo root
- your graph filter is correct

## 14. Recommended Daily Workflow

If you use this repo regularly, this is the simplest routine:

1. Sync or copy new Markdown articles
2. Run `/sync-and-analyze 5` or `/extract 5`
3. Run `/insights`
4. Open Obsidian
5. Review `wiki/maps/writing-board.md`
6. Start writing from the strongest idea cluster

## More Project Docs

- [COMMANDS_README.md](COMMANDS_README.md): plain-language command guide
- [PROCESS_README.md](PROCESS_README.md): plain-language workflow explanation
- [DRIVE_SYNC_SETUP.md](DRIVE_SYNC_SETUP.md): extra Google Drive details

## Official References Used For The Setup Steps

- Ollama Windows install: `https://docs.ollama.com/windows`
- Ollama quickstart: `https://docs.ollama.com/quickstart`
- Ollama + Claude Code: `https://docs.ollama.com/integrations/claude-code`
- Ollama Anthropic-compatible setup: `https://docs.ollama.com/api/anthropic-compatibility`
- Claude Code setup: `https://code.claude.com/docs/en/setup`
- Claude Desktop install: `https://support.claude.com/en/articles/10065433-install-claude-desktop`
