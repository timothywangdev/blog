---
name: polish
description: Polish Documentation (core workflow)
---

# Polish Documentation

Polish the current document for clarity, mathematical rigor, and accessibility.

**Includes:** Hooks (engagement, titles) and Visuals (images, diagrams) as mandatory passes.

## Critical Requirements

- **Author name**: Always use `author: "Hujie Wang"` in frontmatter
- **Always spawn a team**: Launch agents in parallel for EVERY polish run — never execute passes sequentially yourself. Minimum team configuration below.
- **Substack posts (_substack.qmd): NO TABLES EVER.** Substack does not render markdown tables — they appear as jumbled unreadable text. If polishing a `_substack.qmd` file, convert any tables to bullet lists and never introduce new tables. Use bullet lists for all comparisons, schedules, and structured data.

## Team Configuration (spawn all at once)

When `/polish` is invoked, immediately spawn these agents in a single message:

| Agent | Passes | What it does |
|-------|--------|--------------|
| **Agent 1: Structure + Hooks** | Pass 0, 1, 2, 5 | Research analogies, scope check, TL;DR, section hooks, PAS opening |
| **Agent 2: Math + Notation** | Pass 3, 7 | Equation intuition, variable definitions, notation consistency, math colors |
| **Agent 3: Credibility + References** | Pass 4 | Verify all references via web search, misconceptions, real-system connections |
| **Agent 4: Visuals** | Pass 6 | Visual density audit, hero visual, generate/find missing diagrams |

Each agent reads the post and the relevant sub-skill (polish-hooks, polish-math, polish-visuals). Each returns exact `old_string → new_string` edit pairs. Apply edits after all 4 return.

**Never do passes one-at-a-time.** Parallelism is the default, not an optimization.

## Target Audiences

1. **ML Engineers** — Practical insights without reading full papers
2. **PhD Students** — Intuition behind derivations
3. **Software Engineers** — Accessible explanations
4. **Founders/PMs** — High-level insights
5. **Hobbyists** — Why techniques work

## Mathematical Content

- Intuition BEFORE math ("here's what we're trying to show...")
- **Define ALL variables immediately after equations** (e.g., "Here $s$ is the **state**, $a$ is the **action**")
- Add inline comments in derivations: `&& \text{(reason)}`
- For complex proofs, add "Proof sketch" first
- Use analogies liberally

### Notation Consistency

- Same concept = same symbol throughout
- Consistent subscript/superscript placement
- Verify parentheses, signs, indices
- Check boundary conditions are consistent

### Equation Colors (key equations only)

| Color | Role | Example |
|-------|------|---------|
| Blue | Output/loss | $\textcolor{blue}{\mathcal{L}}$ |
| Green | Target/data | $\textcolor{green}{y}$ |
| Purple | Learned/predicted | $\textcolor{purple}{f_\theta}$ |
| Orange | Input/noise | $\textcolor{orange}{\epsilon}$ |
| Red | Penalty/constraint | $\textcolor{red}{R(\theta)}$ |

Color 2-4 terms max. Always add prose explanation after.

## Structure & Flow

- Each section answers: "Why do I care?"
- Add transitions between sections
- **Bold** key terms when first introduced
- Break long derivations with explanatory text

### Cross-References (Quarto)

```markdown
$$ equation $$ {#eq-name}     →  [-@eq-name]
![caption](img){#fig-name}    →  @fig-name
## Section {#sec-name}        →  @sec-name
```

Link to prior posts: `[Part 3](../3-probability-paths/)`

### Callouts

| Type | Use For |
|------|---------|
| `callout-note` | TL;DR, Definitions, Collapsible derivations |
| `callout-tip` | Theorems, Intuitions, Examples |
| `callout-warning` | Pitfalls, Caveats |
| `callout-important` | Critical insights |

**TL;DR (top of post):** Preview — help readers decide to read
```markdown
::: {.callout-note appearance="simple"}
## TL;DR
- **The problem**: [One line]
- **The solution**: [One line]
- **The result**: [Numbers]
:::
```

**Summary (end of post):** Consolidation — what we accomplished, what's next
```markdown
::: {.callout-note appearance="simple"}
## Summary
We showed X, which means Y. The key insight was Z. Next: [link to Part N].
:::
```

## Practical Value

Every post must answer: "What can I DO with this?"

- Connect to real systems (Stable Diffusion, Sora, LeRobot)
- Include "When to use this" and "When NOT to use this"
- Link to implementations/code when available

## Research Credibility

- Cite with superscripts: `$^{[1]}$`
- **Verify references** via web search before adding
- Every reference = clickable link (arXiv, proceedings)
- Add "Common Misconceptions" callouts
- Acknowledge limitations honestly

## Accessibility

Write for a brilliant but exhausted PhD student at 2am. No skipped steps. No implicit context.

- Define jargon on first use
- Add "Recall that X means..." for prior concepts
- Use second person: "Notice that...", "You might wonder..."

## Avoiding AI Language

**Avoid**: delve, utilize, harness, pivotal, seamless, groundbreaking, leverage, crucial
**Avoid phrases**: "Let's dive in", "It's worth noting", "Furthermore", "In conclusion"
**Never use em dashes** (—): replace with commas, colons, parentheses, or restructure the sentence.
**Do**: Use contractions inconsistently, vary paragraph length, include fragments, be specific

## Task Passes

### Pass 0: Research
- [ ] Search how others explain the same concept
- [ ] Note good analogies, visualizations, framings

### Pass 1: Content Scope
- [ ] Is the post trying to cover too much? (> 3000 words often signals this)
- [ ] Are there self-contained sections that could be standalone posts?
- [ ] Would extracting content improve focus and depth?
- [ ] Flag candidates: background/prerequisites, tangential deep-dives, appendix-like sections

**Extract when:** A section is self-contained, has its own "why do I care?", and removing it improves focus.
**Keep when:** The section is essential context or the payoff comes from seeing it alongside other content.

### Pass 2: Structure

- [ ] Add TL;DR callout at top
- [ ] Ensure each section answers "Why do I care?"
- [ ] Add transitions between sections
- [ ] Add cross-references

### Pass 3: Math Polish

- [ ] Intuition BEFORE each equation
- [ ] Define all variables after equations
- [ ] Check notation consistency
- [ ] Verify parentheses, signs

### Pass 4: Credibility
- [ ] Add References section (verify via web search)
- [ ] Include "Common Misconceptions"
- [ ] Connect to real systems
- [ ] Verify all dates/timestamps against current date (check env: `Today's date`)

### Pass 5: Hooks (from `/polish-hooks`)

- [ ] Opening uses PAS framework (Problem → Agitate → Solution)
- [ ] Title follows working patterns ("Why X Fails", "How Y Fixed Z")
- [ ] Social proof early (citations, who's using it)
- [ ] TL;DR is scannable (10 seconds)
- [ ] Read opening aloud — rewrite if you stumble

### Pass 6: Visuals (from `/polish-visuals`)

- [ ] Visual density audit (target: 1 image per 100-200 lines)
- [ ] Hero visual in first screen (before scroll)
- [ ] Check official paper assets before generating (project pages, arXiv HTML, GitHub)
- [ ] Equation-heavy sections have diagrams
- [ ] All generated images verified for quality

**Red flags:**

- ❌ 200+ lines without a visual
- ❌ "Imagine..." without an actual picture
- ❌ Key equation without preceding intuition diagram

### Pass 7: Math Visuals (from `/polish-math`)

**Professional standard: 1–2 colors per equation, only on the term that carries the new insight.**

- [ ] Identify the 1-3 "thesis" equations the post is fundamentally about
- [ ] Per equation: identify ONE concept to highlight — color only that (1–2 terms max)
- [ ] Use `\underbrace` to name conceptual chunks (e.g., "oscillation" vs "forcing") — not individual symbols
- [ ] Wrap the single most critical subterm in `\bbox[border: 2px dashed orange]{}` (once per post)
- [ ] Use `\boxed{}` for the key result of a derivation (one per section, no color inside)
- [ ] Add prose legend only if variables aren't defined in adjacent text/table
- [ ] Structural scaffolding (I, Δt, bias terms) stays black
- [ ] Check colorblind safety: no red+green pairs
- [ ] Verify `\bbox` renders with `quarto preview` (MathJax only, not KaTeX)

**Only apply to posts with ≥ 3 key equations. Skip for mostly-prose posts.**

Do NOT change mathematical content — only improve exposition.
