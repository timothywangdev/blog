# validate-idea

Kill bad ideas in 30 minutes. Run 7 brutal filters that catch 90% of startup failures before you waste time building.

## Usage

```
/validate-idea <idea description>
```

## Execution Flow

```
1. PARSE idea → extract: problem, solution, customer, market

2. RUN FILTERS (stop at first NO-GO)
   ├── Filter 1: Surface Check (5 min) → pain exists?
   ├── Filter 2: Technical Feasibility (5 min) → can you build it?
   ├── Filter 3: Market Dynamics (5 min) → growing or dying?
   ├── Filter 4: Customer Reality (5 min) → who pays, how?
   ├── Filter 5: Distribution (5 min) → how do you reach them?
   ├── Filter 6: Why You? (2 min) → founder-market fit
   └── Filter 7: Tarpit Check (3 min) → known trap?

3. OUTPUT verdict: GO / CONDITIONAL GO / NO-GO
```

**Total time: ~30 min. Kill at first failure.**

---

## The 7 Filters

### Filter 1: Surface Check (5 min)

**Question:** Does this problem actually exist outside your head?

**WebSearch:**
```
"frustrated with <tool>" site:reddit.com
<problem> complaints 2024 2025
"wish there was" <category>
"I would pay for" <solution>
```

**Playwright (social proof):**
```bash
mcp__playwright__browser_navigate → reddit.com/search/?q=<keyword>+frustrated
mcp__playwright__browser_snapshot → extract upvotes, quotes
```

| Signal | Score |
|--------|-------|
| 100+ upvotes on complaint | +3 |
| 50+ comments | +2 |
| Multiple posts same issue | +3 |
| Workarounds being shared | +2 |
| "I would pay" comments | +4 |

**Pass:** Score ≥8, with verbatim quotes
**Kill:** No evidence, only your assumption

---

### Filter 2: Technical Feasibility (5 min)

**Question:** Can you actually build what you're promising?

| Trap | Why It Fails |
|------|--------------|
| "AI detects X" | Arms race—adversaries adapt faster than you |
| "Verify/authenticate X" | Only catches sloppy bad actors |
| "Automate platform X" | Platform will ban you or build it |
| "Aggregate data from X" | APIs get revoked, scraping gets blocked |
| ">90% accuracy required" | You'll achieve 60%, users will hate it |

**Questions to answer:**
1. What's the core technical approach?
2. What accuracy/reliability can you actually achieve?
3. Does this require data you don't have?
4. Is this an arms race against adversaries?

**Pass:** Standard web app, clear technical path
**Kill:** Arms race, platform dependency, accuracy gap

---

### Filter 3: Market Dynamics (5 min)

**Question:** Is this market growing, and is there room for you?

**WebSearch:**
```
<market> trends 2025
<market> market size growth
<category> companies funding 2024
is <market> dying
```

| Question | Good | Bad |
|----------|------|-----|
| Trend | Growing, new problem | Shrinking, reverting to old ways |
| Competition | Fragmented, no clear winner | One dominant player, or 50+ funded startups |
| Self-solve | Too hard/expensive to DIY | Big companies doing it in-house |
| Timing | New enabling technology | Problem existed for 20 years, been tried |

**Pass:** Growing market, no dominant player, new enabler
**Kill:** Shrinking, winner-take-all, or "why hasn't this been solved?"

---

### Filter 4: Customer Reality (5 min)

**Question:** Who exactly pays, and can they buy?

**YC Partner Questions:**
1. "Who is your customer?" → Must be specific (job title, company size)
2. "How much will they pay?" → Must have evidence, not guess
3. "How do they buy today?" → Credit card = good, procurement = bad
4. "What's the first sale?" → If you can't describe it, you can't close it

| Customer Type | Buy Ease | Reality |
|---------------|----------|---------|
| Individual (B2C) | Easy | Won't pay more than $20/mo |
| SMB owner (<10 ppl) | Easy | Problem must be DAILY |
| SMB manager | Medium | Needs boss approval |
| Mid-market | Hard | Budget cycles, multiple stakeholders |
| Enterprise | Very Hard | 6-12 month sales cycle minimum |

**Pass:** Specific buyer, can pay with credit card, urgent problem
**Kill:** "Companies", needs procurement, problem is monthly/yearly

---

### Filter 5: Distribution (5 min)

**Question:** How do you reach your first 10 customers without spending money?

**YC Partner Question:** "How will you get your first users?"

| Channel | Works If | Doesn't Work If |
|---------|----------|-----------------|
| Cold email | You know exactly who to email | "Businesses" |
| Content/SEO | You can write better than anyone | Commodity topic |
| Community | You're already a member | You'll "join and promote" |
| Product Hunt | Developer/early adopter audience | B2B enterprise |
| Referral | Product has network effects | Single-player tool |

**Red flags:**
- "We'll do marketing" (means you don't know)
- "Paid ads" (means you need funding)
- "Partnerships" (means 6+ months to first customer)
- "Virality" (means you're hoping)

**Pass:** Can describe exact steps to first 10 customers
**Kill:** Vague "marketing", requires paid acquisition

---

### Filter 6: Why You? (2 min)

**Question:** Why are you the right person to build this?

**YC cares about founder-market fit:**

| Strong Signal | Weak Signal |
|---------------|-------------|
| Built this at previous job | "I read about this problem" |
| Domain expert (5+ years) | "I'm a fast learner" |
| Already have customers waiting | "People said they'd use it" |
| Failed at this before, learned | First time thinking about it |
| Network in the industry | No connections |

**Pass:** Unfair advantage—domain expertise, existing network, or prior attempts
**Kill:** "I just thought of this" with no edge

---

### Filter 7: Tarpit Check (3 min)

**Question:** Is this a known startup graveyard?

**YC "Tarpit" Ideas** (look attractive, kill startups):

| Tarpit | Why It Fails |
|--------|--------------|
| Consumer social apps | Network effects require massive scale |
| Local services marketplaces | Unit economics never work |
| "Uber for X" | Supply-side acquisition is brutal |
| Restaurant/food tech | Margins are 3%, everyone has tried |
| Events/ticketing | Highly seasonal, competitors entrenched |
| Dating apps | Winner-take-all, Tinder exists |
| Crypto/Web3 for normies | Normies don't care |
| Developer tools (broad) | Developers don't pay, big co's give free |
| Note-taking apps | 1000 exist, nobody switches |
| CRM for X | Salesforce ecosystem dominates |

**AI wrapper nuance:** "Thin wrapper on GPT" is a tarpit, but AI products CAN have massive value:

| Has Moat | No Moat |
|----------|---------|
| [Manus](https://techcrunch.com/2025/12/29/meta-just-bought-manus-an-ai-startup-everyone-has-been-talking-about/) ($2B+ exit to Meta, Dec 2025) | Generic "ChatGPT for X" |
| [Cursor](https://www.cnbc.com/2025/11/13/cursor-ai-startup-funding-round-valuation.html) ($29B valuation, $1B ARR) | Simple API wrapper |
| [OpenClaw](https://techcrunch.com/2026/02/15/openclaw-creator-peter-steinberger-joins-openai/) (acqui-hire by OpenAI) | Feature OpenAI will ship |
| Vertical AI with proprietary data | Horizontal AI with no data |
| Deep workflow integration | Chatbot slapped on website |

**What separates $29B Cursor from dead wrappers:**
- UX is the product (not the AI)
- $1B+ ARR (revenue, not just users)
- Deep workflow integration (IDE, not chatbot)
- Hard to replicate (context + habit)

**AI moat checklist:**
- [ ] Workflow/UX is 10x better than ChatGPT directly?
- [ ] Revenue traction? (Cursor: $1B ARR)
- [ ] Deep vertical or workflow lock-in?
- [ ] Hard to replicate in < 6 months?
- [ ] Acquirer would buy for team + product, not just users?

**"Hot Problem" Traps:**

| Signal | Trap |
|--------|------|
| Trending on HN/Reddit | Competition incoming in 3 months |
| VC-backable narrative | You'll be outspent by funded competitors |
| Obvious pain + obvious solution | Already being built by 10 teams |
| "AI for X" angle | Technically harder than it looks |

**Better signs:**
- Boring, specific vertical
- Problem for 10+ years
- Nobody talks about it
- You discovered it through work

**Pass:** Not a tarpit, not a hot problem
**Kill:** Known graveyard or hot trending topic

---

## Verdict Decision

```python
if all_7_filters_pass:
    verdict = "GO"
    confidence = count_strong_signals() / 7 * 10

elif 5_or_more_pass and failures_are_fixable:
    verdict = "CONDITIONAL GO"
    conditions = list_what_needs_validation()

else:
    verdict = "NO-GO"
    reason = first_failed_filter
```

---

## Output Format

```markdown
# Idea Validation: [Idea Name]

## Verdict: GO / CONDITIONAL GO / NO-GO
**Confidence:** X/10
**Primary risk:** [One sentence]
**Time to validate:** [If CONDITIONAL GO]

## Filter Results

| # | Filter | Result | Finding |
|---|--------|--------|---------|
| 1 | Surface Check | ✅/❌ | [Key evidence or gap] |
| 2 | Technical Feasibility | ✅/❌ | [Build approach or blocker] |
| 3 | Market Dynamics | ✅/❌ | [Growth signal or concern] |
| 4 | Customer Reality | ✅/❌ | [Who pays or why they won't] |
| 5 | Distribution | ✅/❌ | [Channel or lack thereof] |
| 6 | Why You? | ✅/❌ | [Edge or missing fit] |
| 7 | Tarpit Check | ✅/❌ | [Clear or known graveyard] |

## If NO-GO

**Killed at:** Filter [N] — [Name]
**Reason:** [One sentence]
**Could pivot?** [Yes/No + direction if yes]

## If GO

**Strongest signal:** [What makes this compelling]
**Biggest risk:** [What could still kill it]
**First step:** [Exact next action]
```

---

## YC Partner Heuristics

**Questions that kill ideas:**

1. "Why now?" — If you can't answer, timing is wrong
2. "What do you know that others don't?" — If nothing, no edge
3. "How do you get to $1?" — If unclear, you don't understand the business
4. "Who desperately needs this?" — If "everyone", it's no one
5. "What's the insight?" — If "X is broken", that's observation not insight

**Speed tests:**

| Question | Good | Bad |
|----------|------|-----|
| How fast to first $1? | < 1 week | "After we build..." |
| How fast to 10 users? | < 1 month | "After we launch..." |
| Would you use it yourself? | Yes, daily | "It's for others" |
| Can you explain in 1 sentence? | Yes | Needs paragraphs |

**Dalton Caldwell's filters:**

1. **Schlep blindness** — Is this hard work others avoid? (Good)
2. **Unsexy** — Does it sound boring? (Good)
3. **Narrow** — Is it very specific? (Good)
4. **Yours** — Do you have this problem? (Good)

---

## Tool Commands

### WebSearch (Use for every filter)

```
# Surface check
"<problem> frustrated" site:reddit.com
"<tool> sucks" OR "<tool> broken"
"wish there was <category>"

# Market
<market> growth 2025
<market> trends funding
<category> startups launched 2024

# Competition
<competitor> pricing
<competitor> alternatives
<competitor> review
```

### Playwright MCP (Verify claims)

```bash
# Competitor check
mcp__playwright__browser_navigate → <competitor URL>
mcp__playwright__browser_snapshot → verify live, check pricing

# Social proof
mcp__playwright__browser_navigate → reddit.com/search/?q=<keyword>
mcp__playwright__browser_snapshot → count upvotes

# App store competition
mcp__playwright__browser_navigate → Chrome Web Store / Shopify Apps
mcp__playwright__browser_snapshot → count competitors

# Evidence
mcp__playwright__browser_take_screenshot → save proof
```

---

## Rules

1. **Kill at first failure** — Don't waste time on later filters
2. **WebSearch everything** — Don't trust training data
3. **Verify with Playwright** — Screenshots > assumptions
4. **Specific > vague** — "SMB owners in construction" not "businesses"
5. **Evidence > opinions** — Quotes and numbers, not feelings
6. **30 min max** — If it takes longer, you're rationalizing
7. **NO-GO is success** — Saved you months of wasted time
