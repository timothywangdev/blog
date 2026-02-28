---
name: download-arxiv
description: Download arXiv paper HTML to post folder for reference
---

# Download arXiv Paper

Download the HTML version of an arXiv paper to the current post's folder for reference while writing.

## Usage

```
/download-arxiv <arxiv_id_or_url> [output_folder]
```

**Examples:**
- `/download-arxiv 2303.04137` — Downloads to current directory
- `/download-arxiv https://arxiv.org/abs/2303.04137 posts/robotics/1-diffusion-policy/`

## How It Works

1. Extract arXiv ID from URL or use directly (e.g., `2303.04137`)
2. Try ar5iv HTML rendering first (better formatting)
3. Fall back to arxiv HTML if ar5iv fails
4. Save as `paper_<arxiv_id>.html` in the target folder

## Command

```bash
# Extract arxiv ID and download
ARXIV_ID="2303.04137"  # or extract from URL
OUTPUT_DIR="."  # or specified folder

curl -L -o "${OUTPUT_DIR}/paper_${ARXIV_ID}.html" \
  "https://ar5iv.labs.arxiv.org/html/${ARXIV_ID}" 2>/dev/null || \
curl -L -o "${OUTPUT_DIR}/paper_${ARXIV_ID}.html" \
  "https://arxiv.org/html/${ARXIV_ID}" 2>/dev/null

# Verify download
ls -la "${OUTPUT_DIR}/paper_${ARXIV_ID}.html"
```

## Notes

- ar5iv provides better HTML rendering than arxiv's native HTML
- Some older papers may not have HTML versions (only PDF)
- Downloaded files should NOT be committed to git (add to `.gitignore`)
- Use for reference while writing, then delete

## Cleanup

Add to `.gitignore`:
```
posts/**/paper_*.html
```
