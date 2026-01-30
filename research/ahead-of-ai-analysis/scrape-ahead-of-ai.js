/**
 * Ahead of AI Scraper
 *
 * Scrapes all articles from Sebastian Raschka's "Ahead of AI" newsletter
 * Extracts: title, subtitle, date, images with captions, and full text
 *
 * Usage:
 *   node scrape-ahead-of-ai.js
 *
 * Prerequisites:
 *   npm install playwright
 *   npx playwright install chromium
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://magazine.sebastianraschka.com';
const OUTPUT_DIR = path.join(__dirname, 'raw');
const PROGRESS_FILE = path.join(OUTPUT_DIR, 'progress.json');

// Create output directory if it doesn't exist
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Load progress from previous run
 */
function loadProgress() {
  if (fs.existsSync(PROGRESS_FILE)) {
    return JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf8'));
  }
  return { scrapedUrls: [], articles: [] };
}

/**
 * Save progress incrementally
 */
function saveProgress(progress) {
  fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
}

/**
 * Extract article URLs from the archive page
 */
async function getArticleUrls(page) {
  await page.goto(`${BASE_URL}/archive?sort=new`, { waitUntil: 'networkidle' });

  // Scroll to load all articles (archive uses infinite scroll)
  let previousHeight = 0;
  let currentHeight = await page.evaluate(() => document.body.scrollHeight);

  while (previousHeight < currentHeight) {
    previousHeight = currentHeight;
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1500);
    currentHeight = await page.evaluate(() => document.body.scrollHeight);
  }

  // Extract all article URLs
  const urls = await page.evaluate(() => {
    const links = document.querySelectorAll('a[data-testid="post-preview-title"]');
    return Array.from(links).map(link => ({
      url: link.href,
      title: link.innerText.trim()
    }));
  });

  console.log(`Found ${urls.length} articles in archive`);
  return urls;
}

/**
 * Extract content from a single article page
 */
async function scrapeArticle(page, url) {
  console.log(`Scraping: ${url}`);

  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });

    // Check for paywall
    const isPaywalled = await page.evaluate(() => {
      return document.querySelector('.paywall') !== null ||
             document.querySelector('[class*="paywall"]') !== null ||
             document.body.innerText.includes('This post is for paid subscribers');
    });

    if (isPaywalled) {
      console.log(`  -> Paywall detected, checking if logged in...`);
    }

    // Extract article content
    const content = await page.evaluate(() => {
      const title = document.querySelector('h1.post-title')?.innerText ||
                    document.querySelector('h1')?.innerText || '';
      const subtitle = document.querySelector('h3.subtitle')?.innerText || '';
      const date = document.querySelector('time')?.innerText || '';
      const likes = document.querySelector('[class*="like-count"]')?.innerText || '';

      const bodyEl = document.querySelector('.body.markup') || document.querySelector('article');

      // Extract images with captions
      const images = [];
      if (bodyEl) {
        bodyEl.querySelectorAll('img').forEach((img) => {
          if (img.src && !img.src.includes('avatar') && !img.src.includes('logo') && img.src.includes('substack')) {
            images.push({
              src: img.src,
              caption: img.closest('figure')?.querySelector('figcaption')?.innerText || img.alt || ''
            });
          }
        });
      }

      // Extract full text
      const textContent = bodyEl?.innerText || '';

      // Check if content seems truncated (paywall)
      const hasPaywall = document.querySelector('.paywall') !== null ||
                         textContent.includes('This post is for paid subscribers') ||
                         textContent.length < 1000;

      return {
        title,
        subtitle,
        date,
        likes,
        url: window.location.href,
        imageCount: images.length,
        images,
        textContent,
        hasPaywall
      };
    });

    return content;
  } catch (error) {
    console.error(`  -> Error scraping ${url}: ${error.message}`);
    return null;
  }
}

/**
 * Convert article content to markdown format
 */
function articleToMarkdown(article) {
  let md = `# ${article.title}\n\n`;

  if (article.subtitle) {
    md += `**Subtitle:** ${article.subtitle}\n\n`;
  }

  md += `**Date:** ${article.date}\n\n`;
  md += `**URL:** ${article.url}\n\n`;

  if (article.likes) {
    md += `**Likes:** ${article.likes}\n\n`;
  }

  md += `**Image Count:** ${article.imageCount}\n\n`;

  if (article.hasPaywall) {
    md += `**Status:** PAYWALL - Content may be incomplete\n\n`;
  }

  md += `---\n\n`;

  // Images section
  if (article.images.length > 0) {
    md += `## Images\n\n`;
    article.images.forEach((img, idx) => {
      md += `${idx + 1}. ![Figure](${img.src})\n`;
      if (img.caption) {
        md += `   - Caption: ${img.caption}\n`;
      }
      md += `\n`;
    });
    md += `---\n\n`;
  }

  // Full text content
  md += `## Full Text Content\n\n`;
  md += article.textContent;

  return md;
}

/**
 * Generate a filename from article title
 */
function generateFilename(index, title) {
  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 60);

  return `${String(index).padStart(2, '0')}-${slug}.md`;
}

/**
 * Main scraping function
 */
async function main() {
  console.log('=== Ahead of AI Scraper ===\n');

  // Use persistent context to remember login credentials
  const userDataDir = path.join(__dirname, '.browser-data');

  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: false,  // Set to true for headless mode after first login
    slowMo: 100,      // Slow down for stability
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  // Get existing page or create new one
  const pages = context.pages();
  const page = pages.length > 0 ? pages[0] : await context.newPage();

  // Check if we need to log in
  console.log('Navigating to Ahead of AI...');
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });

  // Check login status by looking for subscription indicator
  const checkLoginStatus = async () => {
    return await page.evaluate(() => {
      // Check for signs of being logged in
      const hasSettings = document.body.innerText.includes('Settings');
      const hasUserMenu = document.querySelector('[class*="user-indicator"]') !== null;
      const hasSubscribeButton = document.querySelector('button[class*="subscribe"]') !== null;
      const hasSignIn = document.body.innerText.includes('Sign in');

      // Logged in if we see settings/user menu OR don't see subscribe/sign in buttons
      return hasSettings || hasUserMenu || (!hasSubscribeButton && !hasSignIn);
    });
  };

  let isLoggedIn = await checkLoginStatus();

  if (!isLoggedIn) {
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║                    LOGIN REQUIRED                          ║');
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log('║  1. Click "Sign in" in the browser window                  ║');
    console.log('║  2. Complete the login process                             ║');
    console.log('║  3. Once logged in, the script will auto-detect and start  ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');
    console.log('Waiting for login... (5 minute timeout)\n');

    // Poll for login status every 3 seconds
    const startTime = Date.now();
    const timeout = 300000; // 5 minutes

    while (!isLoggedIn && (Date.now() - startTime) < timeout) {
      await page.waitForTimeout(3000);

      // Check if URL changed (user navigated to login page and back)
      const currentUrl = page.url();
      if (currentUrl.includes('login') || currentUrl.includes('sign')) {
        console.log('  Login page detected, waiting for completion...');
      }

      // Re-check login status
      try {
        isLoggedIn = await checkLoginStatus();
        if (isLoggedIn) {
          console.log('  ✓ Login detected!\n');
          break;
        }
      } catch (e) {
        // Page might be navigating, wait and retry
        await page.waitForTimeout(1000);
      }
    }

    if (!isLoggedIn) {
      console.log('Login timeout. Continuing anyway (some content may be paywalled).\n');
    }
  } else {
    console.log('✓ Already logged in!\n');
  }

  // Get all article URLs
  const articleUrls = await getArticleUrls(page);

  // Load progress from previous run
  const progress = loadProgress();
  console.log(`\nPreviously scraped: ${progress.scrapedUrls.length} articles`);

  // Create index for tracking
  const index = {
    scrapedOn: new Date().toISOString(),
    source: BASE_URL,
    totalArticles: articleUrls.length,
    articles: progress.articles || []
  };

  // Scrape each article
  for (let i = 0; i < articleUrls.length; i++) {
    const { url, title } = articleUrls[i];

    // Skip if already scraped
    if (progress.scrapedUrls.includes(url)) {
      console.log(`\n[${i + 1}/${articleUrls.length}] ${title} (already scraped, skipping)`);
      continue;
    }

    console.log(`\n[${i + 1}/${articleUrls.length}] ${title}`);

    const article = await scrapeArticle(page, url);

    if (article && article.textContent.length > 100) {
      const filename = generateFilename(i + 1, article.title);
      const filepath = path.join(OUTPUT_DIR, filename);

      const markdown = articleToMarkdown(article);
      fs.writeFileSync(filepath, markdown);

      console.log(`  -> Saved: ${filename} (${article.imageCount} images, ${article.textContent.length} chars)`);

      const articleMeta = {
        index: i + 1,
        title: article.title,
        date: article.date,
        url: article.url,
        filename,
        imageCount: article.imageCount,
        wordCount: article.textContent.split(/\s+/).length,
        hasPaywall: article.hasPaywall
      };

      index.articles.push(articleMeta);
      progress.scrapedUrls.push(url);
      progress.articles.push(articleMeta);

      // Save progress after each article
      saveProgress(progress);
    } else {
      console.log(`  -> Skipped (no content or error)`);
    }

    // Be polite - add delay between requests
    await page.waitForTimeout(2000);
  }

  // Save index file
  const indexPath = path.join(OUTPUT_DIR, 'index.json');
  fs.writeFileSync(indexPath, JSON.stringify(index, null, 2));
  console.log(`\nSaved index to: ${indexPath}`);

  // Generate markdown index
  let indexMd = `# Ahead of AI - Scraped Articles Index\n\n`;
  indexMd += `**Scraped on:** ${index.scrapedOn}\n\n`;
  indexMd += `**Source:** ${BASE_URL}\n\n`;
  indexMd += `**Total Articles:** ${index.totalArticles}\n\n`;
  indexMd += `---\n\n`;
  indexMd += `## Articles\n\n`;
  indexMd += `| # | Title | Date | Images | Words | Status |\n`;
  indexMd += `|---|-------|------|--------|-------|--------|\n`;

  for (const article of index.articles) {
    const status = article.hasPaywall ? '🔒 Paywall' : '✅ Complete';
    indexMd += `| ${article.index} | [${article.title}](${article.filename}) | ${article.date} | ${article.imageCount} | ~${article.wordCount} | ${status} |\n`;
  }

  fs.writeFileSync(path.join(OUTPUT_DIR, 'index.md'), indexMd);

  console.log('\n=== Scraping Complete ===');
  console.log(`Total articles: ${index.articles.length}`);
  console.log(`Paywalled: ${index.articles.filter(a => a.hasPaywall).length}`);
  console.log(`Complete: ${index.articles.filter(a => !a.hasPaywall).length}`);
  console.log(`\nLogin credentials saved to: ${userDataDir}`);
  console.log('Future runs will reuse your login automatically.');

  await context.close();
}

main().catch(console.error);
