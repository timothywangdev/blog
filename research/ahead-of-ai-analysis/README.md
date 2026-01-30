# Ahead of AI Scraper

Automated scraper for Sebastian Raschka's "Ahead of AI" newsletter on Substack.

## Setup

```bash
cd /home/wearaway/projects/blog/research/ahead-of-ai-analysis

# Install dependencies
npm install

# Install Playwright browser
npx playwright install chromium
```

## Usage

### Interactive Mode (recommended for first run)

```bash
npm run scrape
```

This opens a browser window. If you're not logged in:
1. The script will pause and prompt you to log in
2. Log in with your Substack account
3. Navigate back to the main page
4. The script will continue automatically

### What Gets Scraped

For each article:
- Title and subtitle
- Publication date
- Like count
- All images with captions (Substack CDN URLs)
- Full text content
- Paywall status

### Output

Files are saved to `./raw/`:
- `01-article-title.md` - Individual article files
- `index.json` - Machine-readable index
- `index.md` - Human-readable index with table

### Paywall Handling

- Articles behind paywall are marked with `hasPaywall: true`
- If logged in with a paid subscription, full content is scraped
- If not logged in, partial content may be captured

## Configuration

Edit `scrape-ahead-of-ai.js` to customize:

```javascript
// Run headless (no browser window)
const browser = await chromium.launch({
  headless: true,  // Change to true
  slowMo: 100
});
```

## Troubleshooting

**"Timeout waiting for page"**
- Increase timeout in `page.goto()` calls
- Check internet connection

**Missing images**
- Images are stored as URLs, not downloaded
- Substack CDN URLs may expire; re-scrape if needed

**Paywall content missing**
- Ensure you're logged in with a paid subscription
- Wait for login before continuing

## Rate Limiting

The script includes a 2-second delay between articles to be respectful.
Adjust `waitForTimeout(2000)` if needed.
