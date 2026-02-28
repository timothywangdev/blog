#!/usr/bin/env python3
"""
Rewrite QMD for Substack Compatibility

Automatically fixes common issues that cause problems when pasting to Substack:
1. Callout titles: Add emoji + type prefix (e.g., "## TL;DR" → "## 📝 Note — TL;DR")
2. Punctuation before images: Add continuation text after ? or : before images
3. Tables: Convert to bullet lists (TODO)

Usage:
    python rewrite_for_substack.py input.qmd [-o output.qmd]

Requirements:
    pip install pyyaml
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install pyyaml")
    sys.exit(1)


# Callout type → emoji mapping
CALLOUT_EMOJIS = {
    'note': '📝',
    'tip': '💡',
    'warning': '⚠️',
    'important': '❗',
    'caution': '🔥',
}

# Callout type → display name
CALLOUT_NAMES = {
    'note': 'Note',
    'tip': 'Tip',
    'warning': 'Warning',
    'important': 'Important',
    'caution': 'Caution',
}


def parse_frontmatter(content: str) -> tuple[dict, str, str]:
    """
    Extract YAML frontmatter and body.
    Returns (frontmatter_dict, frontmatter_raw, body).
    """
    match = re.match(r'^(---\s*\n.*?\n---\s*\n)(.*)$', content, re.DOTALL)
    if match:
        frontmatter_raw = match.group(1)
        body = match.group(2)
        # Parse YAML
        yaml_content = re.match(r'^---\s*\n(.*?)\n---', frontmatter_raw, re.DOTALL)
        if yaml_content:
            try:
                frontmatter = yaml.safe_load(yaml_content.group(1))
                return frontmatter or {}, frontmatter_raw, body
            except yaml.YAMLError:
                pass
    return {}, '', content


def fix_callout_titles(content: str) -> tuple[str, list[str]]:
    """
    Fix callout titles to include emoji + type prefix.

    Before: ::: {.callout-note}
            ## TL;DR

    After:  ::: {.callout-note}
            ## 📝 Note — TL;DR

    Returns (fixed_content, list_of_changes).
    """
    changes = []

    # Pattern to match callout blocks with titles
    # Matches: ::: {.callout-TYPE ...}\n## TITLE
    pattern = r'(:::\s*\{\.callout-(\w+)[^}]*\}\s*\n)(##\s*)([^\n]+)'

    def replace_callout(match):
        callout_start = match.group(1)
        callout_type = match.group(2).lower()
        heading_prefix = match.group(3)
        title = match.group(4).strip()

        emoji = CALLOUT_EMOJIS.get(callout_type, '📌')
        type_name = CALLOUT_NAMES.get(callout_type, callout_type.capitalize())

        # Check if title already has the prefix
        if title.startswith(emoji) or title.startswith(f'{type_name}:') or title.startswith(f'{type_name} —'):
            return match.group(0)  # Already fixed

        # Determine separator based on title
        if title in ['TL;DR', 'TLDR', 'Summary']:
            new_title = f"{emoji} {type_name} — {title}"
        else:
            new_title = f"{emoji} {type_name}: {title}"

        changes.append(f"Callout: '{title}' → '{new_title}'")
        return f"{callout_start}{heading_prefix}{new_title}"

    fixed = re.sub(pattern, replace_callout, content)
    return fixed, changes


def fix_punctuation_before_images(content: str) -> tuple[str, list[str]]:
    """
    Fix paragraphs ending with ? or : immediately before images.

    Before: What does MSE loss learn?

            ![image](path.png)

    After:  What does MSE loss learn? The answer is shown below.

            ![image](path.png)

    Returns (fixed_content, list_of_changes).
    """
    changes = []

    # Pattern: paragraph ending with ? or : followed by blank line and image
    # We need to be careful not to match legitimate uses

    # Pattern for question mark before image
    pattern_question = r'(\?)\s*\n\s*\n(!\[[^\]]*\]\([^)]+\))'

    def fix_question(match):
        # Add continuation text
        image = match.group(2)
        changes.append(f"Added continuation after '?' before image")
        return "? The answer is shown below.\n\n" + image

    content = re.sub(pattern_question, fix_question, content)

    # Pattern for colon before image
    pattern_colon = r'(:\s*)\n\s*\n(!\[[^\]]*\]\([^)]+\))'

    def fix_colon(match):
        image = match.group(2)
        changes.append(f"Restructured ':' before image")
        # Replace colon with period and add reference
        return ", as shown below.\n\n" + image

    content = re.sub(pattern_colon, fix_colon, content)

    # Pattern for period at end of sentence with % before image (specific case)
    # e.g., "46.9%." followed by image - the period can get orphaned
    pattern_percent_period = r'(\d+\.?\d*%)\s*\.\s*\n\s*\n(!\[[^\]]*\]\([^)]+\))'

    def fix_percent_period(match):
        percent = match.group(1)
        image = match.group(2)
        changes.append(f"Added continuation after '{percent}.' before image")
        return f"{percent}. The figure below illustrates this.\n\n" + image

    content = re.sub(pattern_percent_period, fix_percent_period, content)

    return content, changes


def add_substack_url_placeholder(frontmatter_raw: str) -> str:
    """Add substack_url field if not present."""
    if 'substack_url:' not in frontmatter_raw:
        # Insert before the closing ---
        return re.sub(
            r'\n---\s*\n$',
            '\nsubstack_url: ""\n---\n',
            frontmatter_raw
        )
    return frontmatter_raw


def rewrite_for_substack(input_path: Path, output_path: Path) -> dict:
    """
    Main rewrite function.
    Returns a report dict with changes made.
    """
    content = input_path.read_text()

    # Parse frontmatter
    frontmatter, frontmatter_raw, body = parse_frontmatter(content)

    report = {
        'input': str(input_path),
        'output': str(output_path),
        'changes': [],
    }

    # Fix callout titles
    body, callout_changes = fix_callout_titles(body)
    report['changes'].extend(callout_changes)

    # Fix punctuation before images
    body, punct_changes = fix_punctuation_before_images(body)
    report['changes'].extend(punct_changes)

    # Add substack_url placeholder
    frontmatter_raw = add_substack_url_placeholder(frontmatter_raw)

    # Combine and write
    output_content = frontmatter_raw + body
    output_path.write_text(output_content)

    report['total_changes'] = len(report['changes'])
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Rewrite QMD for Substack compatibility"
    )
    parser.add_argument("input", help="Input QMD file")
    parser.add_argument("-o", "--output", help="Output file (default: _substack.qmd in same dir)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / "_substack.qmd"

    print(f"📄 Input:  {input_path}")
    print(f"📄 Output: {output_path}")
    print()

    if args.dry_run:
        # Just show what would change
        content = input_path.read_text()
        _, _, body = parse_frontmatter(content)

        _, callout_changes = fix_callout_titles(body)
        _, punct_changes = fix_punctuation_before_images(body)

        all_changes = callout_changes + punct_changes

        print("🔍 Changes that would be made:")
        for change in all_changes:
            print(f"   • {change}")
        print(f"\nTotal: {len(all_changes)} changes")
        return

    # Do the rewrite
    report = rewrite_for_substack(input_path, output_path)

    print("✅ Changes made:")
    for change in report['changes']:
        print(f"   • {change}")

    print(f"\n📊 Total: {report['total_changes']} changes")
    print(f"\n✅ Saved to: {output_path}")


if __name__ == "__main__":
    main()
