#!/usr/bin/env python3
"""
Substack Post Validator

Validates a published Substack post against its source _substack.qmd file.
Takes a Playwright accessibility snapshot as input and checks for common issues.

Usage:
    python validate_substack.py path/to/_substack.qmd --snapshot snapshot.txt
    python validate_substack.py path/to/_substack.qmd --snapshot-stdin < snapshot.txt

The snapshot should be the raw text output from Playwright's browser_snapshot tool.

Requirements:
    pip install pyyaml
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install pyyaml")
    sys.exit(1)


@dataclass
class ValidationIssue:
    """A single validation issue found."""
    severity: str  # "critical", "warning", "info"
    category: str  # e.g., "orphaned_punctuation", "callout_formatting"
    message: str
    context: str = ""  # Surrounding text for debugging
    ref: str = ""  # Playwright element reference if available


@dataclass
class ValidationReport:
    """Complete validation report."""
    source_file: str
    substack_url: str
    status: str  # "PASS", "WARNINGS", "FAIL"
    issues: list[ValidationIssue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "substack_url": self.substack_url,
            "status": self.status,
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "context": i.context,
                    "ref": i.ref,
                }
                for i in self.issues
            ],
            "stats": self.stats,
        }

    def to_markdown(self) -> str:
        """Generate a markdown report."""
        status_emoji = {"PASS": "✅", "WARNINGS": "⚠️", "FAIL": "❌"}.get(
            self.status, "❓"
        )

        lines = [
            f"## Validation Report",
            f"",
            f"**Source**: `{self.source_file}`",
            f"**Published**: {self.substack_url}",
            f"**Status**: {status_emoji} {self.status}",
            f"",
            f"### Content Summary",
        ]

        for key, value in self.stats.items():
            lines.append(f"- **{key}**: {value}")

        # Group issues by severity
        critical = [i for i in self.issues if i.severity == "critical"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        info = [i for i in self.issues if i.severity == "info"]

        if critical:
            lines.extend(["", "### ❌ Critical Issues", ""])
            for issue in critical:
                lines.append(f"- **{issue.category}**: {issue.message}")
                if issue.context:
                    lines.append(f"  - Context: `{issue.context[:100]}...`")

        if warnings:
            lines.extend(["", "### ⚠️ Warnings", ""])
            for issue in warnings:
                lines.append(f"- **{issue.category}**: {issue.message}")
                if issue.context:
                    lines.append(f"  - Context: `{issue.context[:100]}...`")

        if info:
            lines.extend(["", "### ℹ️ Info", ""])
            for issue in info:
                lines.append(f"- {issue.message}")

        if not self.issues:
            lines.extend(["", "### ✅ All Checks Passed", ""])

        return "\n".join(lines)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and content from .qmd file."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            return frontmatter or {}, match.group(2)
        except yaml.YAMLError:
            pass
    return {}, content


def extract_qmd_content(qmd_content: str) -> dict:
    """Extract structured content from QMD file."""
    frontmatter, body = parse_frontmatter(qmd_content)

    # Extract headings
    headings = re.findall(r"^(#{2,4})\s+(.+)$", body, re.MULTILINE)

    # Extract images (not equations)
    images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
    # Filter out equation placeholders or data URIs that look like equations
    images = [(alt, src) for alt, src in images if not src.startswith("data:")]

    # Extract callouts
    callout_pattern = r":::\s*\{\.callout-(\w+)[^}]*\}\s*(?:##\s*([^\n]+))?\s*([\s\S]*?):::"
    callouts = []
    for match in re.finditer(callout_pattern, body):
        callout_type = match.group(1)
        title = match.group(2) or ""
        content = match.group(3) or ""
        callouts.append(
            {
                "type": callout_type,
                "title": title.strip(),
                "content": content.strip(),
                "word_count": len(content.split()),
            }
        )

    # Extract block equations
    block_equations = re.findall(r"\$\$([\s\S]+?)\$\$", body)

    # Extract links
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)
    internal_links = [(t, u) for t, u in links if u.startswith("../")]
    external_links = [(t, u) for t, u in links if u.startswith("http")]

    # Extract bullet lists (lines starting with - or *)
    bullet_lists = re.findall(r"^[\-\*]\s+.+$", body, re.MULTILINE)

    # Extract numbered lists (lines starting with 1. 2. etc)
    numbered_lists = re.findall(r"^\d+\.\s+.+$", body, re.MULTILINE)

    return {
        "title": frontmatter.get("title", ""),
        "substack_url": frontmatter.get("substack_url", ""),
        "headings": headings,
        "images": images,
        "callouts": callouts,
        "block_equations": block_equations,
        "internal_links": internal_links,
        "external_links": external_links,
        "bullet_lists": bullet_lists,
        "numbered_lists": numbered_lists,
    }


def parse_snapshot_elements(snapshot: str) -> list[dict]:
    """
    Parse Playwright accessibility snapshot into structured elements.
    Returns list of {type, text, ref, level} dicts.
    """
    elements = []

    # Match patterns like:
    # - heading "Text" [level=2] [ref=e123]
    # - paragraph [ref=e456]: "Text content"
    # - figure [ref=e789]:
    # - link "Text" [ref=e012]:
    # - strong [ref=e345]: "Bold text"

    # Pattern for headings
    for match in re.finditer(
        r'-\s*heading\s+"([^"]+)"\s*\[level=(\d+)\](?:\s*\[ref=(\w+)\])?', snapshot
    ):
        elements.append(
            {
                "type": "heading",
                "text": match.group(1),
                "level": int(match.group(2)),
                "ref": match.group(3) or "",
            }
        )

    # Pattern for paragraphs - handle both formats
    # Format 1: - paragraph [ref=e140]: "."
    # Format 2: - paragraph "Text" [ref=e140]
    for match in re.finditer(
        r'-\s*paragraph\s*(?:\[ref=(\w+)\])?\s*:\s*"([^"]*)"', snapshot
    ):
        elements.append(
            {
                "type": "paragraph",
                "text": match.group(2),
                "ref": match.group(1) or "",
            }
        )

    for match in re.finditer(
        r'-\s*paragraph\s+"([^"]+)"\s*(?:\[ref=(\w+)\])?', snapshot
    ):
        elements.append(
            {
                "type": "paragraph",
                "text": match.group(1),
                "ref": match.group(2) or "",
            }
        )

    # Pattern for figures
    for match in re.finditer(r"-\s*figure\s*\[ref=(\w+)\]", snapshot):
        elements.append(
            {
                "type": "figure",
                "text": "",
                "ref": match.group(1),
            }
        )

    # Pattern for strong/bold text
    for match in re.finditer(
        r'-\s*strong\s*(?:\[ref=(\w+)\])?\s*:\s*"([^"]*)"', snapshot
    ):
        elements.append(
            {
                "type": "strong",
                "text": match.group(2),
                "ref": match.group(1) or "",
            }
        )

    return elements


def check_orphaned_punctuation(snapshot: str, elements: list[dict]) -> list[ValidationIssue]:
    """
    Check for orphaned punctuation (single char paragraphs like ":", "?", ".").
    This indicates an image was placed mid-sentence.
    """
    issues = []
    orphan_pattern = r'-\s*paragraph\s*(?:\[ref=(\w+)\])?\s*:\s*"([:.?!,;])"\s*$'

    for match in re.finditer(orphan_pattern, snapshot, re.MULTILINE):
        ref = match.group(1) or ""
        punct = match.group(2)

        # Find context - look for preceding paragraph text in elements
        context = ""
        for elem in elements:
            if elem["type"] == "paragraph" and len(elem["text"]) > 5:
                context = elem["text"]

        issues.append(
            ValidationIssue(
                severity="critical",
                category="orphaned_punctuation",
                message=f'Found orphaned punctuation "{punct}" as standalone paragraph',
                context=context,
                ref=ref,
            )
        )

    return issues


def check_callout_formatting(snapshot: str, elements: list[dict]) -> list[ValidationIssue]:
    """
    Check for run-together callout type and title like "NoteWhat is...".
    """
    issues = []

    # Pattern: (Note|Warning|Tip|Important|Caution) immediately followed by capital letter
    callout_types = ["Note", "Warning", "Tip", "Important", "Caution"]
    pattern = rf'\b({"|".join(callout_types)})([A-Z][a-zA-Z])'

    for elem in elements:
        text = elem.get("text", "")
        for match in re.finditer(pattern, text):
            callout_type = match.group(1)
            next_chars = match.group(2)
            issues.append(
                ValidationIssue(
                    severity="critical",
                    category="callout_formatting",
                    message=f'Callout type runs into title: "{callout_type}{next_chars}..." (missing separator)',
                    context=text[:80],
                    ref=elem.get("ref", ""),
                )
            )

    # Also check raw snapshot for strong elements with this pattern
    strong_pattern = rf'-\s*strong[^:]*:\s*"({"|".join(callout_types)})([A-Z][^\s"]*[^"]*)"'
    for match in re.finditer(strong_pattern, snapshot):
        callout_type = match.group(1)
        rest = match.group(2)
        full_text = f"{callout_type}{rest}"
        # Avoid duplicates
        if not any(full_text in i.context for i in issues):
            issues.append(
                ValidationIssue(
                    severity="critical",
                    category="callout_formatting",
                    message=f'Callout type runs into title: "{full_text[:50]}..."',
                    context=full_text,
                    ref="",
                )
            )

    return issues


def check_raw_markdown_links(snapshot: str) -> list[ValidationIssue]:
    """Check for raw markdown links that weren't rendered as hyperlinks."""
    issues = []

    # Pattern: [text](url) appearing as literal text in paragraphs
    # This catches markdown links that weren't converted to actual links
    raw_link_pattern = r'paragraph[^:]*:\s*[^"]*"\[([^\]]+)\]\(([^)]+)\)'

    for match in re.finditer(raw_link_pattern, snapshot):
        link_text = match.group(1)
        link_url = match.group(2)
        issues.append(
            ValidationIssue(
                severity="critical",
                category="raw_markdown_link",
                message=f'Raw markdown link not rendered: [{link_text}]({link_url[:30]}...)',
                context=f"Link should be clickable, not literal text",
                ref="",
            )
        )

    return issues


def check_missing_lists(qmd_data: dict, snapshot: str) -> list[ValidationIssue]:
    """Check if source has bullet/numbered lists but snapshot has none."""
    issues = []

    # Count lists in snapshot
    has_list_items = bool(re.search(r'-\s*list\s*\[ref=', snapshot))
    has_listitem = bool(re.search(r'-\s*listitem', snapshot))

    # Check if source has bullet points
    source_has_bullets = len(qmd_data.get("bullet_lists", [])) > 0

    if source_has_bullets and not has_list_items and not has_listitem:
        issues.append(
            ValidationIssue(
                severity="critical",
                category="missing_lists",
                message=f"Source has bullet lists but published version has NO list elements",
                context="All bullet points were converted to plain paragraphs",
                ref="",
            )
        )

    return issues


def check_missing_links(qmd_data: dict, snapshot: str) -> list[ValidationIssue]:
    """Check if hyperlinks from source are missing in published version."""
    issues = []

    # Count links in snapshot
    snapshot_links = len(re.findall(r'-\s*link\s+"[^"]+"\s*\[ref=', snapshot))
    # Also count links in figures (images are links in Substack)
    figure_links = len(re.findall(r'figure.*\n.*link', snapshot))
    total_snapshot_links = snapshot_links + figure_links

    # Get expected link count from source (external + internal)
    source_links = len(qmd_data.get("external_links", [])) + len(qmd_data.get("internal_links", []))

    # If we have significantly fewer links, that's a problem
    if source_links > 0 and total_snapshot_links < source_links // 2:
        issues.append(
            ValidationIssue(
                severity="warning",
                category="missing_links",
                message=f"Source has {source_links} links but only ~{total_snapshot_links} found in published",
                context="Many hyperlinks may not have been converted properly",
                ref="",
            )
        )

    return issues


def check_raw_latex(snapshot: str) -> list[ValidationIssue]:
    """Check for raw LaTeX that wasn't rendered."""
    issues = []

    latex_patterns = [
        (r"\\frac\{", "\\frac{...}"),
        (r"\\mathbb\{", "\\mathbb{...}"),
        (r"\\mathcal\{", "\\mathcal{...}"),
        (r"\\begin\{aligned\}", "\\begin{aligned}"),
        (r"\\nabla", "\\nabla"),
        (r"\\partial", "\\partial"),
        (r"\\alpha(?![a-z])", "\\alpha"),
        (r"\\beta(?![a-z])", "\\beta"),
        (r"\\theta(?![a-z])", "\\theta"),
    ]

    for pattern, display in latex_patterns:
        if re.search(pattern, snapshot):
            issues.append(
                ValidationIssue(
                    severity="critical",
                    category="raw_latex",
                    message=f"Raw LaTeX found: {display} (equation not rendered)",
                    context="",
                    ref="",
                )
            )

    return issues


def check_image_count(qmd_data: dict, snapshot: str) -> list[ValidationIssue]:
    """Check that image counts match."""
    issues = []

    qmd_images = len(qmd_data["images"])
    snapshot_figures = len(re.findall(r"-\s*figure\s*\[ref=", snapshot))

    if qmd_images != snapshot_figures:
        issues.append(
            ValidationIssue(
                severity="critical",
                category="missing_images",
                message=f"Image count mismatch: {qmd_images} in QMD, {snapshot_figures} in Substack",
                context="",
                ref="",
            )
        )

    return issues


def check_heading_count(qmd_data: dict, elements: list[dict]) -> list[ValidationIssue]:
    """Check that major headings are present."""
    issues = []

    qmd_h2 = [h[1] for h in qmd_data["headings"] if h[0] == "##"]
    snapshot_h2 = [e["text"] for e in elements if e["type"] == "heading" and e.get("level") == 2]

    # Check if any QMD headings are missing (fuzzy match)
    for qmd_heading in qmd_h2:
        found = False
        for snap_heading in snapshot_h2:
            # Normalize and compare
            if qmd_heading.lower().strip() in snap_heading.lower() or snap_heading.lower() in qmd_heading.lower():
                found = True
                break
        if not found:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="missing_heading",
                    message=f'Heading may be missing: "{qmd_heading}"',
                    context="",
                    ref="",
                )
            )

    return issues


def check_callout_content(qmd_data: dict, snapshot: str, elements: list[dict]) -> list[ValidationIssue]:
    """Check that callouts have content, not just titles."""
    issues = []

    # Look for callout titles that are immediately followed by another heading
    # This indicates the body was stripped
    callout_types = ["Note", "Warning", "Tip", "Important", "Caution"]

    for callout in qmd_data["callouts"]:
        if callout["word_count"] > 20:  # Only check substantial callouts
            title = callout["title"]
            if title:
                # Check if title appears in snapshot
                title_found = title.lower() in snapshot.lower()
                if not title_found:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            category="callout_content",
                            message=f'Callout may be missing: "{title[:50]}..."',
                            context=f"Expected ~{callout['word_count']} words",
                            ref="",
                        )
                    )

    return issues


def validate(qmd_path: Path, snapshot: str) -> ValidationReport:
    """Run all validation checks and return a report."""
    qmd_content = qmd_path.read_text()
    qmd_data = extract_qmd_content(qmd_content)

    report = ValidationReport(
        source_file=str(qmd_path),
        substack_url=qmd_data["substack_url"],
        status="PASS",
        issues=[],
        stats={
            "headings_in_qmd": len(qmd_data["headings"]),
            "images_in_qmd": len(qmd_data["images"]),
            "callouts_in_qmd": len(qmd_data["callouts"]),
            "equations_in_qmd": len(qmd_data["block_equations"]),
            "internal_links": len(qmd_data["internal_links"]),
            "external_links": len(qmd_data["external_links"]),
            "bullet_list_items": len(qmd_data["bullet_lists"]),
            "numbered_list_items": len(qmd_data["numbered_lists"]),
        },
    )

    # Parse snapshot
    elements = parse_snapshot_elements(snapshot)
    report.stats["elements_in_snapshot"] = len(elements)

    # Run all checks
    report.issues.extend(check_orphaned_punctuation(snapshot, elements))
    report.issues.extend(check_callout_formatting(snapshot, elements))
    report.issues.extend(check_raw_latex(snapshot))
    report.issues.extend(check_raw_markdown_links(snapshot))
    report.issues.extend(check_missing_lists(qmd_data, snapshot))
    report.issues.extend(check_missing_links(qmd_data, snapshot))
    report.issues.extend(check_image_count(qmd_data, snapshot))
    report.issues.extend(check_heading_count(qmd_data, elements))
    report.issues.extend(check_callout_content(qmd_data, snapshot, elements))

    # Determine overall status
    critical_count = sum(1 for i in report.issues if i.severity == "critical")
    warning_count = sum(1 for i in report.issues if i.severity == "warning")

    if critical_count > 0:
        report.status = "FAIL"
    elif warning_count > 0:
        report.status = "WARNINGS"
    else:
        report.status = "PASS"

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Substack post against its source QMD file"
    )
    parser.add_argument("qmd_file", help="Path to the _substack.qmd file")
    parser.add_argument(
        "--snapshot",
        help="Path to file containing Playwright accessibility snapshot",
    )
    parser.add_argument(
        "--snapshot-stdin",
        action="store_true",
        help="Read snapshot from stdin",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of markdown",
    )

    args = parser.parse_args()

    qmd_path = Path(args.qmd_file)
    if not qmd_path.exists():
        print(f"Error: File not found: {qmd_path}", file=sys.stderr)
        sys.exit(1)

    # Read snapshot
    if args.snapshot_stdin:
        snapshot = sys.stdin.read()
    elif args.snapshot:
        snapshot_path = Path(args.snapshot)
        if not snapshot_path.exists():
            print(f"Error: Snapshot file not found: {snapshot_path}", file=sys.stderr)
            sys.exit(1)
        snapshot = snapshot_path.read_text()
    else:
        print("Error: Must provide --snapshot or --snapshot-stdin", file=sys.stderr)
        sys.exit(1)

    # Run validation
    report = validate(qmd_path, snapshot)

    # Output
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.to_markdown())

    # Exit code based on status
    if report.status == "FAIL":
        sys.exit(1)
    elif report.status == "WARNINGS":
        sys.exit(0)  # Warnings don't fail
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
