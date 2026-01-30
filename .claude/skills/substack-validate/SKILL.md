---
name: substack-validate
description: Validate a published Substack post against its source QMD file. Checks for missing content, broken equations, missing images, and formatting issues.
---

# Substack Validation Skill

Compare a `_substack.qmd` file against its published Substack post to catch content issues.

## When to Use

Run this after publishing or updating a Substack post to verify:
- All content made it through the copy-paste workflow
- Equations rendered correctly (not showing raw LaTeX)
- Images are present and loading
- Callouts/blockquotes preserved their content
- No sections were accidentally truncated

## Arguments

Takes a path to a `_substack.qmd` file. The file must have a `substack_url` field in its frontmatter.

Example: `/substack-validate posts/diffusion/12-why-diffusion/index_substack.qmd`

## Validation Workflow

### Step 1: Extract Content from QMD

Read the `_substack.qmd` file and extract:

1. **Frontmatter**: Get `substack_url` for fetching the published post
2. **Section headings**: All `##`, `###`, `####` headings
3. **Block equations**: All `$$...$$` blocks
4. **Callouts**: All `::: {.callout-*}` blocks and their titles
5. **Images**: All `![alt](path)` references
6. **Code blocks**: All triple-backtick blocks
7. **Links**: All `[text](url)` references

### Step 2: Fetch Published Post with Playwright

Use Playwright MCP to fetch and analyze the published Substack post:

1. **Navigate to the post**: `browser_navigate` to the `substack_url`
2. **Take a snapshot**: Use `browser_snapshot` to get the accessibility tree — this provides structured content that's easy to analyze
3. **Extract content**: The snapshot includes all headings, paragraphs, images, links, and their hierarchy

**Why Playwright instead of WebFetch?**

- Substack uses JavaScript rendering — Playwright executes JS and gets the fully rendered page
- The accessibility snapshot provides structured content (headings, links, images) that's easy to compare
- Can detect if images failed to load or equations didn't render

**Example Playwright workflow:**

```text
1. browser_navigate(url=substack_url)
2. browser_snapshot() → Get accessibility tree with all content
3. Parse snapshot for: headings, images (alt text), links, blockquotes
```

### Step 3: Compare Content

Check for these issues:

#### Missing Sections
- Compare headings from QMD to headings in published post
- Flag any headings present in QMD but missing from Substack

#### Equation Issues
- **Raw LaTeX**: Look for `\frac`, `\mathbb`, `\alpha`, `\\begin{aligned}` etc. appearing as text (not rendered)
- **Missing equations**: Count block equations in QMD vs images in Substack (Substack renders LaTeX as images)
- **Broken renders**: Look for Substack error messages or placeholder text

#### Missing or Broken Images (CRITICAL)

**This is the #2 cause of validation failures after callout stripping.**

Images can silently fail to upload during paste. The image placeholder appears in the editor but the actual image never loads. You must verify EACH image:

**Detection in Accessibility Snapshot:**

```
# WORKING image:
figure [ref=eXXX]:
  link [ref=eYYY]:
    /url: https://substackcdn.com/image/fetch/...

# BROKEN/MISSING image:
- No figure element where image should be
- figure element with no substackcdn.com URL
- Empty figure element
```

**Validation Procedure:**

1. **Count images in QMD**: Count all `![alt](path)` references (excluding equation renders)
2. **Count figures in Substack**: Count `figure` elements in the accessibility snapshot
3. **Verify URLs**: Each figure should have a link to `substackcdn.com`
4. **Check placement**: Verify figures appear after the correct headings

**For EACH image in QMD:**

```
1. Note the preceding heading (e.g., "The ViT Architecture")
2. Find that heading in the Substack snapshot
3. Verify a figure element follows it (before the next heading)
4. Verify the figure has a substackcdn.com URL
```

**Red flags indicating broken images:**

- Image count mismatch (fewer figures in Substack than images in QMD)
- Heading followed directly by another heading or paragraph (no figure between)
- Figure element with no URL or non-substackcdn URL

**Fix for broken images:**

Use Playwright to upload the image manually:

1. Navigate to the post editor
2. Click where the image should go
3. Click Image button in toolbar → Image menu item
4. Use `browser_file_upload` with the local image path
5. Save the post

#### Callout/Blockquote Issues (CRITICAL)

**This is the most failure-prone check due to Substack's paste limitation bug.**

The paste limitation strips callout CONTENT while keeping callout TITLES. You must verify:

1. **Title exists**: Callout title (e.g., "💡 Intuition: The Scaling Problem") appears
2. **Content follows**: There are actual paragraphs AFTER the title, not just the title alone
3. **Key phrases present**: The first sentence or key phrase from the QMD callout body appears in Substack

**How to detect the paste limitation bug:**

- Callout title appears as bold text but is immediately followed by the next heading
- Multiple callout titles in sequence with no body content between them
- A callout that should have 3+ sentences shows only the title

**For EACH callout in the QMD:**

```
1. Extract: title, first sentence of body, approximate paragraph count
2. Find title in Substack snapshot
3. Verify: content exists AFTER the title (not just the title alone)
4. Check: key phrase from first sentence appears in the following content
```

**Red flags indicating stripped content:**

- Snapshot shows: `heading "💡 Intuition: Something"` → `heading "Next Section"`
- No `paragraph` or `blockquote` elements between callout title and next heading
- Callout appears as single bold line with no explanatory text below

#### Link Issues
- Verify external links are present
- Check cross-post links resolve to valid Substack URLs

### Step 4: Generate Report

Output a validation report with:

```
## Validation Report: [Post Title]

**Source**: posts/diffusion/12-why-diffusion/index_substack.qmd
**Published**: https://aheadofrobotics.substack.com/p/...
**Status**: ✅ PASS / ⚠️ WARNINGS / ❌ ISSUES FOUND

### Content Summary
- Sections: X found in QMD, Y found in Substack
- Equations: X block equations in QMD
- Images: X images referenced
- Callouts: X callouts found
- Links: X internal, Y external

### Issues Found

#### ❌ Critical Issues
[List any missing sections, broken equations, etc.]

#### ⚠️ Warnings
[List minor issues like missing images that couldn't transfer]

#### ✅ Verified
[List what was successfully validated]
```

## What to Check For

### Raw LaTeX Detection

Look for these patterns appearing as literal text (not rendered):

```
\frac{...}{...}
\mathbb{...}
\mathcal{...}
\begin{aligned}
\end{aligned}
\alpha, \beta, \theta (escaped)
\\nabla, \\partial
\|...\| (norm notation)
\underbrace{...}
\text{...}
```

If these appear as text in the published post, the equation didn't render.

### Substack LaTeX Rendering

Substack converts `$$...$$` blocks to images hosted on `substackcdn.com`. A properly rendered equation will appear as:

```html
<img src="https://substackcdn.com/image/fetch/..." alt="equation content">
```

### Content Truncation Patterns

Watch for:
- Callouts that end abruptly
- Lists that are shorter than in the QMD
- Missing "References" or final sections
- Code blocks cut off mid-content

### ⚠️ Substack Paste Limitation Bug (CRITICAL)

**This is the #1 cause of validation failures for long posts.**

**The Bug**: Substack's paste handler strips blockquote/callout CONTENT after approximately 5-6 callouts. The callout TITLES survive but the explanatory content inside is lost.

**Pattern in Accessibility Snapshot**:

```
# BROKEN (content stripped):
heading "💡 Intuition: The Scaling Problem" [level 4]
heading "Next Section Title" [level 2]     ← No content between!

# CORRECT (content preserved):
heading "💡 Intuition: The Scaling Problem" [level 4]
paragraph "Transformers were designed for sequences..."
paragraph "But images aren't sequences..."
heading "Next Section Title" [level 2]
```

**Validation Procedure**:

For posts with 5+ callouts, explicitly verify EACH callout has body content by checking the accessibility snapshot for `paragraph` elements between the callout heading and the next section heading.

**If content is missing**: The fix is to re-paste using the "paste in chunks" workaround documented in `/substack-publish`.

## Example Validation

**Input**: `posts/diffusion/12-why-diffusion/index_substack.qmd`

**Expected Output**:

```
## Validation Report: Diffusion & Flow Matching Part 12: Why Diffusion?

**Source**: posts/diffusion/12-why-diffusion/index_substack.qmd
**Published**: https://aheadofrobotics.substack.com/p/diffusion-and-flow-matching-part-9d9
**Status**: ✅ PASS

### Content Summary
- Sections: 15 found in QMD, 15 found in Substack
- Equations: 12 block equations in QMD, 12 equation images in Substack
- Images: 6 images referenced, 6 found in Substack
- Callouts: 8 callouts found, 8 verified in Substack
- Links: 4 internal cross-links, 15 external references

### Issues Found

#### ✅ Verified
- All 15 section headings present
- All 12 equations rendered as images
- All 8 callout blocks preserved with content
- All cross-links point to valid Substack URLs
- References section complete (15 citations)

#### ⚠️ Warnings
- None

#### ❌ Critical Issues
- None
```

## Automated Checks

The skill should programmatically verify:

1. **Heading count match**: `grep -c "^##" file.qmd` vs headings in fetched HTML
2. **Equation count**: `grep -c "^\$\$" file.qmd` (start of block) vs equation images
3. **Image count match**: Count `![` in QMD vs `figure` elements in snapshot — **MUST MATCH**
4. **Image URLs valid**: Every `figure` must have a `substackcdn.com` URL
5. **Callout content present**: For each callout heading, verify paragraphs follow before next heading
6. **Reference links**: Verify arxiv.org, github.com links are present

## Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Raw `\frac{...}` visible | Equation didn't render | Re-paste content, ensure `$$` are on their own lines |
| Missing section | Copy truncated | Re-copy from HTML, paste again |
| Missing image | Local path, not uploaded | Upload image to Substack manually |
| **Image placeholder but broken** | **Silent upload failure** | **Use Playwright to upload via Image button + `browser_file_upload`** |
| Broken cross-link | Missing `substack_url` | Update source QMD with URL, regenerate HTML |
| Callout missing title | Stripped during paste | Manually add the callout title back |
| **Callout title exists but content missing** | **Paste limitation bug** | **Use "paste in chunks" workaround (see /substack-publish)** |

### Second Most Critical Issue: Silent Image Upload Failures

Images can fail to upload during paste with **no error message**. The validation MUST:

1. Count images in QMD (exclude equation blocks)
2. Count `figure` elements in Substack snapshot
3. **FAIL validation if counts don't match**
4. For each figure, verify it has a `substackcdn.com` URL

### Most Critical Issue: Callout Content Stripping

For posts with 5+ callouts, the paste limitation bug is almost guaranteed to occur. **Always verify callout CONTENT, not just titles.** The validation should fail if:

- Callout title appears but no paragraphs follow before next heading
- Multiple callout titles appear in sequence without intervening content
- Total word count in a callout section is suspiciously low (< 20 words when QMD has 100+)
