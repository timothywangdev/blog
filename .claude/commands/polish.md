# Polish Documentation

Polish the current document to make it accessible and engaging for our target audiences.

## Target Audiences (in priority order)

1. **ML Engineers & Applied Researchers** - Need practical insights without reading full papers
2. **PhD Students & Academic Researchers** - Want intuition behind derivations, not just formulas
3. **AI-Curious Software Engineers** - Intimidated by math, want accessible explanations
4. **Founders & Product Managers** - Need high-level "what does this mean" insights
5. **Hobbyists & Fine-tuners** - Want to understand why techniques work

## Polishing Guidelines

### Mathematical Content
- Every equation should have intuition BEFORE the math ("here's what we're trying to show...")
- Add inline comments explaining each step in derivations using `&& \text{(reason)}`
- When introducing new notation, immediately give a one-sentence plain English meaning
- For complex proofs, add a "Proof sketch" or "Key idea" before diving into details
- Use analogies liberally (e.g., "think of it like...")

### Mathematical Rigor & Notation Consistency

- **Check notation consistency**: Ensure the same concept uses the same symbol throughout (e.g., don't mix $v_\theta$ and $u_\theta$ for the same thing)
- **Subscript/superscript conventions**: Be consistent with placement (e.g., $u_t^\theta$ vs $u_\theta^t$)
- **Verify parentheses**: Check for missing/mismatched parentheses in equations (e.g., `p_t{x}` should be `p_t(x)`)
- **Function arguments**: Be consistent about whether time is a subscript or argument (e.g., $u_t(x)$ vs $u(x, t)$)
- **Check equation correctness**: Verify signs, indices, and mathematical operations are correct
- **Boundary conditions**: Ensure stated conditions (e.g., $t=0$, $t=1$) are consistent throughout
- **Cross-reference accuracy**: Verify theorem/equation references point to the correct items

### Research Credibility

- **Only cite papers that are explicitly referenced in the text** using superscript notation (e.g., `$^{[1]}$` or `$^{[Ho2020]}$`)
- Add a **References** section at the end ONLY if there are superscript citations in the document
- **Verify references**: Use web search to find correct paper titles, authors, venues, and years. Confirm citations actually exist and are accurate before adding them.
- **Include links**: Every reference should be a clickable link (arXiv, conference proceedings, or official paper page). Format as: `[1] [Paper Title](url). *Venue Year*.`
- Acknowledge limitations and open questions honestly
- Add "Common Misconceptions" callouts to show deep expertise
- Distinguish between established results vs. author's interpretation/intuition

### Structure & Flow
- Each section should answer: "Why do I care about this?"
- Add transition sentences between sections explaining the logical flow
- Use **bold** for key terms when first introduced
- Break long derivations into digestible chunks with explanatory text between

### Cross-References & Links

Use Quarto cross-references to connect concepts within and across posts:

**Within a post:**

- **Equations**: Add labels `{#eq-name}` and reference with `[-@eq-name]` or `@eq-name`
- **Figures**: Add labels `{#fig-name}` and reference with `@fig-name`
- **Sections**: Add labels `{#sec-name}` and reference with `@sec-name`
- **Callouts with IDs**: Reference theorems/propositions with `[-@unique-id]`

**Across posts (within the series):**

- Link to previous posts when referencing prior concepts: `[Part 3](../3-probability-paths/)`
- Use descriptive link text: `as we derived in [Flow Matching Loss](../4-flow-matching-loss/)`
- When saying "recall that...", always link to where it was introduced

**Best practices:**

- Prefer clickable references over "see above" or "as shown earlier"
- When introducing notation defined elsewhere, link to its definition
- Cross-link related sections that readers might want to jump between

**Syntax examples:**

```markdown
$$ p_t(x) = \int p_t(x|z) p_{data}(z) dz $$ {#eq-marginal}

As shown in [-@eq-marginal], the marginal is...
Recall from [Part 3](../3-probability-paths/) that...
Using the result from [@conversion-formula]...
```

### Callout Style Guide

Use Quarto callouts consistently across all posts:

**Callout Types (by semantic meaning):**

| Type | Color | Use For | Example Header |
|------|-------|---------|----------------|
| `callout-note` | Blue | TL;DR, Definitions, Context, Collapsible derivations | `## TL;DR`, `## Definition: X` |
| `callout-tip` | Green | Theorems, Propositions, Lemmas, Key intuitions | `## Theorem: X`, `## Intuition: X` |
| `callout-warning` | Orange | Pitfalls, Caveats, "Watch out" moments | `## Common Pitfall`, `## Caution` |
| `callout-important` | Red | Critical insights, Must-not-miss points | `## Key Point`, `## Critical Insight` |

**Appearance Options:**

- `appearance="simple"` — Minimal styling, blends with text. Use for shorter notes, inline context.
- `appearance="default"` — Full border/styling. Use for major theorems/propositions that deserve emphasis.
- `collapse="true"` — Collapsible (click to expand). Use for optional derivations, lengthy proofs, or supplementary details.

**Best Practices:**

- **TL;DR**: Always use `{.callout-note appearance="simple"}` with `## TL;DR` header at the top of each post
  - Purpose: **Preview** — help readers decide if they want to read
  - Style: 2-4 bullet points summarizing *what you'll learn*
  - Tone: "Here's what this post covers..."

- **Summary**: Always use `{.callout-note appearance="simple"}` with `## Summary` header at the end of each post
  - Purpose: **Consolidation** — recap what was covered and connect to next steps
  - Style: Prose paragraphs (not just bullets), include key equations/formulas derived
  - Content: Reference specific results from the post, highlight the "aha" moments, preview what's next
  - Tone: "We proved X, which means Y. The key insight was Z. Next, we'll tackle..."
  - **IMPORTANT**: Summary should NOT look like TL;DR — it should feel like a "what we accomplished" reflection, not a preview
- **Theorems/Propositions**: Use `{#unique-id .callout-tip appearance="default"}` with an ID for cross-referencing
- **Definitions**: Use `{.callout-note appearance="simple"}` with `## Definition: X` header
- **Intuitions**: Use `{.callout-tip appearance="simple"}` with `## Intuition: X` header
- **Collapsible proofs**: Use `{.callout-note collapse="true"}` with `## Derivation of X` or `## Proof` header
- **Examples**: Use `{.callout-tip appearance="simple"}` with `## Example: X` header

**Syntax Example:**

```markdown
::: {#my-theorem .callout-tip appearance="default"}
## Theorem: Important Result
Content here...
:::
```

### Accessibility

::: {.callout-tip appearance="simple"}

## Guiding Mindset

Write as if explaining to a brilliant but exhausted PhD student at 2am. They can handle rigorous math — but don't make them work to follow your logic. No skipped "obvious" steps. No implicit context. If they have to re-read a sentence, you've failed.
:::

- Define jargon on first use
- Avoid assuming knowledge beyond basic calculus and probability
- When referencing prior concepts, add brief reminders (e.g., "Recall that X means...")
- Add "Intuition:" callouts for abstract concepts

### Engagement

- Use second person occasionally ("Notice that...", "You might wonder...")
- Pose and answer natural questions readers might have
- Highlight practical implications and connections to real systems (Stable Diffusion, Sora, etc.)

### TL;DR & Practical Value

- Add a TL;DR callout at the top summarizing key takeaways in 2-3 bullets
- Answer "What can I DO with this?" — connect to real systems (Stable Diffusion, Flux, Sora)
- Mention "When to use this" and "When NOT to use this" where applicable
- Link to companion coding posts if they exist

### Visual Aids

**When to add images** (proactively identify these, don't wait for placeholders):

- Abstract mathematical concepts that benefit from visualization (vector fields, probability flows, transformations)
- Comparisons between two approaches (e.g., ODE vs SDE sampling)
- Process diagrams showing sequential steps (e.g., forward/reverse diffusion)
- Geometric intuitions that are hard to convey in text alone
- Any place where a reader might think "I wish I could see this"

**How to generate:**

- Use the `gemini-image` MCP tool to generate illustrations
- Save images in the same directory as the post (e.g., `posts/diffusion/1-intro/diagram.png`)
- Use descriptive filenames (e.g., `score-function-vector-field.png`, not `fig1.png`)

**Quality control:**

- **Inspect after generation**: Read/view the generated image to verify:
  - Correct labels and clear visualization
  - **Mathematical correctness**: Arrow directions, signs, relationships must be accurate (e.g., positive divergence = arrows pointing outward, not inward)
  - Matches the concept being explained
- If not satisfactory, regenerate with an improved prompt. Repeat until the image is suitable.

### Discoverability

- Ensure title is specific and searchable (e.g., "Flow Matching Explained" not "Part 3")
- Write a compelling first paragraph — it may appear in search snippets
- Use descriptive H2/H3 headers for skimmability and SEO
- Add relevant categories/tags in frontmatter

## Task

Read the current file and apply these guidelines. Complete in order:

### Pass 0: Research

- [ ] Before modifying each major section, search online to see how others explain the same concept (blog posts, tutorials, lecture notes)
- [ ] Learn from effective explanations — note good analogies, visualizations, or framings you can adapt
- [ ] This ensures you're building on the best available pedagogy, not reinventing the wheel

### Pass 1: Structure & Clarity

- [ ] Add TL;DR callout at the top
- [ ] Ensure each section answers "Why do I care?"
- [ ] Add transitions between sections
- [ ] Add cross-references: link to prior posts, label key equations/theorems, replace "see above" with clickable refs

### Pass 2: Mathematical Polish

- [ ] Add intuition BEFORE each major equation
- [ ] Check notation consistency throughout
- [ ] Verify parentheses, signs, and cross-references

### Pass 3: Credibility & Value

- [ ] Add References section with paper citations (use web search to verify each citation is accurate)
- [ ] Ensure every reference is a clickable link (arXiv, proceedings, or official page)
- [ ] Include "Common Misconceptions" where relevant
- [ ] Connect to real systems and practical implications

### Pass 4: Visual & Discoverability

- [ ] Proactively identify where images would help (abstract concepts, comparisons, processes, geometric intuitions)
- [ ] Generate illustrations using `gemini-image` MCP tool
- [ ] Inspect each generated image for visual quality AND mathematical correctness
- [ ] Regenerate any images that have incorrect directions, signs, or relationships
- [ ] Verify title and headers are descriptive/searchable

Do NOT change the mathematical content itself — only improve exposition.
