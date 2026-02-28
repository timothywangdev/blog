# deep-dive

Become an expert in an industry/space before building. Deep research that transforms surface-level understanding into founder-level knowledge.

## When to Use

Use this skill when:
- An idea passed initial screening and needs deeper validation
- You're entering a space you don't fully understand
- You need to understand buyer psychology, not just pain points
- You want to find non-obvious opportunities through expertise

**Prerequisite:** Run `/startup-ideas` first to identify promising opportunities. This skill is for ideas worth 2-4 hours of focused research.

## Usage

```
/deep-dive <industry or idea>     # Full research (2-4 hours)
/deep-dive <industry> quick       # Rapid orientation (30-60 min)
```

**Examples:**
```
/deep-dive "legal tech for small law firms"
/deep-dive "AI tools for real estate agents"
/deep-dive "developer documentation tools" quick
```

## Agent Strategy

**Use dedicated agents with clean context for each deep dive.** This prevents context pollution and enables parallel research.

### Why Clean Context Matters
- Each industry needs unbiased research (prior findings shouldn't influence new analysis)
- Deep dives accumulate large amounts of data that can overflow context
- Multiple deep dives can run in parallel for comparison

### Parallel Execution Pattern

When researching multiple ideas or comparing industries:

```
# Example: Deep dive on 3 ideas simultaneously
Task agent 1: "Run /deep-dive 'legal tech for small firms'"
Task agent 2: "Run /deep-dive 'AI tools for real estate agents'"
Task agent 3: "Run /deep-dive 'developer documentation tools'"
```

### When to Spawn Agents

| Task | Agent Strategy |
|------|----------------|
| Single deep dive | 1 dedicated agent, full focus |
| Comparing 2-3 ideas | Parallel agents, each produces knowledge base doc |
| Phase research (buyer, competitor, etc.) | Can parallelize phases within a deep dive |

### Persisting Research Progress

**Critical:** All research must be stored in markdown files for context persistence across long research sessions.

#### File Structure

```
startup-ideas/
├── ideas/
│   ├── <idea-slug>/
│   │   ├── README.md             # Idea summary and status
│   │   ├── deep-dive.md          # Main knowledge base document
│   │   ├── competitors.md        # Competitor analysis
│   │   ├── buyer-profile.md      # Buyer research
│   │   ├── pricing-analysis.md   # Pricing data
│   │   ├── validation.md         # Pre-validation results
│   │   └── evidence/             # Screenshots, links
```

Each idea gets its own folder containing ALL research, making it easy to resume or hand off.

#### Why Persist to Files
- Research spans multiple sessions (context windows)
- Enables resume after conversation clears
- Creates audit trail of evidence
- Allows comparison across industries
- Other agents can read and build on findings

#### Progress Tracking
Update `startup-ideas/progress.md` after each research phase:
```markdown
## Deep Dive: <Industry>
- [x] Phase 1: Market Landscape (2024-01-15)
- [x] Phase 2: Buyer Deep Dive (2024-01-15)
- [ ] Phase 3: Workflow Analysis (in progress)
- [ ] Phase 4: Competitive Intelligence
- [ ] Phase 5: Pricing & Economics
- [ ] Phase 6: Distribution Channels
```

## The Goal

Transform from: **"People complain about X"**
Into: **"I understand this market as well as someone who's worked in it for 2 years"**

---

## Research Framework

### Phase 1: Market Landscape (30 min)

**1.1 Define the Space**
- What exactly is this market? (Be precise)
- What adjacent markets exist?
- Is this B2B, B2C, or prosumer?
- Approximate market size (find real data, don't guess)

**1.2 Key Players Map**

| Category | Players | Notes |
|----------|---------|-------|
| Market leaders | | Why did they win? |
| Emerging challengers | | What's their angle? |
| Recent failures | | Why did they fail? |
| Adjacent tools | | What do customers also use? |

**Research Sources:**
- G2/Capterra category pages
- Crunchbase for funding/company data
- ProductHunt launches in the category
- Industry reports (search: `<industry> market report filetype:pdf`)

### Phase 2: Buyer Deep Dive (45 min)

**2.1 Who Actually Buys?**

| Question | Answer |
|----------|--------|
| Job title of decision maker | |
| Job title of end user | |
| Company size sweet spot | |
| Budget owner | |
| Typical budget range | |
| Purchase trigger events | |

**2.2 Buyer Journey**

Map the full journey:
1. **Awareness:** How do they discover solutions exist?
2. **Consideration:** Where do they research options?
3. **Decision:** Who signs off? What's the process?
4. **Onboarding:** What determines success/failure?
5. **Expansion/Churn:** Why do they stay or leave?

**Research Sources:**
- LinkedIn: Search for job titles, read their posts
- Reddit: Find where these buyers hang out
- Industry podcasts: Listen to 2-3 episodes
- YouTube: Watch "day in the life" videos for this role

### Phase 3: Workflow Analysis (45 min)

**3.1 Day-in-the-Life**

Map what your target user actually does:

| Time | Activity | Tools Used | Pain Points |
|------|----------|------------|-------------|
| 9am | | | |
| 10am | | | |
| ... | | | |

**3.2 The Full Stack**

What tools do they use together?

```
[Input tools] → [Your opportunity] → [Output tools]
     ↑                                      ↓
[Data sources]                    [Where results go]
```

**3.3 Workflow Friction Points**

- Where do they switch between tools?
- What requires manual copy-paste?
- What do they wish connected automatically?
- What tasks do they procrastinate on?

**Research Sources:**
- Zapier/Make templates for this workflow
- Reddit: "What's your workflow for X?"
- YouTube tutorials for existing tools
- Tool documentation and integration pages

### Phase 4: Competitive Intelligence (45 min)

**4.1 Deep Competitor Analysis**

For top 3 competitors, document:

| Dimension | Competitor 1 | Competitor 2 | Competitor 3 |
|-----------|--------------|--------------|--------------|
| Pricing model | | | |
| Entry price | | | |
| Enterprise price | | | |
| Free tier? | | | |
| Key features | | | |
| Main weakness (from reviews) | | | |
| Ideal customer | | | |
| Funding/team size | | | |
| Founded when | | | |

**4.2 Positioning Gaps**

After analyzing competitors, identify:
- What segment do they ALL ignore?
- What price point is unserved?
- What use case is poorly supported?
- What integration is missing everywhere?

**4.3 Why Customers Churn**

Read 1-3 star reviews looking for:
- What made them try the product?
- What disappointed them?
- What did they switch to?

**Research Sources:**
- G2/Capterra reviews (filter 1-3 stars)
- Twitter: `"switched from <competitor>"` OR `"leaving <competitor>"`
- Reddit: `<competitor> alternative`
- Crunchbase for funding/headcount data

### Phase 5: Pricing & Unit Economics (30 min)

**5.1 Market Pricing Analysis**

| Competitor | Model | Entry | Pro | Enterprise | Per-seat? |
|------------|-------|-------|-----|------------|-----------|
| | | | | | |

**5.2 Willingness to Pay Signals**

- What do Upwork gigs for this task cost?
- What are consultants charging?
- What are adjacent tools priced at?
- Any "I'd pay $X for Y" comments?

**5.3 Your Unit Economics Estimate**

```
Target price: $X/mo
Estimated customers for $10k MRR: X customers
CAC estimate: $X (based on channel)
LTV (assuming 12mo avg): $X
LTV/CAC ratio: X:1

Viable? [ ] Yes [ ] Maybe [ ] No
```

### Phase 6: Distribution Channels (30 min)

**6.1 How Do Competitors Acquire Customers?**

| Channel | Evidence | Viability for Solo Dev |
|---------|----------|------------------------|
| SEO/Content | | |
| Paid ads | | |
| Social (which?) | | |
| Communities | | |
| Partnerships | | |
| PLG/Viral | | |
| Cold outreach | | |

**6.2 Where Does Your Buyer Hang Out?**

- Subreddits:
- Twitter accounts they follow:
- Newsletters they read:
- Podcasts they listen to:
- Conferences they attend:
- Slack/Discord communities:

**6.3 Realistic First 100 Customers**

How would YOU specifically get 100 customers?
1.
2.
3.

---

## Output: Knowledge Base Document

After completing research, produce this document:

```markdown
# Deep Dive: [Industry/Idea]

## Executive Summary
[2-3 sentences: What did you learn? Is this still worth pursuing?]

## Market Overview
- Market size: $X
- Growth: X% annually
- Key trend: [What's changing?]

## Buyer Profile
- **Decision maker:** [Title, company size]
- **Budget:** $X-Y/year
- **Purchase trigger:** [What makes them buy NOW?]
- **Buying process:** [Who's involved, how long]

## Competitive Landscape
| Player | Strength | Weakness | Price |
|--------|----------|----------|-------|
| | | | |

## The Gap
[What specific opportunity exists that competitors miss?]

## Workflow Context
[Where does your tool fit in their day? What comes before/after?]

## Pricing Strategy
- Recommended price: $X/mo
- Rationale: [Why this price?]
- Unit economics: [LTV/CAC estimate]

## Distribution Plan
1. [Primary channel]
2. [Secondary channel]
3. [Where to find first 10 customers]

## Key Risks
1. [Risk 1 and mitigation]
2. [Risk 2 and mitigation]

## Go/No-Go Recommendation
[ ] STRONG GO - Clear opportunity, validated demand
[ ] CAUTIOUS GO - Promising but needs more validation
[ ] PIVOT - Opportunity exists but different than expected
[ ] KILL - Market too hard, timing wrong, or better opportunities exist

## Next Steps
If GO:
1. [Immediate action]
2. [Validation experiment]
3. [MVP scope]
```

---

## Research Tools & Sources

### Playwright MCP Research

**Industry Reports:**
```
browser_navigate: https://www.google.com/search?q=<industry>+market+report+2024+filetype:pdf
```

**LinkedIn Buyer Research:**
```
browser_navigate: https://www.linkedin.com/search/results/people/?keywords=<job title>
```

**Competitor Deep Dive:**
```
browser_navigate: https://www.g2.com/products/<competitor>/reviews
browser_navigate: https://www.crunchbase.com/organization/<competitor>
```

**Community Discovery:**
```
browser_navigate: https://www.reddit.com/search/?q=<industry>&type=sr
browser_navigate: https://www.google.com/search?q=<industry>+slack+community
```

### Web Search Queries

```
"<industry> market size 2024"
"<buyer title> workflow" OR "<buyer title> day in the life"
"<competitor> vs" - find comparison articles
"switched from <competitor>" site:reddit.com
"<industry> trends 2024"
"<buyer title> podcast" - find industry podcasts
```

---

## Time Budget

| Phase | Quick Mode | Full Mode |
|-------|------------|-----------|
| Market Landscape | 10 min | 30 min |
| Buyer Deep Dive | 15 min | 45 min |
| Workflow Analysis | 10 min | 45 min |
| Competitive Intel | 15 min | 45 min |
| Pricing/Economics | 10 min | 30 min |
| Distribution | 10 min | 30 min |
| **Total** | **70 min** | **3.75 hrs** |

---

## Key Principles

1. **Evidence over assumptions** - Every claim needs a source
2. **Talk to the buyer's world** - Use their language, not yours
3. **Understand the full context** - Your tool is one piece of their day
4. **Find the non-obvious** - Surface research finds surface opportunities
5. **Be willing to kill** - Deep research often reveals why NOT to build
6. **Document everything** - Your research is an asset for later

## What This Skill Does NOT Do

- Generate ideas (use `/startup-ideas` for that)
- Validate with real customers (that's outreach)
- Build the product
- Write marketing copy

This skill builds **knowledge** that makes everything else more effective.
