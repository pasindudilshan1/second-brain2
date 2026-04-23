# Obsidian Graph View Guide

## How to Visualize the Idea-Article Network

### Step 1: Open Graph View
- Click the **Graph View** icon in Obsidian's left sidebar (looks like a network diagram)

### Step 2: Set Path Filters

**For full network (ideas + articles):**
```
Path filter: wiki/**
```

**For ideas only (cleaner view of core concepts):**
```
Path filter: wiki/key-ideas/**
```

**For articles only:**
```
Path filter: wiki/article-notes/**
```

### Step 3: Recommended Graph Settings

| Setting | Value | Why |
|---------|-------|-----|
| Node Size | By connections | Shows which ideas/articles are most central |
| Link Distance | 50-100 | Clearer clustering |
| Show Arrows | Off | Connections are bidirectional |
| Node Color | By path group | Distinguishes ideas from articles |

### Step 4: What You'll See

**Central Hub Nodes** (most connections):
- `cfo-strategic-leadership` - connected to 4 articles, 5 other ideas
- `ai-adoption-in-finance-and-accounting` - connected to 5 articles, 4 other ideas

**Bridge Nodes** (connect clusters):
- `human-agent-collaboration-model` - connects AI, talent, and leadership
- `finance-talent-and-skills-gap` - connects AI adoption to career/advisory themes

**Peripheral Nodes** (specialized topics):
- `regulatory-complexity-as-top-challenge` - compliance cluster
- `cfo-uncertainty-and-volatility` - market conditions cluster

## Graph Legend

```
[Key Idea Node] ──── [Article Node]
      │                    │
      │                    └─── Links to 5 ideas
      │
      └─── Links to all supporting articles
           + Links to related ideas
```

## Expected Connections

Each **article note** links to:
- 5 key ideas (its extracted ideas)
- 2-3 other articles (same-idea connections)

Each **key idea page** links to:
- 3-5 supporting articles
- 3-4 related ideas

## Visual Pattern to Expect

```
                    ┌─────────────────┐
                    │  CFO Strategic  │
                    │   Leadership    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │    AI    │       │  Talent  │       │Uncertainty│
   │ Adoption │       │   Gap    │       │          │
   └────┬─────┘       └────┬─────┘       └──────────┘
        │                  │
        └────────┬─────────┘
                 │
                 ▼
        ┌─────────────────┐
        │   Human+Agent   │
        │  Collaboration  │
        └─────────────────┘
```

## Troubleshooting

**If graph looks empty:**
- Check that files are in `second-brain/wiki/` folder
- Verify Obsidian is set to use this folder as vault root

**If connections don't show:**
- Links must use `[[wikilink]]` syntax (not markdown `[text](url)`)
- Both files must exist for connection to appear

**If nodes are too crowded:**
- Use path filter to show only `wiki/key-ideas/**`
- Or zoom out with mouse wheel

## Key Clusters to Identify

1. **CFO Leadership Cluster** (center-top)
   - cfo-strategic-leadership
   - Articles: AI-First CFO, 6 Finance Challenges, Expanded Mandate

2. **AI Adoption Cluster** (center)
   - ai-adoption-in-finance-and-accounting
   - Articles: AI Pain Reliever, AI Pushing Accountants, AI-First CFO

3. **Talent/Skills Cluster** (center-bottom)
   - finance-talent-and-skills-gap
   - human-agent-collaboration-model
   - Articles: AI Pushing Accountants, 6 Finance Challenges

4. **Uncertainty Cluster** (right)
   - cfo-uncertainty-and-volatility
   - Articles: CFO Uncertainty Q1, Deloitte CFO Signals

5. **Regulatory Cluster** (left)
   - regulatory-complexity-as-top-challenge
   - Articles: Top Challenges for Firms
