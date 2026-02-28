# startup-ideas

Find ≤3 validated startup ideas. Kill bad ideas fast. Output GO ideas or none.

## Usage

```
/startup-ideas                    # Scan for opportunities
/startup-ideas <niche>            # Focus on specific niche
/startup-ideas first-principles   # Proactive discovery
```

## Execution Flow

```
1. SETUP
   └── Create startup-ideas/ directory structure

2. GENERATE (loop until 3 GO or 100 validated)
   ├── WebSearch/Playwright → find pain point
   ├── Generate idea from pain point
   └── VALIDATE immediately (see below)

3. VALIDATE (per idea)
   ├── Filter 1: Surface Check → evidence exists?
   ├── Filter 2: Technical Feasibility → can you build it?
   ├── Filter 3: Market Dynamics → growing or dying?
   ├── Filter 4: Customer Reality → who pays?
   └── Filter 5: Boring Business Test → hot problem trap?

4. DECISION
   ├── NO-GO → log to kill-log.md, continue
   ├── CONDITIONAL GO → note condition, continue
   └── GO → add to go-ideas.md, check if done

5. OUTPUT
   └── Write final go-ideas.md (0-3 ideas)
```

## Stop Conditions

- 3 GO ideas found → stop (success)
- 100 ideas validated → stop (exhausted)
- All niches/frameworks explored → stop (natural end)

## Constraints

- Solo developer, bootstrapped
- Infra budget: ≤$200/month
- MVP timeline: ~2 weeks
- Goal: $0 → $10k MRR

---

## Tool Usage

### WebSearch (Required)

Use for all research. Don't rely on training data.

| Phase | Queries |
|-------|---------|
| Pain discovery | `"frustrated with <tool>" site:reddit.com`, `<niche> complaints 2024-2025` |
| Competitor | `<competitor> pricing 2025`, `<competitor> alternatives` |
| Market | `<market> growth 2025`, `is <market> dying` |
| Technical | `<approach> accuracy`, `<API> limitations` |

### Playwright MCP (For Social Media)

Bypasses auth walls. Uses existing browser session.

```bash
# Twitter/X
mcp__playwright__browser_navigate → https://twitter.com/search?q=<keyword>%20sucks&f=live
mcp__playwright__browser_snapshot → capture results

# LinkedIn
mcp__playwright__browser_navigate → https://www.linkedin.com/search/results/content/?keywords=<keyword>%20frustrated
mcp__playwright__browser_snapshot → extract posts

# Reddit
mcp__playwright__browser_navigate → https://www.reddit.com/search/?q=<keyword>+frustrated&sort=top&t=year
mcp__playwright__browser_snapshot → get posts
mcp__playwright__browser_click → click into post
mcp__playwright__browser_snapshot → read comments

# G2 Reviews
mcp__playwright__browser_navigate → https://www.g2.com/products/<competitor>/reviews
mcp__playwright__browser_snapshot → extract 1-3 star reviews

# Upwork (find paid manual tasks)
mcp__playwright__browser_navigate → https://www.upwork.com/nx/search/jobs/?q=<task>&sort=recency
mcp__playwright__browser_snapshot → repetitive jobs = tool opportunity

# Evidence capture
mcp__playwright__browser_take_screenshot → save to startup-ideas/ideas/<slug>/evidence/
```

### Platform Search Patterns

| Platform | URL | What to Look For |
|----------|-----|------------------|
| Reddit | `/search/?q=<keyword>+frustrated&sort=top&t=year` | 100+ upvotes, workarounds |
| HN | `hn.algolia.com/?q=<keyword>&sort=byPopularity` | Points > 100, "I'd pay" |
| Twitter/X | `/search?q=<keyword>%20sucks&f=live` | Viral threads, ratio'd posts |
| LinkedIn | `/search/results/content/?keywords=<keyword>%20frustrating` | B2B pain, manager complaints |
| G2 | `/products/<competitor>/reviews` | 1-3 star reviews, recurring complaints |
| GitHub | `/issues?q=sort%3Areactions-%2B1-desc` | 50+ 👍, long-open issues |
| Upwork | `/nx/search/jobs/?q=<task>` | Repetitive $50-500 jobs |

---

## Validation (Per Idea)

Run `/validate-idea` criteria immediately after generating each idea.

### 5 Filters

| Filter | Pass | Fail |
|--------|------|------|
| Surface Check | Evidence on Reddit/HN/G2 | No complaints found |
| Technical Feasibility | Standard web app | Arms race, >90% accuracy needed |
| Market Dynamics | Growing, no free alternative | Shrinking, big co solved it |
| Customer Reality | Specific buyer, can pay with CC | Vague "companies", needs procurement |
| Boring Business Test | Unsexy but necessary | Hot/trending, VC-backable |

### Decision

```python
if all_filters_pass:
    verdict = "GO"
    add_to_go_ideas()
elif most_pass_with_conditions:
    verdict = "CONDITIONAL GO"
    note_conditions()
else:
    verdict = "NO-GO"
    log_to_kill_log(filter_failed, reason)
```

---

## File Structure

```
startup-ideas/
├── progress.md        # Current status, ideas validated/killed
├── kill-log.md        # Every killed idea + reason
├── go-ideas.md        # Final output (≤3 GO ideas)
└── ideas/
    └── <idea-slug>/
        ├── README.md      # Summary, score, status
        ├── validation.md  # Filter results
        └── evidence/      # Screenshots
```

### kill-log.md Format

```markdown
#### ❌ [Idea Name]
- **Source:** [Where found]
- **Killed at:** Filter [N] ([Name])
- **Reason:** [One sentence]
```

### go-ideas.md Format

```markdown
# Startup Ideas: Final Results

**Date:** YYYY-MM-DD
**Ideas Generated:** N
**Ideas Killed:** N
**GO Ideas:** N (0-3)

---

## 🟢 GO Idea #1: [Name]

**One-liner:** [Solution]

| Filter | Result |
|--------|--------|
| Surface Check | ✅ [evidence] |
| Technical Feasibility | ✅ [why] |
| Market Dynamics | ✅ [why] |
| Customer Reality | ✅ [who pays] |
| Boring Business Test | ✅ [why] |

**Confidence:** X/10
**Next step:** [Validation action]
```

---

## Agent Strategy

### Parallel Execution

Spawn 4-6 agents for different niches:

```
Task agent 1: "Research <niche1> pain points, validate each immediately, return GO ideas only"
Task agent 2: "Research <niche2> pain points, validate each immediately, return GO ideas only"
...
```

Each agent returns ONLY:
- GO ideas (with validation summary)
- Kill log entries
- Search queries used

### First Principles Frameworks (When No Niche Given)

| Framework | Question |
|-----------|----------|
| Tech Inflection | What's possible now that wasn't 2 years ago? |
| Picks & Shovels | What does everyone in this space need? |
| Unbundling | What segment is underserved by the giant? |
| Workarounds | What hacky solutions exist? (`<tool> spreadsheet`) |
| Cost Collapse | What was Fortune 500 only, now SMB accessible? |

---

## Idea Template

```markdown
## [Idea Name]

### Pain Point
[Quote actual complaints]

### Target Audience
[Job title, company size, situation]

### Pain Intensity (1-10)
- Frequency: X
- Severity: X
- Urgency: X

### Evidence
- [Source 1]: "[Quote]" (X upvotes)
- [Source 2]: "[Quote]" (X comments)

### Competitors
| Name | What Sucks | Price |
|------|-----------|-------|
| | | |

### Solution
**One-liner:** [Solution]
**MVP (2 weeks):** [Scope]
**Skip:** [Features to cut]

### Pricing
[Price point] because [rationale]

### Kill Criteria
- [Risk 1]
- [Risk 2]
```

---

## Scoring

### Pain Point Score (need 8+ to pursue)

| Signal | Points |
|--------|--------|
| 100+ upvotes | +3 |
| 50+ comments | +2 |
| Multiple posts same issue | +3 |
| Workarounds shared | +2 |
| "I would pay" comments | +4 |
| Same complaint 3+ platforms | +10 |

### Cross-Platform Validation (need 20+ for strong)

| Evidence | Points |
|----------|--------|
| Same complaint 3+ platforms | +10 |
| 100+ combined engagement | +5 |
| Workarounds on multiple platforms | +5 |
| "I would pay" on 2+ platforms | +8 |

---

## Rules

1. **WebSearch every step** — don't use training data
2. **Playwright for social media** — bypasses auth
3. **Validate immediately** — don't batch
4. **Kill fast** — log reason, move on
5. **Evidence required** — quote sources
6. **0 GO is valid** — better than bad ideas
7. **B2B > B2C** — higher LTV, lower churn
8. **Boring > Hot** — less competition
