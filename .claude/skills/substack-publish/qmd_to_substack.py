#!/usr/bin/env python3
"""
QMD to Substack Converter

Converts Quarto .qmd files directly to Substack-compatible HTML with LaTeX
rendered as inline SVG images (base64 encoded for email compatibility).

Usage:
    python qmd_to_substack.py path/to/post/index.qmd [-o output.html]

    # Upload images to Substack CDN (recommended):
    python qmd_to_substack.py path/to/post/index.qmd --upload

    # Direct publish to Substack (no copy-paste needed):
    python qmd_to_substack.py path/to/post/index.qmd --publish
    python qmd_to_substack.py path/to/post/index.qmd --publish --draft  # Create draft only

Requirements (install in .venv):
    pip install requests beautifulsoup4 pyyaml markdown python-substack

Environment variables for --upload/--publish:
    SUBSTACK_EMAIL: Your Substack account email
    SUBSTACK_PASSWORD: Your Substack account password
    OR
    SUBSTACK_COOKIES: Cookies string from browser (semicolon-separated)
"""

import argparse
import base64
import hashlib
import mimetypes
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote
from html import escape as html_escape

try:
    import requests
    import yaml
    import markdown
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install requests pyyaml markdown")
    sys.exit(1)

# Optional: python-substack for CDN uploads and direct publishing
try:
    from substack import Api as SubstackApi
    from substack.post import Post as SubstackPost
    SUBSTACK_AVAILABLE = True
except ImportError:
    SUBSTACK_AVAILABLE = False


# Cache directory for rendered equations
CACHE_DIR = Path.home() / ".cache" / "qmd-to-substack"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Global Substack API instance (set when --upload is used)
_substack_api = None

# Cache for CDN URLs to avoid duplicate uploads
_cdn_url_cache: dict[str, str] = {}


def init_substack_api() -> bool:
    """
    Initialize Substack API client from environment variables.
    Returns True on success, False on failure.
    """
    global _substack_api

    if not SUBSTACK_AVAILABLE:
        print("❌ python-substack not installed. Run: pip install python-substack")
        return False

    email = os.environ.get('SUBSTACK_EMAIL')
    password = os.environ.get('SUBSTACK_PASSWORD')
    cookies = os.environ.get('SUBSTACK_COOKIES')

    if email and password:
        try:
            _substack_api = SubstackApi(email=email, password=password)
            print(f"✅ Authenticated with Substack as {email}")
            return True
        except Exception as e:
            print(f"❌ Substack authentication failed: {e}")
            return False
    elif cookies:
        try:
            _substack_api = SubstackApi(cookies_string=cookies)
            print("✅ Authenticated with Substack using cookies")
            return True
        except Exception as e:
            print(f"❌ Substack cookie authentication failed: {e}")
            return False
    else:
        print("❌ Missing Substack credentials.")
        print("   Set SUBSTACK_EMAIL + SUBSTACK_PASSWORD")
        print("   Or set SUBSTACK_COOKIES")
        return False


def upload_to_substack_cdn(image_path: Path, max_retries: int = 3) -> str | None:
    """
    Upload an image to Substack CDN and return the CDN URL.
    Uses a cache to avoid duplicate uploads.
    Returns None on failure.
    """
    import time
    global _substack_api, _cdn_url_cache

    if _substack_api is None:
        return None

    # Check cache first
    cache_key = str(image_path.resolve())
    if cache_key in _cdn_url_cache:
        return _cdn_url_cache[cache_key]

    # Upload with retry and rate limiting
    for attempt in range(max_retries):
        try:
            # Small delay to avoid rate limiting (100ms between uploads)
            time.sleep(0.1)
            result = _substack_api.get_image(str(image_path))
            # get_image returns {'id': ..., 'url': ...} - extract URL
            if isinstance(result, dict):
                cdn_url = result.get('url', str(result))
            else:
                cdn_url = str(result)
            # Cache the result
            _cdn_url_cache[cache_key] = cdn_url
            return cdn_url
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                # Rate limited - wait and retry with exponential backoff
                wait_time = 2 ** (attempt + 1)
                print(f"  ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  ⚠️  Failed to upload {image_path.name}: {e}")
                return None
    return None


def get_equation_hash(latex: str, display: bool) -> str:
    """Generate cache key for equation."""
    return hashlib.md5(f"{display}:{latex}".encode()).hexdigest()


def download_latex_image(latex: str, display: bool, output_dir: Path) -> str | None:
    """
    Download LaTeX equation as PNG image to local file.
    Returns relative filename (e.g., 'eq_abc123.png') or None on failure.
    """
    # Generate unique filename from latex hash
    eq_hash = get_equation_hash(latex, display)[:8]
    filename = f"eq_{eq_hash}.png"
    output_path = output_dir / filename

    # Check if already downloaded
    if output_path.exists():
        return filename

    # Download from CodeCogs
    dpi = 150 if display else 120
    latex_with_dpi = f"\\dpi{{{dpi}}} {latex}"
    encoded_latex = quote(latex_with_dpi)
    url = f"https://latex.codecogs.com/png.latex?{encoded_latex}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        output_path.write_bytes(response.content)
        return filename
    except Exception as e:
        print(f"  ⚠️  Failed to download equation: {latex[:30]}... - {e}")
        return None


def svg_to_data_uri(svg_content: str) -> str:
    """Convert SVG content to base64 data URI."""
    svg_content = svg_content.strip()
    b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"


def image_to_data_uri(image_path: Path) -> str | None:
    """Convert a local image file to base64 data URI."""
    if not image_path.exists():
        return None

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type:
        suffix = image_path.suffix.lower()
        mime_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
        }
        mime_type = mime_map.get(suffix, 'application/octet-stream')

    # Read and encode
    try:
        image_data = image_path.read_bytes()
        b64 = base64.b64encode(image_data).decode('utf-8')
        return f"data:{mime_type};base64,{b64}"
    except Exception as e:
        print(f"  ⚠️  Failed to read image {image_path}: {e}")
        return None


def process_images_for_substack(content: str, base_dir: Path, upload: bool = False) -> tuple[str, list, int]:
    """
    Process images for Substack.

    If upload=True: Upload to Substack CDN and replace paths with CDN URLs.
    If upload=False: Keep local paths (requires local server when pasting).

    Returns (processed_content, images_list, upload_count).
    """
    img_pattern = r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)'
    images_to_upload = []
    upload_count = [0]  # Use list for mutable counter in nested function

    def process_image(match):
        alt_text = match.group(1)
        img_src = match.group(2)

        # Skip URLs (already hosted)
        if img_src.startswith(('http://', 'https://')):
            return match.group(0)

        # Skip data URIs
        if img_src.startswith('data:'):
            return match.group(0)

        # Handle local images
        img_path = base_dir / img_src
        if not img_path.exists():
            print(f"  ⚠️  Image not found: {img_src}")
            return match.group(0)

        if upload and _substack_api is not None:
            # Upload to Substack CDN
            cdn_url = upload_to_substack_cdn(img_path)
            if cdn_url:
                upload_count[0] += 1
                print(f"  ✅ Uploaded: {img_path.name} → CDN")
                return f'![{alt_text}]({cdn_url})'
            else:
                # Upload failed, keep local path
                images_to_upload.append({
                    'path': str(img_path.resolve()),
                    'filename': img_path.name,
                    'alt': alt_text
                })
                return match.group(0)
        else:
            # Track for manual upload
            images_to_upload.append({
                'path': str(img_path.resolve()),
                'filename': img_path.name,
                'alt': alt_text
            })
            return match.group(0)

    processed = re.sub(img_pattern, process_image, content)
    return processed, images_to_upload, upload_count[0]


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and content from .qmd file."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            return frontmatter or {}, match.group(2)
        except yaml.YAMLError:
            pass
    return {}, content


def process_callouts(content: str, for_api: bool = False) -> str:
    """
    Convert Quarto callouts to blockquotes.

    Args:
        content: Markdown content with Quarto callout syntax
        for_api: If True, use special markers for API post-processing

    Returns:
        Content with callouts converted to blockquote syntax (or markers for API)
    """
    callout_pattern = r':::\s*\{\.callout-(\w+)(?:\s+[^}]*)?\}\s*([\s\S]*?):::'

    emojis = {
        'note': '📝',
        'tip': '💡',
        'warning': '⚠️',
        'important': '❗',
        'caution': '🔥',
    }

    callout_counter = [0]

    def replace_callout(match):
        callout_type = match.group(1)
        inner = match.group(2)
        emoji = emojis.get(callout_type, '📌')

        # Extract title if present (## Title format)
        title_match = re.match(r'^##\s*(.+?)\n([\s\S]*)$', inner.strip())
        if title_match:
            title = title_match.group(1).strip()
            body = title_match.group(2)
        else:
            title = callout_type.capitalize()
            body = inner

        if for_api:
            # Use special markers that will be converted to blockquote nodes
            callout_id = callout_counter[0]
            callout_counter[0] += 1
            # Format: marker, title, body content, end marker
            return f'\n%%CALLOUT_START_{callout_id}%%\n**{emoji} {title}**\n\n{body.strip()}\n%%CALLOUT_END_{callout_id}%%\n'
        else:
            # Format as blockquote for HTML output
            body_lines = body.strip().split('\n')
            quoted_body = '\n> '.join(body_lines)
            return f'\n> **{emoji} {title}**\n>\n> {quoted_body}\n'

    return re.sub(callout_pattern, replace_callout, content)


def get_substack_url(post_dir: Path) -> str | None:
    """
    Look up the substack_url from a post's _substack.qmd frontmatter.
    Returns the URL if found, None otherwise.
    """
    substack_qmd = post_dir / "index_substack.qmd"
    if not substack_qmd.exists():
        return None

    try:
        content = substack_qmd.read_text()
        frontmatter, _ = parse_frontmatter(content)
        url = frontmatter.get('substack_url', '')
        return url if url else None
    except Exception:
        return None


def rewrite_post_links(content: str, current_post_dir: Path) -> str:
    """
    Rewrite relative links to other posts with their Substack URLs.

    Handles patterns like:
    - [text](../3-probability-paths/)
    - [text](../3-probability-paths/index.qmd)
    - [text](../other-post)
    """
    # Pattern for markdown links to relative paths (not http/https/data/mailto)
    link_pattern = r'\[([^\]]+)\]\((\.\./[^)]+)\)'

    warnings = []

    def replace_link(match):
        link_text = match.group(1)
        relative_path = match.group(2)

        # Resolve the path to get the target post directory
        # Remove trailing index.qmd or similar if present
        clean_path = re.sub(r'/?index\.qmd$', '', relative_path)
        clean_path = clean_path.rstrip('/')

        target_dir = (current_post_dir / clean_path).resolve()

        # Look up Substack URL
        substack_url = get_substack_url(target_dir)

        if substack_url:
            return f'[{link_text}]({substack_url})'
        else:
            # Keep original link but warn
            warnings.append(f"No substack_url found for: {relative_path}")
            return match.group(0)

    result = re.sub(link_pattern, replace_link, content)

    # Print warnings
    for warning in warnings:
        print(f"   ⚠️  {warning}")

    return result


def _print_video_instructions(videos: list[dict], edit_url: str = None) -> None:
    """Print instructions for manual video upload."""
    print("\n🎬 VIDEO UPLOAD REQUIRED")
    print("=" * 50)
    print("Substack has no public API for video upload.")
    print("Videos must be uploaded manually through the editor.\n")

    print("Videos to upload:")
    for v in videos:
        status = f"({v['size_mb']}MB)" if v.get('size_mb') else "(not found)"
        print(f"   [{v['index']}] {v['filename']} {status}")
        if v.get('path'):
            print(f"       Path: {v['path']}")

    print("\n📝 Manual Upload Steps:")
    if edit_url:
        print(f"   1. Open the draft: {edit_url}")
    else:
        print("   1. Open the post in Substack editor")
    print("   2. Find the placeholder: **[VIDEO N: filename.mp4]**")
    print("   3. Delete the placeholder text")
    print("   4. Click the + button or type / to open insert menu")
    print("   5. Select 'Video' from the menu")
    print("   6. Upload the video file from your computer")
    print("   7. Wait for processing (~30-60 seconds per video)")
    print("   8. Save the draft/post")

    print("\n💡 Tip: Videos can also be embedded from YouTube/Vimeo")
    print("   using the 'Embed' option if you've uploaded there.\n")


def process_videos(content: str, base_dir: Path) -> tuple[str, list[dict]]:
    """
    Process Quarto video shortcodes and create placeholders.

    Since Substack has no public API for video upload, we:
    1. Detect video shortcodes: {{< video filename.mp4 >}}
    2. Replace with a visible placeholder in HTML
    3. Track videos for manual upload instructions

    Returns:
        (processed_content, list of video dicts with path/filename info)
    """
    # Match Quarto video shortcode: {{< video filename.mp4 >}}
    video_pattern = r'\{\{<\s*video\s+([^\s>]+)(?:\s+[^>]*)?\s*>\}\}'

    videos_found = []
    video_counter = [0]

    def replace_video(match):
        video_src = match.group(1)
        video_counter[0] += 1
        video_num = video_counter[0]

        # Resolve path
        video_path = base_dir / video_src
        video_exists = video_path.exists()

        video_info = {
            'index': video_num,
            'filename': video_src,
            'path': str(video_path.resolve()) if video_exists else None,
            'exists': video_exists,
            'size_mb': round(video_path.stat().st_size / (1024 * 1024), 1) if video_exists else None
        }
        videos_found.append(video_info)

        if video_exists:
            # Create a visible placeholder that can be identified later
            return f'\n\n**[VIDEO {video_num}: {video_src}]** *(Manual upload required — see instructions below)*\n\n'
        else:
            return f'\n\n**[VIDEO {video_num}: {video_src}]** *(File not found)*\n\n'

    processed = re.sub(video_pattern, replace_video, content)

    if videos_found:
        print(f"   Found {len(videos_found)} video(s) requiring manual upload")
        for v in videos_found:
            status = f"{v['size_mb']}MB" if v['exists'] else "NOT FOUND"
            print(f"      - {v['filename']} ({status})")

    return processed, videos_found


def clean_quarto_syntax(content: str) -> str:
    """Remove Quarto-specific syntax."""
    # Remove cross-reference labels {#sec-xxx}, {#eq-xxx}, {#fig-xxx}
    content = re.sub(r'\s*\{#[^}]+\}', '', content)

    # Remove @ref citations (could enhance to show as text)
    content = re.sub(r'@(fig|sec|eq|tbl)-[\w-]+', '', content)

    # Remove Quarto attributes on fenced code blocks
    content = re.sub(r'```\{[^}]+\}', '```', content)

    # Remove ::: divs that aren't callouts (but keep their content)
    def replace_div(match):
        if '.callout' in match.group(0):
            return match.group(0)  # Keep callouts
        return match.group(1)  # Return just the content

    content = re.sub(r':::\s*\{[^}]*\}\s*([\s\S]*?):::', replace_div, content)

    return content


def protect_and_render_math(content: str) -> tuple[str, list]:
    """
    Protect math from markdown processing and prepare for rendering.
    Returns content with placeholders and list of math expressions.
    """
    placeholders = []
    counter = [0]  # Use list for mutable counter in nested function

    def clean_blockquote_latex(latex: str) -> str:
        """Remove leading '>' from lines in LaTeX (when inside blockquotes)."""
        lines = latex.split('\n')
        cleaned_lines = []
        for line in lines:
            # Strip leading '> ' or '>' from each line
            stripped = line.lstrip()
            if stripped.startswith('>'):
                stripped = stripped[1:].lstrip()
            else:
                stripped = line
            cleaned_lines.append(stripped)
        return '\n'.join(cleaned_lines)

    def create_placeholder(latex: str, display: bool) -> str:
        placeholder_id = f"%%MATH_{counter[0]}%%"
        counter[0] += 1
        # Clean blockquote markers from display math
        if display:
            latex = clean_blockquote_latex(latex)
        placeholders.append({
            'id': placeholder_id,
            'latex': latex.strip(),
            'display': display
        })
        return placeholder_id

    # First, protect escaped dollar signs \$ -> placeholder
    escaped_dollar_placeholder = "%%ESCAPED_DOLLAR%%"
    content = content.replace('\\$', escaped_dollar_placeholder)

    # Protect display math $$...$$
    content = re.sub(
        r'\$\$([\s\S]+?)\$\$',
        lambda m: create_placeholder(m.group(1), True),
        content
    )

    # Protect inline math $...$ (not preceded or followed by $)
    content = re.sub(
        r'(?<!\$)\$(?!\$)([^\$\n]+?)\$(?!\$)',
        lambda m: create_placeholder(m.group(1), False),
        content
    )

    # Restore escaped dollar signs as literal $
    content = content.replace(escaped_dollar_placeholder, '$')

    return content, placeholders


def restore_math(html: str, placeholders: list, output_dir: Path, upload: bool = False) -> tuple[str, int, int]:
    """
    Download equation images locally and restore placeholders.
    If upload=True, also uploads to Substack CDN.

    Returns (html, download_count, upload_count).
    """
    downloaded = 0
    uploaded = 0

    for item in placeholders:
        placeholder_id = item['id']
        latex = item['latex']
        display = item['display']

        filename = download_latex_image(latex, display, output_dir)

        if filename:
            downloaded += 1
            local_path = output_dir / filename

            # Determine image source: CDN URL or local filename
            if upload and _substack_api is not None:
                cdn_url = upload_to_substack_cdn(local_path)
                if cdn_url:
                    uploaded += 1
                    img_src = cdn_url
                else:
                    img_src = filename  # Fallback to local
            else:
                img_src = filename

            if display:
                replacement = f'''<div style="text-align: center; margin: 1.5em 0; overflow-x: auto;">
                    <img src="{img_src}" alt="{html_escape(latex)}" style="max-width: 100%;" class="math-display">
                </div>'''
            else:
                replacement = f'<img src="{img_src}" alt="{html_escape(latex)}" style="vertical-align: middle; display: inline;" class="math-inline">'
        else:
            # Fallback: show LaTeX code
            if display:
                replacement = f'<pre>{html_escape(latex)}</pre>'
            else:
                replacement = f'<code>{html_escape(latex)}</code>'
        html = html.replace(placeholder_id, replacement)

    return html, downloaded, uploaded


def clean_html_tags(content: str) -> str:
    """
    Remove or convert HTML tags that won't render in Substack markdown.
    Converts <sup>N</sup> to Unicode superscript characters.
    Preserves comparison operators like <10ms or >95%.
    """
    superscript_map = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')

    def to_superscript(match):
        return match.group(1).translate(superscript_map)

    content = re.sub(r'<sup>(\d+)</sup>', to_superscript, content)

    # Protect comparison operators (< or > followed by numbers) before stripping HTML
    # <10, >95%, >=5, <=10, etc.
    content = re.sub(r'<(\d)', r'&lt;\1', content)  # <10 -> &lt;10
    content = re.sub(r'>(\d)', r'&gt;\1', content)  # >95 -> &gt;95
    content = re.sub(r'<=', '≤', content)
    content = re.sub(r'>=', '≥', content)

    # Remove actual HTML tags (only match valid tag patterns)
    # A valid HTML tag starts with < followed by a letter or /, not a number or space
    content = re.sub(r'</?[a-zA-Z][^>]*>', '', content)

    # Restore HTML entities to readable characters
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')

    return content


def replace_math_with_images(content: str, output_dir: Path, upload: bool = False) -> str:
    """
    Replace LaTeX math expressions with image markdown.

    Downloads equation images, optionally uploads to CDN, and replaces
    LaTeX expressions with markdown image syntax.

    Args:
        content: Markdown content with LaTeX math
        output_dir: Directory to save equation images
        upload: If True, upload images to Substack CDN

    Returns:
        Markdown content with LaTeX replaced by image references
    """
    def clean_blockquote_latex(latex: str) -> str:
        """Remove leading '>' from lines in LaTeX (when inside blockquotes)."""
        lines = latex.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith('>'):
                stripped = stripped[1:].lstrip()
            else:
                stripped = line
            cleaned_lines.append(stripped)
        return '\n'.join(cleaned_lines)

    # First, protect escaped dollar signs \$ -> placeholder
    escaped_dollar_placeholder = "%%ESCAPED_DOLLAR%%"
    result = content.replace('\\$', escaped_dollar_placeholder)

    # Process display math $$...$$
    def replace_display_math(match):
        latex = clean_blockquote_latex(match.group(1)).strip()
        filename = download_latex_image(latex, display=True, output_dir=output_dir)
        if filename:
            local_path = output_dir / filename
            if upload and _substack_api is not None:
                cdn_url = upload_to_substack_cdn(local_path)
                if cdn_url:
                    return f'\n\n![equation]({cdn_url})\n\n'
            return f'\n\n![equation]({filename})\n\n'
        return match.group(0)  # Keep original if download failed

    result = re.sub(r'\$\$([\s\S]+?)\$\$', replace_display_math, result)

    # Process inline math $...$
    def replace_inline_math(match):
        latex = match.group(1).strip()
        filename = download_latex_image(latex, display=False, output_dir=output_dir)
        if filename:
            local_path = output_dir / filename
            if upload and _substack_api is not None:
                cdn_url = upload_to_substack_cdn(local_path)
                if cdn_url:
                    return f'![equation]({cdn_url})'
            return f'![equation]({filename})'
        return match.group(0)  # Keep original if download failed

    result = re.sub(r'(?<!\$)\$(?!\$)([^\$\n]+?)\$(?!\$)', replace_inline_math, result)

    # Restore escaped dollar signs as literal $
    result = result.replace(escaped_dollar_placeholder, '$')

    return result


def preprocess_for_api(content: str) -> str:
    """
    Preprocess markdown content for Substack API publishing.

    Handles:
    - Blockquote markers (>) - strips them, library doesn't handle
    - Double emojis in callout titles - dedupe
    - Bullet lists - marks with special markers for post-processing
    """
    lines = content.split('\n')
    result = []
    bullet_counter = 0
    in_bullet_list = False

    for i, line in enumerate(lines):
        # Strip blockquote markers - Substack API doesn't support blockquotes
        if line.startswith('>'):
            # Remove leading > and optional space
            stripped = line[1:].lstrip() if len(line) > 1 else ''
            # If it's a nested blockquote (>>), strip all
            while stripped.startswith('>'):
                stripped = stripped[1:].lstrip()
            line = stripped

        # Fix double emojis in callout titles (📝 📝 → 📝)
        # These can occur from preprocessing + callout handling
        line = re.sub(r'(📝|💡|⚠️|❗|🔥)\s*\1', r'\1', line)

        # Detect bullet list items and wrap with markers
        stripped_line = line.lstrip()
        is_bullet = stripped_line.startswith('- ') or stripped_line.startswith('* ')

        if is_bullet:
            if not in_bullet_list:
                # Start of a new bullet list
                result.append(f'%%BULLET_LIST_START_{bullet_counter}%%')
                in_bullet_list = True

            # Mark the bullet item (remove the bullet marker, will be reconstructed)
            item_text = stripped_line[2:]  # Remove '- ' or '* '

            # Convert markdown links to placeholder format that preserves URLs
            # from_markdown() loses the href, so we need to preserve it ourselves
            # [text](url) → %%LINK_START%%url%%LINK_SEP%%text%%LINK_END%%
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            def link_to_placeholder(match):
                link_text = match.group(1)
                link_url = match.group(2)
                return f'%%LINK_START%%{link_url}%%LINK_SEP%%{link_text}%%LINK_END%%'
            item_text = re.sub(link_pattern, link_to_placeholder, item_text)

            result.append(f'%%BULLET_ITEM%% {item_text}')
        else:
            if in_bullet_list:
                # End of bullet list (non-bullet line encountered)
                result.append(f'%%BULLET_LIST_END_{bullet_counter}%%')
                in_bullet_list = False
                bullet_counter += 1

            result.append(line)

    # Close any unclosed bullet list at end
    if in_bullet_list:
        result.append(f'%%BULLET_LIST_END_{bullet_counter}%%')

    return '\n'.join(result)


def generate_latex_id() -> str:
    """Generate a unique ID for LaTeX blocks (10 uppercase alphanumeric chars)."""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def extract_latex_blocks(content: str) -> tuple[str, list[dict]]:
    """
    Extract LaTeX math expressions and replace with placeholders.

    Returns:
        (content_with_placeholders, list_of_latex_blocks)

    Each latex block dict has:
        - placeholder: The placeholder string in content
        - expression: The LaTeX expression
        - display: True for block ($$), False for inline ($)
        - id: Unique ID for Substack
    """
    blocks = []
    counter = [0]

    def clean_blockquote_latex(latex: str) -> str:
        """Remove leading '>' from lines in LaTeX (when inside blockquotes)."""
        lines = latex.split('\n')
        cleaned = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith('>'):
                stripped = stripped[1:].lstrip()
            else:
                stripped = line
            cleaned.append(stripped)
        return '\n'.join(cleaned)

    def make_placeholder(match, display: bool) -> str:
        latex = match.group(1).strip()
        if display:
            latex = clean_blockquote_latex(latex)

        placeholder = f"%%LATEX_BLOCK_{counter[0]}%%"
        counter[0] += 1

        blocks.append({
            'placeholder': placeholder,
            'expression': latex,
            'display': display,
            'id': generate_latex_id()
        })
        return placeholder

    # First, protect escaped dollar signs \$ -> placeholder
    escaped_dollar_placeholder = "%%ESCAPED_DOLLAR%%"
    result = content.replace('\\$', escaped_dollar_placeholder)

    # Extract display math $$...$$
    result = re.sub(
        r'\$\$([\s\S]+?)\$\$',
        lambda m: make_placeholder(m, display=True),
        result
    )

    # Extract inline math $...$
    result = re.sub(
        r'(?<!\$)\$(?!\$)([^\$\n]+?)\$(?!\$)',
        lambda m: make_placeholder(m, display=False),
        result
    )

    # Restore escaped dollar signs as literal $
    result = result.replace(escaped_dollar_placeholder, '$')

    return result, blocks


def build_tiptap_with_native_latex(
    markdown_content: str,
    latex_blocks: list[dict],
    post: 'SubstackPost'
) -> None:
    """
    Build Substack post content with native LaTeX support and proper callout formatting.

    IMPORTANT: Substack's TipTap schema requires:
    - latex_block to be a TOP-LEVEL node (not inside paragraphs)
    - blockquote nodes for callout formatting
    - link marks for hyperlinks
    - bulletList/listItem nodes for lists

    This function:
    1. Splits paragraphs when LaTeX placeholders are found
    2. Wraps callout content in blockquote nodes
    3. Converts raw markdown links to proper link nodes
    4. Converts bullet list paragraphs to proper list nodes

    Args:
        markdown_content: Markdown with LaTeX placeholders (%%LATEX_BLOCK_N%%)
                         and callout markers (%%CALLOUT_START/END_N%%)
        latex_blocks: List of LaTeX block dicts from extract_latex_blocks()
        post: SubstackPost instance to build into
    """
    import copy
    import re

    # First, use the library's markdown parser
    post.from_markdown(markdown_content, api=_substack_api)

    # ===== POST-PROCESS: Fix links and lists that library doesn't handle =====

    def convert_text_with_links(text: str) -> list[dict]:
        """Convert text containing markdown links to TipTap nodes with link marks."""
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        result = []
        last_end = 0

        for match in re.finditer(link_pattern, text):
            # Add text before the link
            if match.start() > last_end:
                before_text = text[last_end:match.start()]
                if before_text:
                    result.append({'type': 'text', 'text': before_text})

            # Add the link with proper mark
            link_text = match.group(1)
            link_url = match.group(2)
            result.append({
                'type': 'text',
                'text': link_text,
                'marks': [{'type': 'link', 'attrs': {'href': link_url}}]
            })
            last_end = match.end()

        # Add remaining text after last link
        if last_end < len(text):
            remaining = text[last_end:]
            if remaining:
                result.append({'type': 'text', 'text': remaining})

        return result if result else [{'type': 'text', 'text': text}]

    def fix_links_in_node(node: dict) -> dict:
        """Recursively fix markdown links in text nodes."""
        if node.get('type') == 'text':
            text = node.get('text', '')
            if '[' in text and '](' in text:
                # This text contains markdown links - convert it
                return convert_text_with_links(text)
            return node

        if 'content' in node:
            new_content = []
            for child in node['content']:
                fixed = fix_links_in_node(child)
                if isinstance(fixed, list):
                    new_content.extend(fixed)
                else:
                    new_content.append(fixed)
            node['content'] = new_content

        return node

    def get_node_text(node: dict) -> str:
        """Extract all text from a node recursively."""
        if node.get('type') == 'text':
            return node.get('text', '')
        if 'content' not in node:
            return ''
        return ''.join(get_node_text(child) for child in node['content'])

    def is_bullet_marker(node: dict) -> tuple[bool, str, str]:
        """Check if node contains bullet list markers.
        Returns (is_marker, marker_type, marker_id_or_text).
        marker_type: 'start', 'end', or 'item'
        """
        if node.get('type') != 'paragraph':
            return False, '', ''
        text = get_node_text(node)

        # Check for list start marker
        start_match = re.search(r'%%BULLET_LIST_START_(\d+)%%', text)
        if start_match:
            return True, 'start', start_match.group(1)

        # Check for list end marker
        end_match = re.search(r'%%BULLET_LIST_END_(\d+)%%', text)
        if end_match:
            return True, 'end', end_match.group(1)

        # Check for bullet item marker
        item_match = re.search(r'%%BULLET_ITEM%%(.*)$', text)
        if item_match:
            return True, 'item', item_match.group(1)

        return False, '', ''

    def convert_link_placeholders(text: str) -> list[dict]:
        """Convert %%LINK_START%%url%%LINK_SEP%%text%%LINK_END%% to TipTap link nodes."""
        link_pattern = r'%%LINK_START%%([^%]+)%%LINK_SEP%%([^%]+)%%LINK_END%%'
        result = []
        last_end = 0

        for match in re.finditer(link_pattern, text):
            # Add text before the link placeholder
            if match.start() > last_end:
                before_text = text[last_end:match.start()]
                if before_text:
                    result.append({'type': 'text', 'text': before_text})

            # Add the link with proper mark
            link_url = match.group(1)
            link_text = match.group(2)
            result.append({
                'type': 'text',
                'text': link_text,
                'marks': [{'type': 'link', 'attrs': {'href': link_url}}]
            })
            last_end = match.end()

        # Add remaining text after last link
        if last_end < len(text):
            remaining = text[last_end:]
            if remaining:
                result.append({'type': 'text', 'text': remaining})

        return result if result else [{'type': 'text', 'text': text}]

    def strip_marker_from_content(content: list, marker_prefix: str) -> list:
        """Strip marker prefix from paragraph content while preserving other nodes (links, etc.)."""
        if not content:
            return content

        result = []
        found_marker = False

        for node in content:
            if not found_marker and node.get('type') == 'text':
                text = node.get('text', '')
                if marker_prefix in text:
                    # Strip the marker from this text node
                    new_text = text.replace(marker_prefix, '', 1).lstrip()
                    found_marker = True
                    if new_text:
                        # Check if text contains link placeholders
                        if '%%LINK_START%%' in new_text:
                            link_nodes = convert_link_placeholders(new_text)
                            result.extend(link_nodes)
                        # Check if remaining text contains markdown links
                        elif '[' in new_text and '](' in new_text:
                            # Convert links and add resulting nodes
                            link_nodes = convert_text_with_links(new_text)
                            result.extend(link_nodes)
                        else:
                            result.append({'type': 'text', 'text': new_text})
                else:
                    result.append(node)
            else:
                result.append(node)

        return result

    def convert_bullets_to_list(nodes: list[dict]) -> list[dict]:
        """Convert marked bullet items to proper bulletList nodes."""
        result = []
        i = 0

        while i < len(nodes):
            is_marker, marker_type, marker_data = is_bullet_marker(nodes[i])

            if is_marker and marker_type == 'start':
                # Start collecting bullet items until end marker
                list_id = marker_data
                list_items = []
                i += 1  # Skip the start marker

                while i < len(nodes):
                    is_m, m_type, m_data = is_bullet_marker(nodes[i])

                    if is_m and m_type == 'end' and m_data == list_id:
                        # Found end marker, create the list
                        i += 1
                        break
                    elif is_m and m_type == 'item':
                        # This is a bullet item - preserve the paragraph content
                        # but strip the %%BULLET_ITEM%% marker
                        para_content = nodes[i].get('content', [])
                        clean_content = strip_marker_from_content(para_content, '%%BULLET_ITEM%%')

                        if clean_content:
                            list_items.append({
                                'type': 'listItem',
                                'content': [{
                                    'type': 'paragraph',
                                    'content': clean_content
                                }]
                            })
                        i += 1
                    else:
                        # Non-marker content inside list (shouldn't happen, but handle it)
                        i += 1

                # Create the bulletList node
                if list_items:
                    result.append({
                        'type': 'bulletList',
                        'content': list_items
                    })
            elif is_marker and marker_type == 'item':
                # Orphan bullet item (shouldn't happen) - skip
                i += 1
            elif is_marker and marker_type == 'end':
                # Orphan end marker (shouldn't happen) - skip
                i += 1
            else:
                # Regular node - check for stray markers in text and clean
                if nodes[i].get('type') == 'paragraph':
                    text = get_node_text(nodes[i])
                    if '%%BULLET' in text:
                        # Clean stray markers from the content
                        clean_content = nodes[i].get('content', [])
                        clean_content = strip_marker_from_content(clean_content, '%%BULLET_LIST_START_')
                        clean_content = strip_marker_from_content(clean_content, '%%BULLET_LIST_END_')
                        clean_content = strip_marker_from_content(clean_content, '%%BULLET_ITEM%%')
                        if clean_content:
                            result.append({
                                'type': 'paragraph',
                                'content': clean_content
                            })
                    else:
                        result.append(nodes[i])
                else:
                    result.append(nodes[i])
                i += 1

        return result

    # Apply fixes to the body content
    body = post.draft_body
    if 'content' in body:
        # Step 1: Fix links in all nodes
        fixed_content = []
        for node in body['content']:
            fixed = fix_links_in_node(node)
            if isinstance(fixed, list):
                fixed_content.extend(fixed)
            else:
                fixed_content.append(fixed)

        # Step 2: Convert bullet paragraphs to proper list nodes
        fixed_content = convert_bullets_to_list(fixed_content)

        # Step 3: Fix links again in list items (may have markdown links from marker stripping)
        def fix_links_recursive(nodes: list) -> list:
            """Recursively fix markdown links in all nodes including nested content."""
            result = []
            for node in nodes:
                if node.get('type') == 'text':
                    text = node.get('text', '')
                    # Only convert if no existing marks (don't overwrite already-linked text)
                    if '[' in text and '](' in text and not node.get('marks'):
                        link_nodes = convert_text_with_links(text)
                        result.extend(link_nodes)
                    else:
                        result.append(node)
                elif 'content' in node:
                    node['content'] = fix_links_recursive(node['content'])
                    result.append(node)
                else:
                    result.append(node)
            return result

        fixed_content = fix_links_recursive(fixed_content)

        body['content'] = fixed_content

    # ===== END POST-PROCESS =====

    # Build placeholder -> latex_block mapping
    placeholder_map = {
        block['placeholder']: {
            'type': 'latex_block',
            'attrs': {
                'persistentExpression': block['expression'],
                'id': block['id']
            }
        }
        for block in latex_blocks
    }

    # Patterns for LaTeX and callout markers
    latex_pattern = re.compile(r'(%%LATEX_BLOCK_\d+%%)')
    callout_start_pattern = re.compile(r'%%CALLOUT_START_(\d+)%%')
    callout_end_pattern = re.compile(r'%%CALLOUT_END_(\d+)%%')

    def text_contains_placeholder(text: str) -> bool:
        """Check if text contains any LaTeX placeholder."""
        return bool(latex_pattern.search(text))

    def text_contains_callout_marker(text: str) -> bool:
        """Check if text contains callout start/end marker."""
        return bool(callout_start_pattern.search(text)) or bool(callout_end_pattern.search(text))

    def split_paragraph_by_latex(para_node: dict) -> list[dict]:
        """
        Split a paragraph containing LaTeX placeholders into multiple top-level nodes.
        Returns a list of nodes: paragraphs for text, latex_block for equations.
        """
        if para_node.get('type') != 'paragraph':
            return [para_node]

        full_text = get_node_text(para_node)

        if not text_contains_placeholder(full_text):
            return [para_node]

        parts = latex_pattern.split(full_text)
        result_nodes = []

        for part in parts:
            if not part:
                continue

            if part in placeholder_map:
                result_nodes.append(copy.deepcopy(placeholder_map[part]))
            else:
                text_part = part.strip()
                if text_part:
                    result_nodes.append({
                        'type': 'paragraph',
                        'content': [{'type': 'text', 'text': text_part}]
                    })

        return result_nodes if result_nodes else [{'type': 'paragraph'}]

    def is_callout_marker_node(node: dict, marker_type: str) -> tuple[bool, int | None]:
        """Check if node contains a callout marker. Returns (is_marker, callout_id)."""
        text = get_node_text(node)
        if marker_type == 'start':
            match = callout_start_pattern.search(text)
        else:
            match = callout_end_pattern.search(text)
        if match:
            return True, int(match.group(1))
        return False, None

    def remove_marker_from_text(text: str) -> str:
        """Remove callout markers from text."""
        text = callout_start_pattern.sub('', text)
        text = callout_end_pattern.sub('', text)
        return text.strip()

    # Process the body
    body = post.draft_body
    if 'content' not in body:
        return

    # First pass: split paragraphs by LaTeX
    intermediate_content = []
    for node in body['content']:
        if node.get('type') == 'paragraph':
            split_nodes = split_paragraph_by_latex(node)
            intermediate_content.extend(split_nodes)
        else:
            intermediate_content.append(node)

    # Second pass: wrap callout content in blockquotes
    final_content = []
    i = 0
    while i < len(intermediate_content):
        node = intermediate_content[i]
        text = get_node_text(node)

        is_start, callout_id = is_callout_marker_node(node, 'start')
        if is_start:
            # Collect all nodes until matching end marker
            blockquote_content = []

            # Check if start marker paragraph has content after marker
            remaining_text = remove_marker_from_text(text)
            if remaining_text:
                blockquote_content.append({
                    'type': 'paragraph',
                    'content': [{'type': 'text', 'text': remaining_text}]
                })

            i += 1
            while i < len(intermediate_content):
                inner_node = intermediate_content[i]
                inner_text = get_node_text(inner_node)
                is_end, end_id = is_callout_marker_node(inner_node, 'end')

                if is_end and end_id == callout_id:
                    # Check if end marker paragraph has content before marker
                    remaining = remove_marker_from_text(inner_text)
                    if remaining:
                        blockquote_content.append({
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': remaining}]
                        })
                    i += 1
                    break
                else:
                    # Clean any stray markers and add to blockquote
                    if inner_node.get('type') == 'paragraph':
                        cleaned_text = remove_marker_from_text(inner_text)
                        if cleaned_text:
                            blockquote_content.append({
                                'type': 'paragraph',
                                'content': [{'type': 'text', 'text': cleaned_text}]
                            })
                    elif inner_node.get('type') == 'latex_block':
                        # LaTeX inside callout - add to blockquote
                        blockquote_content.append(inner_node)
                    else:
                        blockquote_content.append(inner_node)
                    i += 1

            # Create blockquote node
            if blockquote_content:
                final_content.append({
                    'type': 'blockquote',
                    'content': blockquote_content
                })
        else:
            # Regular node - clean any stray markers
            if node.get('type') == 'paragraph' and text_contains_callout_marker(text):
                cleaned = remove_marker_from_text(text)
                if cleaned:
                    final_content.append({
                        'type': 'paragraph',
                        'content': [{'type': 'text', 'text': cleaned}]
                    })
            else:
                final_content.append(node)
            i += 1

    body['content'] = final_content


def build_post_from_markdown(markdown_content: str, post: 'SubstackPost', native_latex: bool = False) -> None:
    """
    Build Substack post content from markdown using the library's built-in parser.

    Uses python-substack's from_markdown() which properly handles:
    - Images (captionedImage type)
    - Headings
    - Bullet lists
    - Code blocks
    - Bold/italic formatting
    - Links

    Args:
        markdown_content: Markdown content to convert
        post: SubstackPost instance to build into
        native_latex: If True, use native latex_block nodes instead of PNG images
    """
    # Preprocess to handle blockquotes and fix formatting issues
    processed_content = preprocess_for_api(markdown_content)

    if native_latex:
        # Extract LaTeX and replace with placeholders
        content_with_placeholders, latex_blocks = extract_latex_blocks(processed_content)

        # Always use native builder for callout processing, even without LaTeX
        # The callout markers need to be converted to blockquote nodes
        build_tiptap_with_native_latex(content_with_placeholders, latex_blocks, post)
    else:
        # Use the library's built-in markdown parser with API for image uploads
        post.from_markdown(processed_content, api=_substack_api)


def publish_to_substack(
    title: str,
    subtitle: str,
    markdown_content: str,
    draft_only: bool = False,
    native_latex: bool = True
) -> dict | None:
    """
    Publish content directly to Substack via API.

    Args:
        title: Post title
        subtitle: Post subtitle
        markdown_content: Processed markdown content (not HTML)
        draft_only: If True, only create draft (don't publish)
        native_latex: If True, use native latex_block nodes (consistent sizing)

    Returns:
        Dict with post info (id, url) on success, None on failure
    """
    global _substack_api

    if _substack_api is None:
        print("❌ Substack API not initialized")
        return None

    if not SUBSTACK_AVAILABLE:
        print("❌ python-substack not available")
        return None

    try:
        # Get user info for the post
        user_info = _substack_api.get_user_id()
        if not user_info:
            print("❌ Failed to get Substack user info")
            return None

        # Create the post using python-substack's Post class
        print("   Building post content...")
        if native_latex:
            print("   Using native LaTeX rendering (consistent sizing)")
        post = SubstackPost(
            title=title,
            subtitle=subtitle,
            user_id=user_info
        )

        # Build content with our custom parser
        build_post_from_markdown(markdown_content, post, native_latex=native_latex)

        # Create draft with retry
        import time
        print("   Creating draft on Substack...")
        draft_body = post.get_draft()

        draft_result = None
        for attempt in range(3):
            try:
                draft_result = _substack_api.post_draft(draft_body)
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    wait_time = 5 * (attempt + 1)
                    print(f"   ⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

        if not draft_result or "id" not in draft_result:
            print("❌ Failed to create draft")
            return None

        draft_id = draft_result["id"]
        print(f"   ✅ Draft created: ID {draft_id}")

        if draft_only:
            # Return draft info
            return {
                "id": draft_id,
                "status": "draft",
                "url": f"https://aheadofrobotics.substack.com/publish/post/{draft_id}"
            }

        # Publish the draft
        print("   Publishing draft...")
        publish_result = _substack_api.publish_draft(draft_id)

        if publish_result:
            # Try to get the published URL
            slug = draft_result.get("slug", "")
            published_url = f"https://aheadofrobotics.substack.com/p/{slug}" if slug else None

            print("   ✅ Post published!")
            return {
                "id": draft_id,
                "status": "published",
                "url": published_url,
                "slug": slug
            }
        else:
            print("   ⚠️ Draft created but publish may have failed")
            return {
                "id": draft_id,
                "status": "draft",
                "url": f"https://aheadofrobotics.substack.com/publish/post/{draft_id}"
            }

    except Exception as e:
        print(f"❌ Publishing failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def convert_qmd_to_substack(
    qmd_path: Path,
    output_path: Path,
    upload: bool = False,
    publish: bool = False,
    draft_only: bool = False
) -> bool:
    """
    Main conversion function.

    Args:
        qmd_path: Path to .qmd file
        output_path: Output path for HTML file
        upload: If True, upload images to Substack CDN
        publish: If True, publish directly to Substack via API
        draft_only: If True (with publish), only create draft

    Returns:
        True on success, False on failure
    """
    print(f"\n📄 Processing: {qmd_path}")

    # Initialize Substack API if upload or publish is enabled
    needs_api = upload or publish
    if needs_api:
        if not init_substack_api():
            print("❌ Cannot proceed without Substack authentication.")
            if publish:
                return False
            print("   Continuing without CDN upload...")
            upload = False

    # Read file
    raw_content = qmd_path.read_text()

    # Parse frontmatter
    frontmatter, md_content = parse_frontmatter(raw_content)
    title = frontmatter.get('title', 'Untitled')
    author = frontmatter.get('author', '')
    date = frontmatter.get('date', '')
    print(f"   Title: {title}")

    # Process callouts
    print("   Processing callouts...")
    processed_content = process_callouts(md_content)

    # Process videos (detect shortcodes, create placeholders)
    print("   Processing videos...")
    processed_content, videos_found = process_videos(processed_content, qmd_path.parent)

    # Clean Quarto syntax
    print("   Cleaning Quarto syntax...")
    processed_content = clean_quarto_syntax(processed_content)

    # Rewrite links to other posts with Substack URLs
    print("   Rewriting post links...")
    processed_content = rewrite_post_links(processed_content, qmd_path.parent)

    # Process images
    if upload:
        print("   Processing images (uploading to Substack CDN)...")
    else:
        print("   Processing images (will need local server)...")
    processed_content, images_to_upload, img_uploaded = process_images_for_substack(
        processed_content, qmd_path.parent, upload=upload
    )

    # Protect math before markdown processing
    print("   Extracting math expressions...")
    protected_content, placeholders = protect_and_render_math(processed_content)
    print(f"   Found {len(placeholders)} math expressions")

    # Convert markdown to HTML
    print("   Converting markdown to HTML...")
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html = md.convert(protected_content)

    # Download equation images and restore placeholders
    if upload:
        print("   Downloading and uploading equation images...")
    else:
        print("   Downloading equation images...")
    html, eq_downloaded, eq_uploaded = restore_math(html, placeholders, qmd_path.parent, upload=upload)
    print(f"   Downloaded {eq_downloaded} equation images")
    if upload:
        print(f"   Uploaded {eq_uploaded} equations to CDN")

    # Create final HTML document
    final_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_escape(title)}</title>
    <style>
        * {{ box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.7;
            max-width: 680px;
            margin: 0 auto;
            padding: 24px;
            color: #1a1a1a;
            background: #fff;
        }}

        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 2em;
        }}

        h1 {{ font-size: 2em; line-height: 1.2; margin-top: 0; margin-bottom: 0.5em; }}
        h2 {{ font-size: 1.5em; margin-top: 2em; padding-bottom: 0.3em; border-bottom: 1px solid #eee; }}
        h3 {{ font-size: 1.25em; margin-top: 1.5em; }}
        h4 {{ font-size: 1.1em; margin-top: 1.2em; }}

        p {{ margin: 1em 0; }}

        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}

        code {{
            font-family: ui-monospace, "SF Mono", Monaco, "Cascadia Code", Consolas, monospace;
            font-size: 0.875em;
            background: #f6f8fa;
            padding: 2px 6px;
            border-radius: 4px;
        }}

        pre {{
            background: #f6f8fa;
            padding: 16px;
            overflow-x: auto;
            border-radius: 8px;
            font-size: 0.875em;
            line-height: 1.5;
        }}

        pre code {{
            background: none;
            padding: 0;
        }}

        blockquote {{
            border-left: 4px solid #ddd;
            padding: 0.5em 1em;
            margin: 1.5em 0;
            color: #555;
            background: #f9f9f9;
            border-radius: 0 4px 4px 0;
        }}

        blockquote p {{ margin: 0.5em 0; }}
        blockquote p:first-child {{ margin-top: 0; }}
        blockquote p:last-child {{ margin-bottom: 0; }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.5em 0;
            font-size: 0.9em;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 10px 12px;
            text-align: left;
        }}

        th {{
            background: #f6f8fa;
            font-weight: 600;
        }}

        tr:nth-child(even) {{ background: #fafafa; }}

        img {{
            max-width: 100%;
            height: auto;
        }}

        img.math-inline {{
            vertical-align: middle;
            display: inline;
        }}

        img.math-display {{
            max-width: 100%;
        }}

        ul, ol {{ padding-left: 1.5em; }}
        li {{ margin: 0.5em 0; }}

        hr {{
            border: none;
            border-top: 1px solid #eee;
            margin: 2em 0;
        }}

        strong {{ font-weight: 600; }}
    </style>
</head>
<body>
    <article>
        <h1>{html_escape(title)}</h1>
        {f'<div class="meta">{author}{" · " if author and date else ""}{date}</div>' if author or date else ''}
        {html}
    </article>
</body>
</html>'''

    # Write output HTML (always useful for review)
    output_path.write_text(final_html)
    print(f"\n✅ HTML saved to: {output_path}")
    print(f"   Equation images: {eq_downloaded}")

    if upload or publish:
        total_uploaded = img_uploaded + eq_uploaded
        print(f"   Images uploaded to CDN: {total_uploaded}")

    # Direct publish to Substack
    if publish:
        subtitle = frontmatter.get('subtitle', frontmatter.get('description', ''))
        if not subtitle:
            print("\n⚠️  No subtitle in frontmatter. Add one for better engagement:")
            print("   subtitle: \"Your compelling 1-line hook here\"")
            print("   Examples:")
            print("   - \"How neural networks learn to transform random noise into stunning images\"")
            print("   - \"The mathematical trick that makes training 1000x more efficient\"")
            print()
        # Pre-process content for API publishing
        print("   Pre-processing content for API publishing...")

        # Use native LaTeX by default (consistent equation sizing)
        # This skips PNG conversion and uses Substack's native latex_block nodes
        use_native_latex = True  # TODO: Could make this a CLI flag if PNG fallback needed

        if use_native_latex:
            # Re-process content with API-specific callout markers
            # This creates markers that will be converted to blockquote nodes
            api_content = process_callouts(md_content, for_api=True)
            # Process videos (creates placeholders in content)
            api_content, api_videos = process_videos(api_content, qmd_path.parent)
            api_content = clean_quarto_syntax(api_content)
            api_content = rewrite_post_links(api_content, qmd_path.parent)
            # Process images for API (upload to CDN)
            api_content, _, _ = process_images_for_substack(api_content, qmd_path.parent, upload=True)
            publish_content = clean_html_tags(api_content)
            # Use videos from API processing path
            videos_found = api_videos if api_videos else videos_found
        else:
            # Fallback: Convert LaTeX to PNG images (inconsistent sizing)
            publish_content = replace_math_with_images(processed_content, qmd_path.parent, upload=True)
            publish_content = clean_html_tags(publish_content)

        result = publish_to_substack(title, subtitle, publish_content, draft_only=draft_only, native_latex=use_native_latex)

        if result:
            status = result.get('status', 'unknown')
            url = result.get('url', '')

            if status == 'published':
                print(f"\n🎉 Post published to Substack!")
                if url:
                    print(f"   URL: {url}")
                print(f"\n📋 Next steps:")
                print(f"   1. Update substack_url in _substack.qmd frontmatter")
                print(f"   2. Run /substack-validate to verify content")
                if videos_found:
                    print(f"   3. Upload videos manually (see instructions below)\n")
                else:
                    print()
            else:
                print(f"\n📝 Draft created on Substack")
                if url:
                    print(f"   Edit URL: {url}")
                print(f"\n📋 Next steps:")
                print(f"   1. Review draft at the URL above")
                if videos_found:
                    print(f"   2. Upload videos manually (see instructions below)")
                    print(f"   3. Publish when ready\n")
                else:
                    print(f"   2. Publish when ready\n")

            # Print video upload instructions
            if videos_found:
                _print_video_instructions(videos_found, url)
            return True
        else:
            print(f"\n❌ Publishing failed. HTML file saved for manual upload.")
            print(f"   Open {output_path} in browser and copy-paste to Substack.\n")
            return False

    # Manual workflow (no --publish)
    if upload:
        if images_to_upload:
            print("\n⚠️  Some images failed to upload:")
            for img in images_to_upload:
                print(f"   - {img['filename']}")

        print("\n📋 Next steps:")
        print(f"   1. Open {output_path} in browser")
        print("   2. Select all (Cmd/Ctrl+A) and copy")
        print("   3. Paste into Substack editor")
        if videos_found:
            print("   4. Upload videos manually (see instructions below)")
            print("   5. Review and publish!")
        else:
            print("   4. Review and publish!")
        print()
    else:
        print(f"   Images found: {len(images_to_upload)}")

        if images_to_upload:
            print("\n🖼️  Images (will be uploaded when you paste):")
            for img in images_to_upload:
                print(f"   - {img['filename']}")

        print("\n📋 Next steps:")
        print("   1. Start a local server in the post directory:")
        print(f"      cd {qmd_path.parent} && python -m http.server 8765")
        print(f"   2. Open http://localhost:8765/{output_path.name} in browser")
        print("   3. Select all (Cmd/Ctrl+A) and copy")
        print("   4. Paste into Substack — images upload automatically")
        if videos_found:
            print("   5. Upload videos manually (see instructions below)")
            print("   6. Review and adjust formatting as needed")
        else:
            print("   5. Review and adjust formatting as needed")
        print()

    # Print video upload instructions if videos were found
    if videos_found:
        _print_video_instructions(videos_found)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert Quarto .qmd files to Substack-compatible HTML with rendered LaTeX"
    )
    parser.add_argument("input", help="Path to .qmd file")
    parser.add_argument("-o", "--output", help="Output HTML file path")
    parser.add_argument("--clear-cache", action="store_true", help="Clear equation cache")
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload images to Substack CDN (requires SUBSTACK_COOKIES env var)"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish directly to Substack via API (no copy-paste needed)"
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="With --publish: create draft only, don't publish"
    )

    args = parser.parse_args()

    if args.clear_cache:
        import shutil
        shutil.rmtree(CACHE_DIR, ignore_errors=True)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        print("Cache cleared.")

    qmd_path = Path(args.input)
    if not qmd_path.exists():
        print(f"❌ Error: File not found: {qmd_path}")
        sys.exit(1)

    # --publish implies --upload (need CDN URLs for API publishing)
    upload = args.upload or args.publish

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = qmd_path.parent / f"{qmd_path.stem}_substack.html"

    # Convert and optionally publish
    success = convert_qmd_to_substack(
        qmd_path,
        output_path,
        upload=upload,
        publish=args.publish,
        draft_only=args.draft
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
