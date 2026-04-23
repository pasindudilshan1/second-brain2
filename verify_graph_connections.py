#!/usr/bin/env python3
"""
Verify and fix Obsidian graph connections in the second-brain wiki.

This script ensures proper bidirectional links between:
- Article notes and key idea pages
- Key idea pages and their supporting articles
- Related ideas that co-occur in articles

Usage:
    python verify_graph_connections.py --fix

Without --apply, only reports issues. With --apply, fixes them.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
WIKI_DIR = PROJECT_ROOT / "second-brain" / "wiki"
ARTICLE_NOTES_DIR = WIKI_DIR / "article-notes"
KEY_IDEAS_DIR = WIKI_DIR / "key-ideas"
MAPS_DIR = WIKI_DIR / "maps"


def extract_wiki_links(content: str) -> list[str]:
    """Extract all [[wiki links]] from content."""
    pattern = r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]'
    matches = re.findall(pattern, content)
    return [match[0] for match in matches]


def parse_frontmatter(content: str) -> dict[str, str]:
    """Extract frontmatter as dict."""
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    result = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def load_article_notes() -> dict[str, dict]:
    """Load all article notes and extract their key idea links."""
    articles = {}

    if not ARTICLE_NOTES_DIR.exists():
        print(f"Warning: {ARTICLE_NOTES_DIR} does not exist")
        return articles

    for path in ARTICLE_NOTES_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)
        links = extract_wiki_links(content)

        # Find key idea links (in wiki/key-ideas/ slug format)
        key_ideas = []
        for link in links:
            if not link.startswith('article--') and not link.startswith('maps/'):
                key_ideas.append(link)

        articles[path.stem] = {
            'path': path,
            'content': content,
            'frontmatter': frontmatter,
            'key_ideas': key_ideas,
            'title': frontmatter.get('title', path.stem),
        }

    return articles


def load_key_ideas() -> dict[str, dict]:
    """Load all key idea pages and extract their article links."""
    ideas = {}

    if not KEY_IDEAS_DIR.exists():
        print(f"Warning: {KEY_IDEAS_DIR} does not exist")
        return ideas

    for path in KEY_IDEAS_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)
        links = extract_wiki_links(content)

        # Find article links
        article_links = [link for link in links if link.startswith('article--')]

        # Find related idea links
        related_ideas = []
        in_related_section = False
        for line in content.split('\n'):
            if '## Related Ideas' in line:
                in_related_section = True
            elif in_related_section and line.startswith('##'):
                in_related_section = False
            elif in_related_section and '[[' in line:
                match = re.search(r'\[\[([^|\]]+)', line)
                if match:
                    related_ideas.append(match.group(1))

        ideas[path.stem] = {
            'path': path,
            'content': content,
            'frontmatter': frontmatter,
            'article_links': article_links,
            'related_ideas': related_ideas,
            'title': frontmatter.get('title', path.stem),
        }

    return ideas


def verify_connections(articles: dict, ideas: dict) -> dict:
    """Verify bidirectional connections between articles and ideas."""
    issues = {
        'articles_missing_idea_links': [],
        'ideas_missing_article_links': [],
        'ideas_missing_related_ideas': [],
        'orphan_articles': [],
        'orphan_ideas': [],
    }

    # Build reverse index: idea -> articles that link to it
    idea_to_articles = defaultdict(list)
    for article_slug, article_data in articles.items():
        for idea_slug in article_data['key_ideas']:
            idea_to_articles[idea_slug].append(article_slug)

    # Build reverse index: article -> ideas that link to it
    article_to_ideas = defaultdict(list)
    for idea_slug, idea_data in ideas.items():
        for article_slug in idea_data['article_links']:
            article_to_ideas[article_slug].append(idea_slug)

    # Check each article has at least 5 idea links
    for article_slug, article_data in articles.items():
        idea_links = [l for l in article_data['key_ideas'] if l in ideas]
        if len(idea_links) < 5:
            issues['articles_missing_idea_links'].append({
                'article': article_slug,
                'found': len(idea_links),
                'expected': 5,
            })

    # Check each idea links back to its supporting articles
    for idea_slug, idea_data in ideas.items():
        supporting_articles = idea_to_articles.get(idea_slug, [])
        linked_articles = idea_data['article_links']

        missing = set(supporting_articles) - set(linked_articles)
        if missing:
            issues['ideas_missing_article_links'].append({
                'idea': idea_slug,
                'missing_articles': list(missing),
            })

        # Check for related ideas
        if len(idea_data['related_ideas']) < 2:
            issues['ideas_missing_related_ideas'].append({
                'idea': idea_slug,
                'found': len(idea_data['related_ideas']),
                'expected_min': 2,
            })

    # Find orphan articles (not linked by any idea)
    for article_slug in articles:
        if article_slug not in article_to_ideas:
            issues['orphan_articles'].append(article_slug)

    # Find orphan ideas (not linked by any article)
    for idea_slug in ideas:
        if idea_slug not in idea_to_articles:
            issues['orphan_ideas'].append(idea_slug)

    return issues


def fix_connections(articles: dict, ideas: dict, issues: dict) -> int:
    """Fix connection issues. Returns count of fixes applied."""
    fixes_applied = 0

    # Build reverse index: idea -> articles that link to it
    idea_to_articles = defaultdict(list)
    for article_slug, article_data in articles.items():
        for idea_slug in article_data['key_ideas']:
            if idea_slug in ideas:
                idea_to_articles[idea_slug].append(article_slug)

    # Fix ideas missing article links
    for issue in issues['ideas_missing_article_links']:
        idea_slug = issue['idea']
        idea_data = ideas[idea_slug]
        content = idea_data['content']

        # Find the "All Supporting Articles" or "Strongest Supporting Articles" section
        section_pattern = r'(## (?:All|Strongest) Supporting Articles\n+)(.*?)(?=\n##|\Z)'
        match = re.search(section_pattern, content, re.DOTALL)

        if match:
            section_header = match.group(1)
            section_content = match.group(2)

            # Build new article list
            all_articles = set(idea_data['article_links']) | set(issue['missing_articles'])
            new_lines = []

            for article_slug in sorted(all_articles):
                article_data = articles.get(article_slug, {})
                title = article_data.get('title', article_slug) if isinstance(article_data, dict) else article_slug
                # Extract score if present
                score_match = re.search(rf'{re.escape(article_slug)}.*?(\d+/100)', section_content)
                score = score_match.group(1) if score_match else 'N/A'
                new_lines.append(f'- [[{article_slug}|{title}]] - {score}')

            new_section = section_header + '\n'.join(new_lines) + '\n'
            content = content[:match.start()] + new_section + content[match.end():]

            # Write fixed content
            idea_data['path'].write_text(content, encoding='utf-8')
            fixes_applied += 1
            print(f"  Fixed idea '{idea_slug}': added {len(issue['missing_articles'])} article link(s)")

    return fixes_applied


def generate_report(issues: dict) -> str:
    """Generate a markdown report of connection issues."""
    lines = [
        "---",
        'title: "Graph Connections Report"',
        "type: graph-connections-report",
        f"generated: {date.today().isoformat()}",
        "---",
        "",
        "# Graph Connections Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Summary",
        "",
        f"- Articles missing idea links: {len(issues['articles_missing_idea_links'])}",
        f"- Ideas missing article links: {len(issues['ideas_missing_article_links'])}",
        f"- Ideas missing related ideas: {len(issues['ideas_missing_related_ideas'])}",
        f"- Orphan articles: {len(issues['orphan_articles'])}",
        f"- Orphan ideas: {len(issues['orphan_ideas'])}",
        "",
    ]

    if issues['articles_missing_idea_links']:
        lines.extend(["## Articles Missing Idea Links", ""])
        for issue in issues['articles_missing_idea_links']:
            lines.append(f"- `{issue['article']}`: found {issue['found']} ideas, expected {issue['expected']}")
        lines.append("")

    if issues['ideas_missing_article_links']:
        lines.extend(["## Ideas Missing Article Links", ""])
        for issue in issues['ideas_missing_article_links']:
            lines.append(f"- `{issue['idea']}`: missing links to {len(issue['missing_articles'])} article(s)")
            for article in issue['missing_articles']:
                lines.append(f"  - `{article}`")
        lines.append("")

    if issues['ideas_missing_related_ideas']:
        lines.extend(["## Ideas Missing Related Ideas", ""])
        for issue in issues['ideas_missing_related_ideas']:
            lines.append(f"- `{issue['idea']}`: found {issue['found']} related ideas, expected min {issue['expected_min']}")
        lines.append("")

    if issues['orphan_articles']:
        lines.extend(["## Orphan Articles", "", "Articles not linked by any key idea:", ""])
        for article in issues['orphan_articles']:
            lines.append(f"- `{article}`")
        lines.append("")

    if issues['orphan_ideas']:
        lines.extend(["## Orphan Ideas", "", "Ideas not linked by any article:", ""])
        for idea in issues['orphan_ideas']:
            lines.append(f"- `{idea}`")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Actually fix issues. Without this, only report.",
    )
    args = parser.parse_args()

    print("Loading article notes...")
    articles = load_article_notes()
    print(f"  Found {len(articles)} article notes")

    print("Loading key ideas...")
    ideas = load_key_ideas()
    print(f"  Found {len(ideas)} key ideas")

    print("\nVerifying connections...")
    issues = verify_connections(articles, ideas)

    total_issues = (
        len(issues['articles_missing_idea_links']) +
        len(issues['ideas_missing_article_links']) +
        len(issues['ideas_missing_related_ideas']) +
        len(issues['orphan_articles']) +
        len(issues['orphan_ideas'])
    )

    if total_issues == 0:
        print("\n✓ All connections look good!")
        return

    print(f"\nFound {total_issues} issue(s):")
    print(f"  - Articles missing idea links: {len(issues['articles_missing_idea_links'])}")
    print(f"  - Ideas missing article links: {len(issues['ideas_missing_article_links'])}")
    print(f"  - Ideas missing related ideas: {len(issues['ideas_missing_related_ideas'])}")
    print(f"  - Orphan articles: {len(issues['orphan_articles'])}")
    print(f"  - Orphan ideas: {len(issues['orphan_ideas'])}")

    if args.fix:
        print("\nApplying fixes...")
        fixes = fix_connections(articles, ideas, issues)
        print(f"Applied {fixes} fix(es)")

    # Generate report
    report_content = generate_report(issues)
    report_path = MAPS_DIR / "graph-connections-report.md"
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content, encoding='utf-8')
    print(f"\nReport written to: {report_path}")

    if not args.fix:
        print("\nDry run only. Re-run with --fix to apply fixes.")


if __name__ == "__main__":
    main()
