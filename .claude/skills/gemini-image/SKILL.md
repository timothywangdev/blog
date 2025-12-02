---
name: gemini-image
description: Generate images using Gemini API. Use when the user asks to create, generate, or produce images for blog posts, diagrams, or visual content.
---

# Gemini Image Generation Skill

## When to Use
- User requests image generation
- Need visuals for blog posts
- Creating diagrams or illustrations

## How to Generate Images

Use the `gemini_generate_image` MCP tool with these parameters:

| Parameter | Description | Options |
|-----------|-------------|---------|
| `prompt` | Description of the image | Any text |
| `aspect_ratio` | Image dimensions | "1:1", "16:9", "9:16", "4:3", "3:4" |
| `output_path` | Where to save | Path in `images/` folder |

## Prompt Best Practices

For blog post images:
- Be specific about style: "minimalist diagram", "photorealistic", "hand-drawn sketch"
- Include context: "for a technical blog about machine learning"
- Specify colors if needed: "using blue and white color scheme"

## Example Prompts

**For diffusion blog posts:**
- "A visualization of noise being gradually removed from an image, showing the denoising process in 5 steps, minimalist style with blue gradient"
- "Abstract representation of a probability distribution transforming over time, suitable for a math blog"

**For diagrams:**
- "A clean flowchart showing data flowing from noise to image, technical diagram style"

## Output Location

Save generated images to: `images/generated/`
