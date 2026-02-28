#!/usr/bin/env python3
"""
Substack to Markdown Converter

Fetches a published Substack post and converts it back to Markdown
for comparison against the source _substack.qmd file.

Usage:
    python substack_to_md.py https://aheadofrobotics.substack.com/p/post-slug
    python substack_to_md.py https://... -o output.md

Requirements:
    pip install requests beautifulsoup4 markdownify
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install requests beautifulsoup4 markdownify")
    sys.exit(1)


def fetch_substack_html(url: str) -> str:
    """Fetch the HTML content of a Substack post."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def extract_article_content(html: str) -> tuple[str, dict]:
    """
    Extract the main article content from Substack HTML.
    Returns (article_html, metadata_dict).
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Extract metadata
    metadata = {}

    # Title
    title_el = soup.find('h1', class_='post-title')
    if title_el:
        metadata['title'] = title_el.get_text(strip=True)

    # Subtitle
    subtitle_el = soup.find('h3', class_='subtitle')
    if subtitle_el:
        metadata['subtitle'] = subtitle_el.get_text(strip=True)

    # Find the main article content
    # Substack uses different selectors, try multiple
    article = None

    # Try the main content area
    for selector in [
        'div.body.markup',
        'div.available-content',
        'article',
        'div.post-content'
    ]:
        article = soup.select_one(selector)
        if article:
            break

    if not article:
        # Fallback: find the largest div with paragraphs
        divs = soup.find_all('div')
        max_p_count = 0
        for div in divs:
            p_count = len(div.find_all('p'))
            if p_count > max_p_count:
                max_p_count = p_count
                article = div

    if not article:
        raise ValueError("Could not find article content in HTML")

    # Clean up the article HTML
    # Remove subscription prompts, buttons, etc.
    for unwanted in article.find_all(['button', 'form', 'script', 'style']):
        unwanted.decompose()

    # Remove Substack-specific UI elements
    for class_pattern in ['subscribe', 'share', 'like', 'comment', 'footer']:
        for el in article.find_all(class_=lambda x: x and class_pattern in x.lower()):
            el.decompose()

    return str(article), metadata


def html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown."""
    markdown = md(
        html,
        heading_style='ATX',
        bullets='-',
        strong_em_symbol='*',
    )
    return markdown


def normalize_markdown(text: str) -> str:
    """Normalize markdown for comparison."""
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Normalize whitespace in lines
    lines = []
    for line in text.split('\n'):
        line = line.rstrip()
        lines.append(line)
    text = '\n'.join(lines)

    # Remove trailing whitespace
    text = text.strip()

    # Normalize heading spacing
    text = re.sub(r'\n(#{1,6})\s+', r'\n\n\1 ', text)

    # Normalize list item spacing
    text = re.sub(r'\n([*-])\s+', r'\n\1 ', text)

    return text


def convert_substack_to_md(url: str) -> tuple[str, dict]:
    """
    Main conversion function.
    Returns (markdown_content, metadata_dict).
    """
    print(f"Fetching: {url}")
    html = fetch_substack_html(url)

    print("Extracting article content...")
    article_html, metadata = extract_article_content(html)

    print("Converting to Markdown...")
    markdown = html_to_markdown(article_html)

    print("Normalizing...")
    markdown = normalize_markdown(markdown)

    return markdown, metadata


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Substack post to Markdown"
    )
    parser.add_argument("url", help="URL of the Substack post")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument("--include-metadata", action="store_true",
                        help="Include YAML frontmatter with metadata")

    args = parser.parse_args()

    try:
        markdown, metadata = convert_substack_to_md(args.url)

        # Optionally add frontmatter
        if args.include_metadata and metadata:
            frontmatter = "---\n"
            for key, value in metadata.items():
                # Escape quotes in values
                value = value.replace('"', '\\"')
                frontmatter += f'{key}: "{value}"\n'
            frontmatter += "---\n\n"
            markdown = frontmatter + markdown

        # Output
        if args.output:
            Path(args.output).write_text(markdown)
            print(f"\n✅ Saved to: {args.output}")
        else:
            print("\n" + "="*60)
            print(markdown)
            print("="*60)

        # Print stats
        lines = markdown.split('\n')
        headings = [l for l in lines if l.startswith('#')]
        images = len(re.findall(r'!\[', markdown))

        print(f"\n📊 Stats:")
        print(f"   Lines: {len(lines)}")
        print(f"   Headings: {len(headings)}")
        print(f"   Images: {images}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
