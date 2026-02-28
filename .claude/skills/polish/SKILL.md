---
name: polish
description: Polish Documentation (core workflow)
---

# Polish Documentation

Polish the current document for clarity, mathematical rigor, and accessibility.

**Includes:** Hooks (engagement, titles) and Visuals (images, diagrams) as mandatory passes.

## Critical Requirements

- **Author name**: Always use `author: "Hujie Wang"` in frontmatter
- **Parallel research**: Launch 3-4 Task agents simultaneously, not sequentially

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

Do NOT change mathematical content — only improve exposition.
