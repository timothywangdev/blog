#!/usr/bin/env python3
"""
Compare source _substack.qmd against converted Substack markdown.

Usage:
    python compare_md.py source.qmd converted.md
    python compare_md.py source.qmd --url https://substack.com/p/...

Performs:
1. Normalizes both files for comparison
2. Identifies specific issues (orphaned punctuation, callout formatting)
3. Generates a diff report
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

# Import from sibling module
from substack_to_md import convert_substack_to_md


def extract_body(qmd_content: str) -> str:
    """Extract body content from QMD, removing frontmatter."""
    # Remove YAML frontmatter
    match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)$', qmd_content, re.DOTALL)
    if match:
        return match.group(1)
    return qmd_content


def normalize_for_comparison(text: str) -> str:
    """
    Normalize markdown for fair comparison.
    Removes things that legitimately differ between source and published.
    """
    # Remove frontmatter if present
    text = extract_body(text)

    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    # Remove Quarto-specific syntax
    text = re.sub(r'\{#[^}]+\}', '', text)  # Cross-ref labels
    text = re.sub(r'\{\.callout-\w+[^}]*\}', '', text)  # Callout attributes
    text = re.sub(r':::', '', text)  # Div markers

    # Normalize image references (ignore paths, keep alt text)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'![IMAGE: \1]', text)

    # Normalize superscripts (Substack renders these differently)
    text = re.sub(r'\^\[(\d+)\]', r'[\1]', text)  # Quarto footnotes
    text = re.sub(r'<sup>(\d+)</sup>', r'[\1]', text)  # HTML superscripts

    # Normalize headings (remove extra formatting)
    text = re.sub(r'^(#{1,6})\s*\*\*([^*]+)\*\*\s*$', r'\1 \2', text, flags=re.MULTILINE)

    # Strip each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Remove empty lines at start/end
    text = text.strip()

    return text


def find_orphaned_punctuation(text: str) -> list[tuple[int, str]]:
    """Find lines that are just punctuation (orphaned)."""
    issues = []
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped in ['.', '?', ':', ',', ';', '!']:
            # Get context
            context = lines[max(0, i-3):i+2]
            issues.append((i, stripped, context))
    return issues


def find_callout_issues(text: str) -> list[tuple[int, str]]:
    """Find callout type/title run-together patterns."""
    issues = []
    pattern = r'\*\*(Note|Warning|Tip|Important|Caution)([A-Z][^*]*)\*\*'
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        for match in re.finditer(pattern, line):
            callout_type = match.group(1)
            rest = match.group(2)
            issues.append((i, f"{callout_type}{rest[:30]}..."))
    return issues


def generate_diff(source: str, converted: str) -> str:
    """Generate a unified diff between source and converted."""
    source_lines = source.split('\n')
    converted_lines = converted.split('\n')

    diff = difflib.unified_diff(
        source_lines,
        converted_lines,
        fromfile='source (_substack.qmd)',
        tofile='published (Substack)',
        lineterm=''
    )
    return '\n'.join(diff)


def compare(source_path: Path, converted_md: str) -> dict:
    """
    Compare source QMD against converted Substack markdown.
    Returns a report dict.
    """
    source_content = source_path.read_text()

    # Normalize both
    source_norm = normalize_for_comparison(source_content)
    converted_norm = normalize_for_comparison(converted_md)

    # Find issues in converted
    orphaned = find_orphaned_punctuation(converted_md)
    callout_issues = find_callout_issues(converted_md)

    # Generate diff
    diff = generate_diff(source_norm, converted_norm)

    # Count differences
    diff_lines = [l for l in diff.split('\n') if l.startswith('+') or l.startswith('-')]
    diff_lines = [l for l in diff_lines if not l.startswith('+++') and not l.startswith('---')]

    return {
        'source_file': str(source_path),
        'source_lines': len(source_content.split('\n')),
        'converted_lines': len(converted_md.split('\n')),
        'orphaned_punctuation': orphaned,
        'callout_issues': callout_issues,
        'diff': diff,
        'diff_count': len(diff_lines),
    }


def print_report(report: dict):
    """Print a formatted validation report."""
    print("=" * 70)
    print("SUBSTACK VALIDATION REPORT")
    print("=" * 70)
    print(f"\nSource: {report['source_file']}")
    print(f"Source lines: {report['source_lines']}")
    print(f"Converted lines: {report['converted_lines']}")

    # Orphaned punctuation
    print(f"\n{'='*70}")
    print("ORPHANED PUNCTUATION")
    print("="*70)
    if report['orphaned_punctuation']:
        for line_num, punct, context in report['orphaned_punctuation']:
            print(f"\n❌ Line {line_num}: Orphaned '{punct}'")
            print("   Context:")
            for ctx_line in context:
                print(f"   | {ctx_line[:60]}")
    else:
        print("✅ None found")

    # Callout issues
    print(f"\n{'='*70}")
    print("CALLOUT FORMATTING ISSUES")
    print("="*70)
    if report['callout_issues']:
        for line_num, text in report['callout_issues']:
            print(f"❌ Line {line_num}: {text}")
    else:
        print("✅ None found")

    # Diff summary
    print(f"\n{'='*70}")
    print(f"DIFF SUMMARY ({report['diff_count']} changes)")
    print("="*70)
    if report['diff']:
        # Show first 50 lines of diff
        diff_lines = report['diff'].split('\n')
        for line in diff_lines[:50]:
            print(line)
        if len(diff_lines) > 50:
            print(f"\n... ({len(diff_lines) - 50} more lines)")
    else:
        print("✅ No differences found")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("="*70)
    issues = len(report['orphaned_punctuation']) + len(report['callout_issues'])
    if issues == 0 and report['diff_count'] < 10:
        print("✅ PASS - Content matches well")
    elif issues > 0:
        print(f"❌ FAIL - {issues} formatting issues found")
    else:
        print(f"⚠️ WARNING - {report['diff_count']} content differences")


def main():
    parser = argparse.ArgumentParser(
        description="Compare source _substack.qmd against published Substack post"
    )
    parser.add_argument("source", help="Path to source _substack.qmd file")
    parser.add_argument("converted", nargs='?', help="Path to converted markdown file")
    parser.add_argument("--url", help="Fetch and convert from Substack URL instead")

    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    # Get converted markdown
    if args.url:
        print(f"Fetching from Substack: {args.url}")
        converted_md, _ = convert_substack_to_md(args.url)
    elif args.converted:
        converted_path = Path(args.converted)
        if not converted_path.exists():
            print(f"Error: Converted file not found: {converted_path}", file=sys.stderr)
            sys.exit(1)
        converted_md = converted_path.read_text()
    else:
        print("Error: Must provide either converted file path or --url", file=sys.stderr)
        sys.exit(1)

    # Compare
    report = compare(source_path, converted_md)
    print_report(report)

    # Exit code
    issues = len(report['orphaned_punctuation']) + len(report['callout_issues'])
    sys.exit(1 if issues > 0 else 0)


if __name__ == "__main__":
    main()
