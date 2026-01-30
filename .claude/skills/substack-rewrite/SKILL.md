---
name: substack-rewrite
description: Rewrite a Quarto blog post for Substack by eliminating inline LaTeX (→ Unicode/prose) and converting tables to bullet lists.
---

# Substack Rewrite

Rewrite a Quarto blog post to eliminate inline LaTeX while preserving mathematical meaning. Outputs a Substack-compatible `_substack.qmd` file.

## The Problem

Substack only supports **block LaTeX** (centered equations). Inline math like `$x^2$` either:
- Renders as images on separate lines (breaks reading flow)
- Doesn't render at all in email newsletters

## Your Task

Given a QMD file path as argument, rewrite the content following these rules:

### 1. Convert Simple Symbols to Unicode/Text

| LaTeX | Convert To |
|-------|------------|
| `$\alpha$`, `$\beta$`, `$\theta$`, etc. | α, β, θ (Unicode) |
| `$x$`, `$y$`, `$z$` | *x*, *y*, *z* (italics) |
| `$x_0$`, `$x_t$` | *x*₀, *x*ₜ (Unicode subscripts) |
| `$x^2$` | *x*² (Unicode superscript) |
| `$t=0$`, `$t=1$` | t=0, t=1 (plain text) |
| `$\mathbb{R}^d$` | ℝᵈ |
| `$\mathcal{N}$` | 𝒩 or "normal distribution" |

### 2. Rewrite Math in Prose

Transform inline math into natural language when it improves readability:

**Before:**
> A **conditional probability path** $p_t(x|z)$ describes how probability mass moves from noise toward a *specific* target point $z$.

**After:**
> A **conditional probability path** describes how probability mass moves from noise toward a *specific* target point. We write this as *p*ₜ(*x*|*z*) — the distribution over *x* at time *t*, conditioned on target *z*.

**Before:**
> We obtain it by first sampling $z \sim p_{data}$ and then sampling $x \sim p_t(\cdot | z)$

**After:**
> We obtain it by first sampling *z* from the data distribution, then sampling *x* from the conditional path at time *t*.

### 3. Promote Important Equations to Block Math

If an inline equation is **important for understanding**, make it a block equation:

**Before:**
> The conditional vector field is $u_t^{\text{target}}(x | z) = (\dot{\alpha}_t - \frac{\dot{\beta}_t}{\beta_t} \alpha_t) z + \frac{\dot{\beta}_t}{\beta_t} x$

**After:**
> The conditional vector field is:
>
> $$u_t^{\text{target}}(x | z) = (\dot{\alpha}_t - \frac{\dot{\beta}_t}{\beta_t} \alpha_t) z + \frac{\dot{\beta}_t}{\beta_t} x$$

### 4. Keep Block Math Unchanged

Display math (`$$...$$`) stays as-is — Substack handles it well.

### 5. Simplify Notation When Appropriate

If a paragraph has many inline math expressions, consider:
- Introducing notation once, then using prose
- Grouping related expressions into a single block equation
- Adding a "where..." clause after block equations

**Before:**
> where $\dot{\alpha}_t = \frac{\partial \alpha_t}{\partial t}$ and $\dot{\beta}_t = \frac{\partial \beta_t}{\partial t}$ denote time derivatives

**After:**
> where the dots denote time derivatives (e.g., α̇ₜ = ∂αₜ/∂t)

### 6. Convert Tables to Bullet Lists

**Substack doesn't support tables.** Copy-pasting HTML tables results in jumbled, unreadable text. Convert all markdown tables to bullet lists.

**Series/Navigation tables** → Single bullet list with bold part numbers:

**Before:**

```markdown
| Part | Topic | Description |
|------|-------|-------------|
| Part 1 | Introduction | High-level overview |
| Part 2 | Flows | Vector fields and trajectories |
```

**After:**

```markdown
- **Part 1: Introduction** — High-level overview
- **Part 2: Flows** — Vector fields and trajectories
```

**Comparison tables** → Separate sections with labeled bullet lists:

**Before:**

```markdown
| Aspect | Method A | Method B |
|--------|----------|----------|
| Speed | Fast | Slow |
| Accuracy | Low | High |
```

**After:**

```markdown
**Method A:**

- **Speed:** Fast
- **Accuracy:** Low

**Method B:**

- **Speed:** Slow
- **Accuracy:** High
```

## Unicode Reference

### Greek Letters
α β γ δ ε ζ η θ ι κ λ μ ν ξ π ρ σ τ υ φ χ ψ ω
Γ Δ Θ Λ Ξ Π Σ Φ Ψ Ω

### Subscripts
₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉ ₐ ₑ ₕ ᵢ ⱼ ₖ ₗ ₘ ₙ ₒ ₚ ᵣ ₛ ₜ ᵤ ᵥ ₓ

### Superscripts
⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻ ⁿ ⁱ

### Math Symbols
∞ ∂ ∇ × · ± ≤ ≥ ≠ ≈ ≡ ∼ ∝ ∈ ∉ ⊂ ⊃ ∪ ∩ ∅ ∀ ∃ → ← ⇒ ⇐ ↦ ∫ Σ Π √ … ℝ ℕ ℤ

### Special
𝒩 (script N for normal distribution)

## Output

1. Read the input QMD file
2. Rewrite the content following these rules
3. **Add `substack_url: ""` to frontmatter** (placeholder for after publishing)
4. Save to `_substack.qmd` in the same directory as the input file
5. Report statistics:
   - Original inline math count
   - Converted to Unicode/text
   - Promoted to block math
   - Remaining inline (should be 0 or very few)

## Quality Guidelines

From `/polish`:
- Write as if explaining to a brilliant but exhausted PhD student at 2am
- They can handle rigor — but don't make them work to follow your logic
- Preserve all mathematical meaning
- Maintain the pedagogical flow
- Keep the "Intuition BEFORE math" structure
- Don't lose precision for the sake of simplicity

## Avoiding AI-Typical Language

Follow the full guidelines in `/polish` under "Avoiding AI-Typical Language". Key points:

- Replace flagged words: delve → explore, leverage/utilize/harness → use, crucial/pivotal → important
- Remove filler phrases: "It's important to note...", "Let's dive in", "Furthermore/Moreover"
- Reduce em-dashes: limit to 1-2 per paragraph, use commas or periods instead
- Vary sentence length and use contractions naturally
- Be specific: names and citations instead of "many researchers"

## Example Transformation

**Original:**
```markdown
The Gaussian probability path is defined as $p_t(\cdot | z) = \mathcal{N}(\alpha_t z, \beta_t^2 I_d)$ where $\alpha_t$ and $\beta_t$ are noise schedulers.
```

**Rewritten:**
```markdown
The Gaussian probability path is defined as a normal distribution centered at αₜ*z* with variance βₜ²:

$$p_t(\cdot | z) = \mathcal{N}(\alpha_t z, \beta_t^2 I_d)$$

Here αₜ and βₜ are the noise schedulers — smooth functions of time that control how quickly the distribution concentrates on the target.
```

## Next Step

After rewriting, use `/substack-publish` to generate HTML and publish to Substack.
