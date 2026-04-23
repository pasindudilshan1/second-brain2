---
title: "Cleanup Report"
type: maintenance-report
generated: cleanup-second-brain
created: 2026-04-23
---

# Cleanup Report

## 2026-04-23 Cleanup

- Removed 221 empty Markdown article placeholders.
- Removed 6 exact duplicate article files, keeping the preferred original filename in each duplicate group.
- Removed 1 non-Markdown stray file from `raw/articles/`.
- Removed root placeholder files `Untitled.base` and `Welcome.md`.
- Removed generated `__pycache__` folders.

## Current Article Folder State

- Empty Markdown article files: 0
- Non-empty Markdown article files: 82
- Exact duplicate content groups: 0

## Notes

- Non-empty unique article sources were kept.
- Key-idea extraction is now handled by the `$extract-key-ideas` Claude skill, not by Python.

## 2026-04-23 Vault Simplification

Removed folders that are not part of the article idea workflow:

- `journal/`
- `content/`
- `wiki/concepts/`
- `wiki/people/`
- `wiki/projects/`

Active folders:

- `raw/articles/` - source articles from Drive or manual saves.
- `wiki/article-notes/` - generated per-article notes; created when extraction runs.
- `wiki/key-ideas/` - generated reusable idea pages; created when extraction runs.
- `wiki/maps/` - Obsidian connection maps, cleanup report, and writing board.
