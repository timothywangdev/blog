# AI Models Blog

A blog about AI models, machine learning, and deep learning, built with [Quarto](https://quarto.org/).

## Local Development

1. Install [Quarto](https://quarto.org/docs/get-started/)
2. Preview the site locally:
   ```bash
   quarto preview
   ```

## Adding New Posts

Create a new directory under `posts/` with an `index.qmd` file:

```
posts/
  my-new-post/
    index.qmd
    (optional images and assets)
```

Each post should have front matter like:

```yaml
---
title: "Post Title"
author: "Your Name"
date: "2025-11-27"
categories: [category1, category2]
---
```

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when you push to the `master` branch.

**Important**: After the first deployment, go to your GitHub repository Settings > Pages and set the source to "Deploy from a branch" with the `gh-pages` branch.
# test
