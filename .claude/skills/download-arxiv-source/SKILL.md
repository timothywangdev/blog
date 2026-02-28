---
name: download-arxiv-source
description: Download arXiv paper LaTeX source for reference
---

# Download arXiv LaTeX Source

Download the original LaTeX source of an arXiv paper — equations are already perfect LaTeX.

## Usage

```
/download-arxiv-source <arxiv_id_or_url> [output_folder]
```

**Examples:**
- `/download-arxiv-source 2010.02502` — Downloads DDIM paper source
- `/download-arxiv-source https://arxiv.org/abs/2303.04137 posts/robotics/1-diffusion-policy/`

## Command

```bash
ARXIV_ID="2010.02502"  # or extract from URL
OUTPUT_DIR="."

# Download and extract source
wget -q "https://arxiv.org/e-print/${ARXIV_ID}" -O "${OUTPUT_DIR}/source_${ARXIV_ID}.tar.gz"
mkdir -p "${OUTPUT_DIR}/source_${ARXIV_ID}"
tar -xzf "${OUTPUT_DIR}/source_${ARXIV_ID}.tar.gz" -C "${OUTPUT_DIR}/source_${ARXIV_ID}" 2>/dev/null || \
  # Sometimes it's just a .tex file, not tarred
  mv "${OUTPUT_DIR}/source_${ARXIV_ID}.tar.gz" "${OUTPUT_DIR}/source_${ARXIV_ID}/main.tex"

# List extracted files
ls -la "${OUTPUT_DIR}/source_${ARXIV_ID}/"
```

## Why LaTeX Source > PDF Conversion

| Approach | Equation Quality | Speed |
|----------|------------------|-------|
| **LaTeX source** | Perfect (original) | Instant |
| Nougat (PDF→MD) | Good (95%+) | Slow |
| Marker (PDF→MD) | Okay (90%+) | Fast |
| ar5iv HTML | Good but verbose | Instant |

## Tips

- Main content is usually in `main.tex` or `paper.tex`
- Search for equation labels: `grep -n "\\label{eq:" *.tex`
- Find specific equations: `grep -A5 "\\begin{equation}" *.tex`

## Cleanup

Add to `.gitignore`:
```
posts/**/source_*/
```
