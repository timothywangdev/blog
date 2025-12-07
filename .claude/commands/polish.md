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

- Cite original papers — add a **References** section at the end of the post
- **Verify references**: Use web search to find correct paper titles, authors, venues, and years. Confirm citations actually exist and are accurate before adding them.
- **Include links**: Every reference should be a clickable link (arXiv, conference proceedings, or official paper page). Format as: `[Paper Title](url). *Venue Year*.`
- Acknowledge limitations and open questions honestly
- Add "Common Misconceptions" callouts to show deep expertise
- Distinguish between established results vs. author's interpretation/intuition

### Structure & Flow
- Each section should answer: "Why do I care about this?"
- Add transition sentences between sections explaining the logical flow
- Use **bold** for key terms when first introduced
- Break long derivations into digestible chunks with explanatory text between

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

- Look for `[helpful image needed]` placeholders and generate illustrations using the `gemini-image` MCP tool
- Save generated images in the same directory as the post (e.g., `posts/diffusion/1-intro/diagram.png`)
- **Inspect after generation**: Read/view the generated image to verify:
  - Correct labels and clear visualization
  - **Mathematical correctness**: Arrow directions, signs, relationships must be accurate (e.g., positive divergence = arrows pointing outward, not inward)
  - Matches the concept being explained
- If not satisfactory, regenerate with an improved prompt. Repeat until the image is suitable.
- Add diagrams for abstract concepts (vector fields, probability flows, transformations)
- Use illustrations to show intuition that's hard to convey in text alone

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

- [ ] Generate illustrations for `[helpful image needed]` placeholders
- [ ] Inspect each generated image for visual quality AND mathematical correctness
- [ ] Regenerate any images that have incorrect directions, signs, or relationships
- [ ] Verify title and headers are descriptive/searchable

Do NOT change the mathematical content itself — only improve exposition.
