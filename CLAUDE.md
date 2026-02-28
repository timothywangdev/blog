# Project Instructions

## Author Information

- **Author name**: Always use `author: "Hujie Wang"` in all blog post frontmatter. Never use any other name.

## Working Style

- **Use multiple agents in parallel whenever possible**: Always prefer launching multiple Task agents in parallel rather than sequentially. This applies to:
  - **Research tasks**: Launch 3-4 agents simultaneously to explore different aspects of a topic, search for papers/tutorials, or gather information from multiple sources
  - **Independent operations**: If tasks don't depend on each other's results, run them in parallel (e.g., reading multiple files, searching different codebases, fetching multiple web resources)
  - **Exploratory work**: When investigating a codebase or concept, spawn parallel agents to examine different areas simultaneously
  - **General rule**: If you can launch tasks in parallel without waiting for sequential results, do it. Maximize parallelism for performance.

- **Draft posts with /polish**: When creating or editing blog posts, follow the guidelines in `.claude/commands/polish.md`

## Blog Structure

- Posts are in `posts/` directory, organized by series (e.g., `posts/diffusion/`, `posts/robotics/`)
- Each post is a Quarto `.qmd` file in its own folder with an `index.qmd`
- Images go in the same directory as the post
- Use `draft: true` in frontmatter for work-in-progress posts

## Tech Stack

- **Quarto** for blog generation (v1.6.42)
- **GitHub Pages** for hosting
- Preview with: `quarto preview <file> --no-browser --no-watch-inputs`

## Known Issues

### Quarto `draft: true` Bug

**Problem**: `draft: true` in frontmatter causes Quarto to output empty HTML (90 bytes) when rendering within a project context. The file renders correctly outside the project.

**Workaround**: Comment out `draft: true` while previewing/editing:

```yaml
# draft: true  # Uncomment when ready to hide from site
```

Or remove `draft: true` entirely and use `.gitignore` or branch strategy for unpublished posts.
