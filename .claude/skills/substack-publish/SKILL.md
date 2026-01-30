---
name: substack-publish
description: Publish a rewritten Substack QMD file. Handles HTML generation, copy-paste workflow, and validation.
---

# Substack Publishing Workflow

Publish a `_substack.qmd` file to Substack. This skill handles:

1. **Cross-post linking**: Rewrite relative links to published Substack URLs
2. **HTML generation**: Convert to pasteable HTML format
3. **Publishing**: Copy-paste to Substack editor
4. **Validation**: Verify content transferred correctly

**Prerequisites**: Run `/substack-rewrite` first to create the `_substack.qmd` file.

## Cross-Post Linking

The converter automatically rewrites links to other posts in your series.

### How It Works

1. When you include links like `[Part 3](../3-probability-paths/)`, the converter looks for `index_substack.qmd` in that post's folder
2. If found, it reads the `substack_url` from the frontmatter
3. The link is rewritten to point to the Substack URL instead

### Workflow

1. **First post**: No cross-links to rewrite yet
2. **After publishing**: Update `substack_url` in the `_substack.qmd` frontmatter:

   ```yaml
   ---
   title: "Probability Paths"
   substack_url: "https://yourblog.substack.com/p/probability-paths"
   ---
   ```

3. **Subsequent posts**: Links to previously-published posts are automatically rewritten
4. **Missing URLs**: Warned but not failed — original relative links are preserved

## Publishing a New Post

### Step 1: Generate HTML

```bash
.venv/bin/python .claude/skills/substack-publish/qmd_to_substack.py posts/diffusion/3-probability-paths/index_substack.qmd
```

### Step 2: Open in Browser

Start local server (if not already running):

```bash
cd posts && python -m http.server 8765
```

Open the generated HTML (e.g., `http://localhost:8765/diffusion/3-probability-paths/index_substack.html`)

### Step 3: Create Substack Post

1. Go to [Substack Dashboard](https://aheadofrobotics.substack.com/publish/home)
2. Click **"Create new"** → **"Text post"**

### Step 4: Paste Content

**Title & Subtitle:**
- Copy title from frontmatter `title:` field → paste into Substack's **Title** field
- If no subtitle exists, generate a compelling 1-line hook:
  - "How neural networks learn to transform random noise into stunning images"
  - "The mathematical trick that makes training 1000x more efficient"

**Body:**
- Select content starting AFTER the title/author line in browser
- Paste into Substack editor

### ⚠️ CRITICAL: Paste Limitation for Long Posts

**Problem**: Substack's paste handler strips blockquote/callout content after ~5-6 callouts. Titles survive but content is lost.

**Symptoms:**
- Early callouts render correctly with full content
- Later callouts show only the title as bold text with no content below

**Workaround - Paste in Chunks:**

For posts with 5+ callouts:

1. **First paste**: Copy from TL;DR through ~5th callout → paste into Substack
2. **Second paste**: Position cursor at end → copy next chunk → paste
3. **Repeat** as needed

**Verification**: After pasting, scroll through and verify EVERY callout has content, not just titles.

### ⚠️ Image Upload Verification

Images can silently fail to upload during paste.

**After EVERY paste:**
1. Scroll through entire content
2. Check ALL images display correctly
3. If broken, use Playwright to re-upload

**Fix broken images with Playwright:**

```text
1. browser_navigate(url="https://aheadofrobotics.substack.com/publish/post/...")
2. browser_snapshot() → Find the broken image location
3. browser_click(ref=image_button_ref)  # Click Image in toolbar
4. browser_click(ref=image_menu_item_ref)  # Click "Image" in dropdown
5. browser_file_upload(paths=["posts/diffusion/10-diffusion-transformers/image.png"])
6. browser_click(ref=update_button_ref)
7. browser_click(ref=update_now_ref)
```

## Updating an Existing Post

1. **Regenerate HTML** from the updated `_substack.qmd`:

   ```bash
   .venv/bin/python .claude/skills/substack-publish/qmd_to_substack.py posts/diffusion/2-flows/index_substack.qmd
   ```

2. **Reload browser tab** (avoid stale cached content)

3. **Navigate to post** in Substack:
   - Go to [Published posts](https://aheadofrobotics.substack.com/publish/posts/published)
   - Click post → ellipsis menu (⋮) → **Edit**

4. **Replace content**:
   - In browser: Select All (Ctrl+A) → Copy
   - In Substack: Click body → Select All → Paste

5. **Delete heading/author lines** at top:
   - Ctrl+Home → Shift+Down → Delete
   - Repeat for author/date line

6. **Save**: Click **Update** → **Update now**

7. **Cleanup**: Delete the HTML file

## ⚠️ MANDATORY: Run Validation

**ALWAYS run `/substack-validate` after publishing or updating.**

```bash
/substack-validate posts/diffusion/10-diffusion-transformers/index_substack.qmd
```

This catches:
- **Broken images** (silent upload failures — #1 issue)
- **Missing callout content** (paste limitation bug)
- **Raw LaTeX** (equations that didn't render)
- **Missing sections** (content truncation)

**Do NOT skip validation.**

## Cleanup

After validation passes:

1. **Delete the generated HTML file**:

   ```bash
   rm posts/diffusion/3-probability-paths/index_substack.html
   ```

2. **Keep the `_substack.qmd` file** — needed for cross-linking

3. **Update `substack_url`** in frontmatter with the published URL

**Why cleanup matters:**
- HTML files are large (base64-encoded SVGs) and bloat the repo
- They're regenerated on demand
- Only `_substack.qmd` needs version control
