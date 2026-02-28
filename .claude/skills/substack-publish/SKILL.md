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

**Option A: With CDN Upload (Recommended)**

```bash
# Set credentials in .env file:
# SUBSTACK_COOKIES="substack.sid=..."

# Generate HTML with images uploaded to Substack CDN
.venv/bin/python .claude/skills/substack-publish/qmd_to_substack.py posts/diffusion/3-probability-paths/_substack.qmd --upload
```

This uploads all images (both regular images and equation PNGs) to Substack's CDN. The generated HTML contains CDN URLs that work when pasting to Substack.

**Option B: Direct API Publish (Recommended for automation)**

```bash
# Create a draft directly on Substack (no copy-paste needed)
.venv/bin/python .claude/skills/substack-publish/qmd_to_substack.py posts/diffusion/3-probability-paths/_substack.qmd --publish --draft

# Publish immediately (not recommended - review draft first)
.venv/bin/python .claude/skills/substack-publish/qmd_to_substack.py posts/diffusion/3-probability-paths/_substack.qmd --publish
```

This uploads all images to Substack CDN and creates a draft via API. No copy-paste needed.

**What works:**
- Images upload and display correctly
- **Native LaTeX equations** with consistent sizing (uses Substack's built-in LaTeX renderer)
- Text formatting (bold, italic, headings)
- **Callouts rendered as blockquotes** with proper styling (not just plain text)
- LaTeX inside callouts works correctly

**Notes:**
- Creates draft by default with `--draft` flag
- Review draft before publishing
- Citations like `<sup>1</sup>` convert to Unicode superscripts (¹²³⁴⁵⁶⁷⁸⁹⁰)
- Native LaTeX uses `latex_block` nodes for consistent equation sizing

### ⚠️ Video Upload Limitation

**Problem**: Substack has no public API for video upload. Videos in your QMD file cannot be uploaded automatically.

**What happens:**

- The script detects Quarto video shortcodes: `{{< video filename.mp4 >}}`
- Videos are replaced with placeholders: `**[VIDEO 1: filename.mp4]**`
- Instructions are printed for manual upload

**Manual video upload steps:**

1. Open the draft/post in Substack editor
2. Find the placeholder text: `**[VIDEO N: filename.mp4]**`
3. Delete the placeholder text
4. Click the + button or type `/` to open insert menu
5. Select **Video** from the menu
6. Upload the video file from your computer
7. Wait for processing (~30-60 seconds per video)
8. Save the draft/post

**Supported video formats**: 3GP, AAC, AVI, FLV, MP4, MOV, MPEG-2 (max 20GB recommended)

**Alternative**: Upload videos to YouTube first, then use Substack's **Embed** option to embed the YouTube video.

**Option C: Local Server (Manual)**

```bash
.venv/bin/python .claude/skills/substack-publish/qmd_to_substack.py posts/diffusion/3-probability-paths/_substack.qmd
```

**Output**: The script generates:

- `_substack_substack.html` in the same directory as the QMD file
- `eq_*.png` files for any LaTeX equations (downloaded from CodeCogs)

### Step 2: Serve HTML (Only needed without --upload)

**Skip this step if you used `--upload`**. The HTML already has CDN URLs.

If you didn't use `--upload`, you must serve the HTML from a local server:

**CRITICAL**: HTML must be served from the post directory for images to load correctly. The HTML uses relative paths like `src="teaser.png"` and `src="eq_abc123.png"`.

Start a local server in the post directory:

```bash
cd posts/diffusion/3-probability-paths && python -m http.server 8765
```

Then open: `http://localhost:8765/_substack_substack.html`

**Why this matters**:

- Images use relative paths (not base64 or absolute paths)
- The server must run from the same directory as the images
- Running from `/tmp` or `posts/` will cause images to fail loading

### Step 3: Create Substack Post

1. Go to [Substack Dashboard](https://aheadofrobotics.substack.com/publish/home)
2. Click **"Create new"** → **"Text post"**

### Step 4: Paste Content

**Title & Subtitle:**
- Copy title from frontmatter `title:` field → paste into Substack's **Title** field
- **REQUIRED**: Add `subtitle:` to frontmatter before publishing. Generate a compelling 1-line hook:
  - "How neural networks learn to transform random noise into stunning images"
  - "The mathematical trick that makes training 1000x more efficient"
  - "Foundation models finally worked. Data is now the bottleneck."

  The script will warn if no subtitle is found.

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

### Step 5: Add Subscribe Buttons

Add 1-3 CTAs to encourage subscriptions. Use the **Button** menu in the toolbar.

**Button types:**

| Type | Use case |
|------|----------|
| **Subscribe w/ caption** | Primary — adds email box + customizable text |
| Subscribe | Minimal — just the button |
| Share post | After high-value content |

**Placement:**

| Position | When to use |
|----------|-------------|
| After TL;DR | Early capture — readers already see value |
| Mid-post (after key insight) | Natural pause |
| End of post | Standard — readers who finished are engaged |

**Workflow:**

1. Position cursor where you want the button
2. Click **Button** in toolbar
3. Select **Subscribe w/ caption**
4. Edit the caption text (default is generic)

**Better captions:**

- "Want more deep dives on robotics research? Subscribe for weekly breakdowns."
- "This is Part 3 of a 12-part series. Subscribe to get the rest."
- "Next week: how to actually implement this. Subscribe so you don't miss it."

**Rule of 3**: Maximum 3 CTAs per post. More feels spammy.

### ⚠️ CRITICAL: "Post Too Long" Error

**Problem**: "Your post is too long and can't be saved" error can occur when images fail to upload properly.

**How images work now**:

- HTML uses relative image paths (e.g., `src="teaser.png"`)
- When you open HTML in browser with local server running, images load
- When you copy-paste to Substack, it automatically uploads loaded images
- If local server isn't running, images won't load → paste fails or includes broken placeholders

**Symptoms:**

- Post appears short but won't save
- "IMAGE NOT FOUND" text visible where images should be
- Images show as broken/missing in Substack editor

**Solution:**

1. **Ensure local server is running** in the post directory before opening HTML
2. **Verify images load** in browser before copying
3. **Delete broken placeholders** if any — click and delete
4. **Manually upload images** via Substack's Image button if needed

**Prevention**: Always verify images display correctly in the browser before copying to Substack.

### ⚠️ Image Upload Verification

Images can silently fail to upload during paste.

**After EVERY paste:**
1. Scroll through entire content
2. Check ALL images display correctly (no "IMAGE NOT FOUND" text)
3. If broken, delete the placeholder and manually re-upload

**Fix broken images manually:**

1. Click on the broken image placeholder
2. Delete it
3. Position cursor where image should go
4. Click **Image** in toolbar → **Image**
5. Upload the image file from your local disk
6. Save the post

**Fix broken images with Playwright:**

```text
1. browser_navigate(url="https://aheadofrobotics.substack.com/publish/post/...")
2. browser_snapshot() → Find the broken image location
3. browser_click(ref=broken_image_ref)  # Select broken image
4. browser_press_key(key="Delete")  # Delete it
5. browser_click(ref=image_button_ref)  # Click Image in toolbar
6. browser_click(ref=image_menu_item_ref)  # Click "Image" in dropdown
7. browser_file_upload(paths=["posts/diffusion/10-diffusion-transformers/image.png"])
8. browser_click(ref=update_button_ref)
9. browser_click(ref=update_now_ref)
```

### ⚠️ SVG to PNG Conversion

**Problem**: Substack doesn't reliably render SVGs. Convert to PNG before uploading.

**CRITICAL**: Do NOT use ImageMagick `convert` for complex SVGs with embedded base64 images — it silently produces blank/corrupt output.

**Use cairosvg instead:**

```bash
# Install if needed
pip3 install cairosvg

# Convert with 2x scale for retina displays
python3 -c "import cairosvg; cairosvg.svg2png(url='image.svg', write_to='image.png', scale=2)"
```

**Verification checklist:**
1. Check output file size — if suspiciously small (<50KB for a complex diagram), it's likely corrupt
2. Open the PNG and verify content is visible
3. Expected sizes: simple diagram ~50-200KB, complex multi-panel ~300-500KB

**Why ImageMagick fails:**
- SVGs with embedded `<image xlink:href="data:image/png;base64,...">` tags
- ImageMagick doesn't properly decode and composite embedded base64 images
- Produces blank white output with no error message

## Updating an Existing Post

1. **Regenerate HTML** from the updated `_substack.qmd`:

   ```bash
   .venv/bin/python .claude/skills/substack-publish/qmd_to_substack.py posts/diffusion/2-flows/_substack.qmd
   ```

2. **Start local server** in the post directory:

   ```bash
   cd posts/diffusion/2-flows && python -m http.server 8765
   ```

3. **Open HTML in browser**: `http://localhost:8765/_substack_substack.html`

4. **Reload browser tab** (avoid stale cached content)

5. **Navigate to post** in Substack:
   - Go to [Published posts](https://aheadofrobotics.substack.com/publish/posts/published)
   - Click post → ellipsis menu (⋮) → **Edit**

6. **Replace content**:
   - In browser: Select All (Ctrl+A) → Copy
   - In Substack: Click body → Select All → Paste

7. **Delete heading/author lines** at top:
   - Ctrl+Home → Shift+Down → Delete
   - Repeat for author/date line

8. **Save**: Click **Update** → **Update now**

9. **Cleanup**: Delete the HTML file and equation images

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
   rm posts/diffusion/3-probability-paths/_substack_substack.html
   ```

2. **Delete generated equation images** (if any):

   ```bash
   rm posts/diffusion/3-probability-paths/eq_*.png
   ```

3. **Keep the `_substack.qmd` file** — needed for cross-linking

4. **Update `substack_url`** in frontmatter with the published URL

**Why cleanup matters:**

- HTML and equation images are regenerated on demand
- Only `_substack.qmd` needs version control
- Equation images are downloaded fresh each time (ensures latest rendering)
