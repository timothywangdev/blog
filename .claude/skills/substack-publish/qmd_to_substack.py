#!/usr/bin/env python3
"""
QMD to Substack Converter

Converts Quarto .qmd files directly to Substack-compatible HTML with LaTeX
rendered as inline SVG images (base64 encoded for email compatibility).

Usage:
    python qmd_to_substack.py path/to/post/index.qmd [-o output.html]

Requirements (install in .venv):
    pip install requests beautifulsoup4 pyyaml markdown
"""

import argparse
import base64
import hashlib
import mimetypes
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


# Cache directory for rendered equations
CACHE_DIR = Path.home() / ".cache" / "qmd-to-substack"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_equation_hash(latex: str, display: bool) -> str:
    """Generate cache key for equation."""
    return hashlib.md5(f"{display}:{latex}".encode()).hexdigest()


def render_latex_to_png(latex: str, display: bool = False) -> str | None:
    """
    Render LaTeX to PNG using CodeCogs API.
    Returns base64-encoded PNG data URI (better Substack compatibility than SVG).
    """
    cache_key = get_equation_hash(latex, display)
    cache_file = CACHE_DIR / f"{cache_key}.png"

    # Check cache first
    if cache_file.exists():
        png_data = cache_file.read_bytes()
        b64 = base64.b64encode(png_data).decode('utf-8')
        return f"data:image/png;base64,{b64}"

    # Use CodeCogs PNG API with higher DPI for quality
    # \\dpi{150} for display math, \\dpi{120} for inline
    dpi = 150 if display else 120
    latex_with_dpi = f"\\dpi{{{dpi}}} {latex}"
    encoded_latex = quote(latex_with_dpi)
    url = f"https://latex.codecogs.com/png.latex?{encoded_latex}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        png_data = response.content

        # Cache the result
        cache_file.write_bytes(png_data)

        b64 = base64.b64encode(png_data).decode('utf-8')
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        print(f"  ⚠️  Failed to render: {latex[:40]}... - {e}")
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


def embed_local_images(content: str, base_dir: Path) -> str:
    """Convert local image references to base64 data URIs."""
    # Pattern for markdown images: ![alt](path) or ![alt](path "title")
    img_pattern = r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)'

    def replace_image(match):
        alt_text = match.group(1)
        img_src = match.group(2)

        # Skip URLs (http, https, data URIs)
        if img_src.startswith(('http://', 'https://', 'data:')):
            return match.group(0)

        # Resolve path relative to the qmd file
        img_path = base_dir / img_src

        data_uri = image_to_data_uri(img_path)
        if data_uri:
            return f'![{alt_text}]({data_uri})'
        else:
            print(f"  ⚠️  Image not found: {img_src}")
            return match.group(0)

    return re.sub(img_pattern, replace_image, content)


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


def process_callouts(content: str) -> str:
    """Convert Quarto callouts to blockquotes."""
    callout_pattern = r':::\s*\{\.callout-(\w+)(?:\s+[^}]*)?\}\s*([\s\S]*?):::'

    emojis = {
        'note': '📝',
        'tip': '💡',
        'warning': '⚠️',
        'important': '❗',
        'caution': '🔥',
    }

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

        # Format as blockquote
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

    return content, placeholders


def restore_math(html: str, placeholders: list) -> str:
    """Render math and restore placeholders in HTML."""
    for item in placeholders:
        placeholder_id = item['id']
        latex = item['latex']
        display = item['display']

        data_uri = render_latex_to_png(latex, display)

        if data_uri:
            if display:
                replacement = f'''<div style="text-align: center; margin: 1.5em 0; overflow-x: auto;">
                    <img src="{data_uri}" alt="{html_escape(latex)}" style="max-width: 100%;" class="math-display">
                </div>'''
            else:
                replacement = f'<img src="{data_uri}" alt="{html_escape(latex)}" style="vertical-align: middle; display: inline;" class="math-inline">'
            html = html.replace(placeholder_id, replacement)
        else:
            # Fallback: show LaTeX code
            if display:
                html = html.replace(placeholder_id, f'<pre>{html_escape(latex)}</pre>')
            else:
                html = html.replace(placeholder_id, f'<code>{html_escape(latex)}</code>')

    return html


def convert_qmd_to_substack(qmd_path: Path, output_path: Path) -> bool:
    """
    Main conversion function.

    Args:
        qmd_path: Path to .qmd file
        output_path: Output path for HTML file

    Returns:
        True on success, False on failure
    """
    print(f"\n📄 Processing: {qmd_path}")

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

    # Clean Quarto syntax
    print("   Cleaning Quarto syntax...")
    processed_content = clean_quarto_syntax(processed_content)

    # Rewrite links to other posts with Substack URLs
    print("   Rewriting post links...")
    processed_content = rewrite_post_links(processed_content, qmd_path.parent)

    # Embed local images as base64
    print("   Embedding local images...")
    processed_content = embed_local_images(processed_content, qmd_path.parent)

    # Protect math before markdown processing
    print("   Extracting math expressions...")
    protected_content, placeholders = protect_and_render_math(processed_content)
    print(f"   Found {len(placeholders)} math expressions")

    # Convert markdown to HTML
    print("   Converting markdown to HTML...")
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html = md.convert(protected_content)

    # Render math and restore placeholders
    print("   Rendering LaTeX to SVG...")
    html = restore_math(html, placeholders)

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

    # Write output
    output_path.write_text(final_html)

    print(f"\n✅ Success! Saved to: {output_path}")
    print(f"   Math expressions rendered: {len(placeholders)}")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {output_path} in a browser to preview")
    print(f"   2. Select all content (Cmd/Ctrl+A) and copy")
    print(f"   3. Paste into Substack's editor")
    print(f"   4. Review and adjust formatting as needed\n")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert Quarto .qmd files to Substack-compatible HTML with rendered LaTeX"
    )
    parser.add_argument("input", help="Path to .qmd file")
    parser.add_argument("-o", "--output", help="Output HTML file path")
    parser.add_argument("--clear-cache", action="store_true", help="Clear equation cache")

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

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = qmd_path.parent / f"{qmd_path.stem}_substack.html"

    # Convert
    success = convert_qmd_to_substack(qmd_path, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
