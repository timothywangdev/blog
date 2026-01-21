# Project Instructions

## Author Information

- **Author name**: Always use `author: "Hujie Wang"` in all blog post frontmatter. Never use any other name.

## Working Style

- **Use parallel agents**: When researching topics or gathering information, always launch multiple Task agents in parallel (3-4 simultaneously) rather than sequentially. This applies to:
  - Researching different aspects of a topic
  - Searching for papers, tutorials, and explanations
  - Gathering information from multiple sources

- **Draft posts with /polish**: When creating or editing blog posts, follow the guidelines in `.claude/commands/polish.md`

## Blog Structure

- Posts are in `posts/` directory, organized by series (e.g., `posts/diffusion/`, `posts/robotics/`)
- Each post is a Quarto `.qmd` file in its own folder with an `index.qmd`
- Images go in the same directory as the post
- Use `draft: true` in frontmatter for work-in-progress posts

## Tech Stack

- **Quarto** for blog generation
- **GitHub Pages** for hosting
- Preview with: `quarto preview <file> --no-browser --no-watch-inputs`
