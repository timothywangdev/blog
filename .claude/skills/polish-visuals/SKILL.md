---
name: polish-visuals
description: Images, diagrams, and visual density
---

# Visual Polish

Add and optimize images, diagrams, and visual aids.

**Use with:** `/polish` (core workflow)

## Images vs Videos: Prioritize Images

| Factor | Images | Videos |
|--------|--------|--------|
| Cross-platform | ✅ Works everywhere | ⚠️ Medium has no MP4 |
| Storage | ✅ Small files | ⚠️ GitHub Pages bandwidth |
| Loading | ✅ Fast | ⚠️ Slow, may not autoplay |
| Effort | ✅ Save and embed | ⚠️ YouTube upload needed |

**Use videos only for:** Motion/interaction demos that can't be captured in a still.

## Hero Visual (First Screen)

Place a striking visual **before readers scroll**. It should show the **problem** or **key insight**.

| Type | When to use |
|------|-------------|
| Problem visualization | Failure is vivid (robot crashing) |
| Before/after comparison | Improvement is dramatic |
| Key insight diagram | One visual captures the "aha" |
| Results at a glance | Numbers tell the story |

**Don't use:** Generic AI art, decorative images, complex diagrams needing explanation.

## Official Paper Assets First

Before generating, check:

1. **Project pages** — Search `[paper name] project page`
2. **arXiv HTML** — `arxiv.org/html/[paper-id]`
3. **GitHub repos** — `/assets`, `/figures`, `/docs` folders

**Why official is better:** Accurate, high quality, credible, legal, time-saving.

**How to use:**
- Download locally (don't hotlink)
- Attribute: "Figure from [Paper Name], Chi et al. 2023"

**Finding videos:** Use Playwright browser tools — many sites load videos via JavaScript. Run `browser_navigate` then `browser_evaluate` to query DOM.

## Visual Density Targets

| Content type | Target |
|--------------|--------|
| Math-heavy | 1 image per 100-150 lines |
| Conceptual | 1 image per 150-200 lines |
| Tutorial | 1 image per major step |

**Red flags:**
- ❌ Post with 0 images
- ❌ 200+ lines without a visual
- ❌ Equation-heavy section with no diagram
- ❌ "Imagine..." without an actual picture
- ❌ ASCII art diagrams — always use real images or remove entirely

## Where Visuals Are Mandatory

1. Before key equations (diagram showing intuition)
2. At problem introduction (show the failure)
3. For interpolation/transformation (before → after)
4. For comparisons (side-by-side)
5. For geometric concepts (vector fields, flows)

## Generating Images (when official unavailable)

Use `gemini-image` MCP tool. Save in post directory with descriptive filename.

**Style requirements (academic paper figures):**
- Clean vector-style, NOT photorealistic AI art
- Simple geometric shapes, flat colors, thin outlines
- Clear sans-serif labels on all components
- No gradients, 3D effects, glossy rendering

**Quality control:**
1. Inspect generated image
2. Verify labels are correct
3. Check mathematical correctness (arrow directions, signs)
4. If it looks AI-generated, regenerate with: "clean vector-style technical illustration, academic paper figure, simple flat design"

## SVG to PNG Conversion

**When to convert:** Substack requires PNG/JPG — always convert SVGs before publishing.

### Use cairosvg, NOT ImageMagick

ImageMagick's `convert` silently fails on SVGs with embedded base64 images (common in paper figures). It produces blank/corrupt output with no error.

```bash
# Install
pip3 install cairosvg

# Convert with 2x scale for retina
python3 -c "import cairosvg; cairosvg.svg2png(url='image.svg', write_to='image.png', scale=2)"
```

**Verification:**

| Check | Expected |
|-------|----------|
| File size | Complex diagram: 300-500KB. If <50KB, likely corrupt |
| Visual | Open and verify content is visible |
| Dimensions | Should match SVG viewBox × scale factor |

## Video Embedding (if needed)

**Quarto blog:**
```markdown
{{< video demo.mp4 width="100%" >}}
```

**YouTube (cross-platform):**
```markdown
{{< video https://www.youtube.com/watch?v=VIDEO_ID >}}
```

## Task

- [ ] Audit visual density (lines ÷ images — if >200:1, add visuals)
- [ ] Add hero visual in first screen
- [ ] Check for official paper assets before generating
- [ ] Generate diagrams for equation-heavy sections
- [ ] Verify all generated images for quality and correctness

**Quick audit example:**
- 400 lines, 2 images → 200:1 → borderline, add 1-2 more
- 300 lines, 4 images → 75:1 → good
