# Project Instructions

## Author Information

- **Author name**: Always use `author: "Hujie Wang"` in all blog post frontmatter. Never use any other name.

## Working Style

- **Always spawn a team of agents**: Default to parallel agent teams for every non-trivial task. Never execute passes or subtasks sequentially when they can run concurrently. This is not an optimization — it is the required approach.
  - **Research tasks**: Launch 3-4 agents simultaneously to explore different aspects of a topic, search for papers/tutorials, or gather information from multiple sources
  - **Polish/editing runs**: Spawn all pass-agents at once (structure, math, credibility, visuals) — never do passes one at a time
  - **Independent operations**: If tasks don't depend on each other's results, run them in parallel (reading multiple files, searching different codebases, fetching multiple web resources)
  - **Exploratory work**: Spawn parallel agents to examine different areas of a codebase or concept simultaneously
  - **Enforcement**: If you find yourself about to do a second sequential task, stop and ask whether it could have been launched in parallel with the first

- **Draft posts with /polish**: When creating or editing blog posts, follow the guidelines in `.claude/commands/polish.md`

## Thinking Principles

- **Surface assumptions explicitly**: For complex decisions, identify and state key assumptions before proceeding.
- **Steelman alternatives**: When recommending an approach, present the strongest case for alternatives. Develop competing hypotheses for research tasks.
- **Trace to first principles**: For technical decisions, reason from fundamental truths rather than conventions or analogies.
- **Self-check before concluding**: Verify your answer against original requirements and constraints before finishing.
- **State uncertainty directly**: When confidence is low, say so explicitly with reasoning.

## Blog Structure

- Posts are in `posts/` directory, organized by series (e.g., `posts/diffusion/`, `posts/robotics/`)
- Each post is a Quarto `.qmd` file in its own folder with an `index.qmd`
- Images go in the same directory as the post
- Use `draft: true` in frontmatter for work-in-progress posts

## Skills

- **arxivsub-skill**: Use `/arxivsub-skill` to search academic papers via the arXivSub API. Covers arXiv and major AI/CV conferences (CVPR, ICCV, ICLR, ICML, NeurIPS, AAAI, MICCAI). Use for finding recent research when writing blog posts.

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
