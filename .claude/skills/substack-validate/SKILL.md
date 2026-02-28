---
name: substack-validate
description: Validate a published Substack post against its source QMD file. Checks for missing content, broken equations, missing images, and formatting issues.
---

# Substack Validation Skill

Validate a published Substack post by converting it back to Markdown and comparing against the source `_substack.qmd`.

## Quick Start

```bash
# Option 1: Fetch from URL and compare
python .claude/skills/substack-validate/compare_md.py \
    posts/robotics/1-diffusion-policy/_substack.qmd \
    --url https://aheadofrobotics.substack.com/p/...

# Option 2: Convert first, then compare
python .claude/skills/substack-validate/substack_to_md.py \
    https://aheadofrobotics.substack.com/p/... \
    -o /tmp/converted.md

python .claude/skills/substack-validate/compare_md.py \
    posts/robotics/1-diffusion-policy/_substack.qmd \
    /tmp/converted.md
```

## How It Works

```text
Published Substack post
        ↓
   [fetch HTML]
        ↓
   [html → markdown]        _substack.qmd
        ↓                        ↓
   converted.md    ←→    [normalize both]
        ↓                        ↓
    [compare: find issues + generate diff]
        ↓
   Validation Report
```

**Key insight**: Converting Substack back to Markdown enables direct MD ↔ MD comparison, which is much more reliable than comparing against accessibility snapshots.

## Tools

### `substack_to_md.py`

Fetches a Substack post and converts it to Markdown.

```bash
python substack_to_md.py URL [-o output.md] [--include-metadata]
```

**Output**: Clean markdown with:

- Headings preserved
- Images as `![alt](substackcdn-url)`
- Blockquotes preserved
- Lists preserved

### `compare_md.py`

Compares source QMD against converted markdown.

```bash
python compare_md.py source.qmd converted.md
python compare_md.py source.qmd --url https://...
```

**Checks**:

1. **Orphaned punctuation** — Single-char lines (`.`, `?`, `:`)
2. **Callout formatting** — Run-together patterns (`NoteTL;DR`)
3. **Content diff** — Line-by-line differences

## Example Output

```text
======================================================================
SUBSTACK VALIDATION REPORT
======================================================================

Source: posts/robotics/1-diffusion-policy/_substack.qmd
Source lines: 1063
Converted lines: 245

======================================================================
ORPHANED PUNCTUATION
======================================================================

❌ Line 9: Orphaned '.'
   Context:
   | ...outperformed everything before it by 46.9%
   |
   | .
   |
   | [![](https://substackcdn.com/image/...

❌ Line 39: Orphaned '?'
   Context:
   | ...What does a standard neural network trained with MSE loss learn
   |
   | ?

======================================================================
CALLOUT FORMATTING ISSUES
======================================================================
❌ Line 15: NoteTL;DR...
❌ Line 43: WarningThe Averaging Disaster...
❌ Line 83: TipIntuition: From Images to Actions...

======================================================================
SUMMARY
======================================================================
❌ FAIL - 11 formatting issues found
```

## What Gets Detected

| Issue                | Pattern                            | Example               |
|----------------------|------------------------------------|-----------------------|
| Orphaned punctuation | Line contains only `.` `?` `:` `,` | `?` on its own line   |
| Callout run-together | `**(Note\|Warning\|Tip)[A-Z]`      | `**NoteTL;DR**`       |
| Missing content      | Diff shows deletions               | Section not published |
| Extra content        | Diff shows additions               | Unexpected text added |

## Workflow

### 1. After Publishing

```bash
# Validate the published post
python compare_md.py _substack.qmd --url https://...
```

### 2. If Issues Found

**Orphaned punctuation** → Fix in `_substack.qmd`:

- Don't end paragraphs with `?` or `:` before images
- Add continuation text after punctuation
- Re-publish

**Callout formatting** → Fix in `_substack.qmd`:

- Add explicit separators: `## 📝 Note: Title` instead of `## Title`
- Re-publish

**Missing content** → Check paste process:

- Substack may have truncated during paste
- Re-paste in smaller chunks

## Dependencies

```bash
pip install requests beautifulsoup4 markdownify pyyaml
```

## Limitations

- Substack renders some markdown differently (superscripts, footnotes)
- Images become CDN URLs (compared by position, not path)
- Multi-part posts: Source may be longer than single published post
- LaTeX equations render as images (can't compare math content directly)

## Future Improvements

- Semantic comparison (ignore formatting, compare meaning)
- Image content comparison (visual diff)
- Automatic fix suggestions
- Integration with `/substack-publish` for pre-publish validation
