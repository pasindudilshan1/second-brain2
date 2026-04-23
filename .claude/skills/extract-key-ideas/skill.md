---
name: extract-key-ideas
description: Extract exactly five scored key ideas from saved Markdown articles and build an Obsidian network of article notes, reusable key-idea pages, and same-idea connection maps. Use when the user asks to extract key ideas, analyze articles for writing, connect articles by similar ideas, create Obsidian graph links, or update the second-brain article idea network without using Python for extraction.
---

# Extract Key Ideas

## Core Rule

Do the key-idea extraction by reading and reasoning over the article text. Do not call Python, keyword scripts, TF-IDF scripts, or LLM API scripts to decide the five ideas.

It is acceptable to run non-extraction commands for support tasks, such as:
- `python sync_drive_articles.py` to sync raw articles from Google Drive.
- `python cleanup_second_brain.py --apply` only when the user asks to clean clutter.

## Vault Paths

Assume the project root is `C:\Users\USER\Documents\second-brain`.

- Raw article sources: `second-brain/raw/articles/`
- Article idea notes: `second-brain/wiki/article-notes/`
- Reusable key idea pages: `second-brain/wiki/key-ideas/`
- Same-idea map: `second-brain/wiki/maps/core-connections.md`
- Writing board: `second-brain/wiki/maps/writing-board.md`
- Wiki index: `second-brain/wiki/index.md`
- Activity log: `second-brain/wiki/log.md`

Never edit raw article source files except for explicit cleanup of empty or duplicate imports.

## Batch Workflow

1. Select articles from `second-brain/raw/articles/`.
   - Prefer new or changed non-empty `.md` files.
   - If the user gives no limit, process a manageable batch and state what was processed.
   - Skip empty files and obvious bot/challenge pages such as "just a moment".
2. Read each article enough to understand the argument, not just headings.
3. Extract exactly five key ideas per article.
4. Score each idea from 0 to 100 using the scoring rubric below.
5. Write one article note per article in `wiki/article-notes/`.
6. Create or update one key idea page per reusable idea in `wiki/key-ideas/`.
7. Update `wiki/maps/core-connections.md` to link articles that share the same or substantially similar key idea.
8. Update `wiki/maps/writing-board.md` with article angles for the strongest idea clusters.
9. Update `wiki/index.md` and append a short entry to `wiki/log.md`.
10. For visualization, tell the user to open Obsidian Graph View with the recommended path filter.

## Scoring Rubric

Score each key idea against the specific article, not against the whole vault.

- 90-100: Central thesis or repeated argument with strong supporting detail.
- 75-89: Major section-level idea with direct evidence.
- 55-74: Important supporting idea, but not the main thesis.
- 35-54: Mentioned clearly but lightly developed.
- 0-34: Incidental mention; usually do not select unless needed to reach five ideas.

Use one decimal only when useful. Prefer whole numbers.

## Idea Naming

Use reusable idea names, not article-specific headlines.

Good:
- `AI adoption in finance and accounting`
- `CFO strategic leadership`
- `Regulatory disclosure and reporting change`
- `Accounting talent and skills`

Bad:
- `This article is about AI`
- `Kenvue CFO article`
- `Interesting accounting update`

Slug filenames in lowercase hyphen-case:
- `ai-adoption-in-finance-and-accounting.md`
- `cfo-strategic-leadership.md`

## Article Note Template

Create `wiki/article-notes/article--SOURCE-STEM.md`.

```markdown
---
title: "Article title"
type: article-idea-note
source: "raw/articles/source-file.md"
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
---

# Article title

Raw source: `raw/articles/source-file.md`
Original URL: https://example.com

## Five Key Ideas

1. [[key-idea-slug|Readable Idea Name]] - score: 88/100
   Evidence: Brief paraphrase from the article.
2. ...

## Same-Idea Article Links

- [[article--other-source|Other article title]] - shared: [[key-idea-slug|Readable Idea Name]]

## Drafting Angle

- Start from [[strongest-idea|Strongest Idea]] as the main thesis.
- Use the same-idea article links as supporting evidence and contrast points.
```

## Key Idea Page Template

Create or update `wiki/key-ideas/key-idea-slug.md`.

```markdown
---
title: "Readable Idea Name"
type: key-idea
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
---

# Readable Idea Name

## Score

- Average article score: 82/100
- Highest article score: 94/100
- Supporting articles: 4

## Strongest Supporting Articles

- [[article--source-a|Article A]] - 94/100
  - Evidence: Brief paraphrase.

## Related Ideas

- [[related-idea|Related Idea]] - appears together in 3 article(s)

## Use For Writing

- Treat the highest-scoring articles as evidence.
- Treat related ideas as sections, counterpoints, or follow-up articles.
```

## Similarity Rules

Two articles should be linked when:
- They share at least one same key idea, or
- Their idea wording differs but the underlying claim is the same.

Similarity score:
- 80-100: Three or more shared ideas, or the same dominant thesis.
- 60-79: Two strong shared ideas.
- 35-59: One strong shared idea plus a related supporting idea.
- 10-34: One light shared idea.

Only include useful links in article notes. Put larger groupings in `core-connections.md`.

## Output Discipline

- Keep every key idea in its own Markdown file.
- Use Obsidian wiki links everywhere: `[[slug|Label]]`.
- Do not invent article claims not supported by the source.
- Prefer paraphrase over quotation.
- If the article is too short or empty, skip it and note the skip in the final response.
- When processing many articles, work in batches instead of pretending the whole vault was analyzed.

## Obsidian Graph Optimization

To ensure the idea-article network displays correctly in Obsidian Graph View:

### Key Idea Page Requirements

Each key idea page MUST link back to ALL its supporting articles (not just strongest):

```markdown
## All Supporting Articles

- [[article--source-slug|Article Title]] - score/100
- [[article--another-slug|Another Article]] - score/100
```

### Article Note Requirements

Each article note MUST link to:
1. All 5 key ideas with scores
2. Related articles that share ideas (same-idea links)

```markdown
## Five Key Ideas

1. [[key-idea-slug|Readable Idea Name]] - score: 88/100

## Same-Idea Article Links

- [[article--other-source|Other article]] - shared: [[key-idea-slug|Shared Idea]]
```

### Idea-to-Idea Connections

Each key idea page MUST include related ideas that co-occur:

```markdown
## Related Ideas

- [[related-idea-slug|Related Idea Name]] - appears together in N articles
```

### Graph View Instructions (for user)

After processing, tell the user:
1. Open Obsidian Graph View
2. Set path filter: `wiki/**` for full network or `wiki/key-ideas/**` for ideas only
3. Set node size: "By connections" to show central hubs
4. Expected pattern: CFO leadership and AI adoption as central hubs

### Output Files Checklist

Always create/update:
- `wiki/article-notes/article--SOURCE.md` - one per article
- `wiki/key-ideas/idea-slug.md` - one per unique idea
- `wiki/maps/core-connections.md` - idea clusters with article tables
- `wiki/maps/writing-board.md` - thesis angles with evidence
- `wiki/index.md` - catalog of all notes and ideas
- `wiki/log.md` - append batch summary
