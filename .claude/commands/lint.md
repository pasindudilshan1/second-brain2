---
description: Run a health check on the wiki
argument-hint: (no arguments)
---

Run a health check on the wiki and report findings.

Scan wiki/ for the following issues:

1. **Broken [[wiki-links]]** - Links that point to non-existent pages
2. **Orphan pages** - Pages not linked from any other page or index.md
3. **Missing frontmatter** - Pages without required YAML frontmatter fields
4. **Stale pages** - Pages untouched for 30+ days (check last-updated)
5. **Contradictions** - Conflicting information between pages

Report findings as a structured list organized by issue type. Include:
- File path
- Description of the issue
- Severity (error, warning, info)

Do NOT fix anything yet. Ask for permission before making any changes.
