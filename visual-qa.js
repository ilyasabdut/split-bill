const { chromium } = require('playwright');

const pages = [
  { url: '/', name: 'Dashboard' },
  { url: '/receipt', name: 'Receipt' },
  { url: '/split', name: 'Create Split' },
  { url: '/history', name: 'History' },
  { url: '/settings', name: 'Settings' },
];

const issues = [];

async function checkPage(page, url, name) {
  console.log(`\n📄 Checking ${name} (${url})...`);
  
  try {
    await page.goto(`http://localhost:5173${url}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    
    // 1. Check for horizontal scroll (overflow)
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth + 5;
    });
    
    if (hasHorizontalScroll) {
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
      issues.push({ page: name, issue: `⚠️ Horizontal overflow: scrollWidth=${scrollWidth}, clientWidth=${clientWidth}` });
    }
    
    // 2. Check for clipped elements at edges (real content, not Svelte internals)
    const clippedElements = await page.evaluate(() => {
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      const results = [];
      
      // Get all meaningful elements
      const selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a', 'button', 'input', 'div[role]', 'article', 'section'];
      const elements = [];
      
      for (const sel of selectors) {
        try {
          document.querySelectorAll(sel).forEach(el => {
            const rect = el.getBoundingClientRect();
            const text = el.textContent?.trim();
            if (rect.width > 10 && rect.height > 10 && text && text.length > 2) {
              elements.push({ tag: el.tagName, rect, text: text.slice(0, 40) });
            }
          });
        } catch (e) {}
      }
      
      // Check for clipped elements
      for (const el of elements) {
        if (el.rect.right > viewportWidth - 2 && el.rect.width > 30) {
          results.push(`"${el.text}" clipped at right edge`);
        }
        if (el.rect.bottom > viewportHeight - 80 && el.rect.height > 30) { // Account for bottom nav
          results.push(`"${el.text}" clipped at bottom`);
        }
        if (el.rect.left < 2 && el.rect.width > 30) {
          results.push(`"${el.text}" clipped at left edge`);
        }
      }
      
      return results.slice(0, 3);
    });
    
    if (clippedElements.length > 0) {
      issues.push({ page: name, issue: `⚠️ Clipped elements: ${clippedElements.join('; ')}` });
    }
    
    // 3. Check centered content
    const centerCheck = await page.evaluate(() => {
      const viewportWidth = window.innerWidth;
      const main = document.querySelector('main');
      if (!main) return null;
      
      const rect = main.getBoundingClientRect();
      const center = viewportWidth / 2;
      const elementCenter = rect.left + rect.width / 2;
      const offset = Math.abs(center - elementCenter);
      
      if (offset > 50 && rect.width > 100) {
        return `Main content ${offset.toFixed(0)}px off-center (width: ${rect.width.toFixed(0)})`;
      }
      return null;
    });
    
    if (centerCheck) {
      issues.push({ page: name, issue: `⚠️ ${centerCheck}` });
    }
    
    // 4. Take screenshot for manual review
    await page.screenshot({ path: `/tmp/${name.replace(/\s+/g, '-')}-light.png`, fullPage: false });
    console.log(`   ✅ ${name} - light mode OK (screenshot saved)`);
    
  } catch (e) {
    issues.push({ page: name, issue: `❌ Error: ${e.message}` });
    console.log(`   ❌ ${name} failed: ${e.message}`);
  }
}

async function checkDarkMode(page) {
  console.log('\n🌙 Checking Dark Mode...');
  
  // Enable dark mode via localStorage and class
  for (const p of pages) {
    console.log(`   Checking ${p.name} in dark mode...`);
    try {
      await page.goto(`http://localhost:5173${p.url}`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(500);
      
      // Set dark mode
      await page.evaluate(() => {
        localStorage.setItem('theme', 'dark');
        document.documentElement.classList.add('dark');
      });
      
      await page.reload({ waitUntil: 'networkidle' });
      await page.waitForTimeout(1000);
      
      // Check for contrast issues
      const darkIssues = await page.evaluate(() => {
        const issues = [];
        const body = document.body;
        const bgColor = window.getComputedStyle(body).backgroundColor;
        
        // Parse RGB
        const rgbMatch = bgColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        let bgBrightness = 128;
        if (rgbMatch) {
          bgBrightness = (parseInt(rgbMatch[1]) + parseInt(rgbMatch[2]) + parseInt(rgbMatch[3])) / 3;
        }
        
        // Check if background is too light for dark mode
        if (bgBrightness > 180) {
          issues.push(`Background too light: ${bgColor} (brightness: ${bgBrightness.toFixed(0)})`);
        }
        
        // Check text contrast
        const textElements = document.querySelectorAll('h1, h2, h3, p, span, a, button');
        let lowContrastCount = 0;
        
        for (const el of textElements) {
          const color = window.getComputedStyle(el).color;
          const textMatch = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
          if (textMatch) {
            const textBrightness = (parseInt(textMatch[1]) + parseInt(textMatch[2]) + parseInt(textMatch[3])) / 3;
            const contrast = Math.abs(textBrightness - bgBrightness);
            if (contrast < 30) {
              lowContrastCount++;
            }
          }
          if (lowContrastCount > 5) break;
        }
        
        if (lowContrastCount > 3) {
          issues.push(`Low contrast text detected (${lowContrastCount} elements)`);
        }
        
        return issues;
      });
      
      if (darkIssues.length > 0) {
        issues.push({ page: `${p.name} (dark mode)`, issue: `⚠️ ${darkIssues.join('; ')}` });
      }
      
      // Screenshot
      await page.screenshot({ path: `/tmp/${p.name.replace(/\s+/g, '-')}-dark.png`, fullPage: false });
      console.log(`   ✅ ${p.name} - dark mode OK (screenshot saved)`);
      
    } catch (e) {
      issues.push({ page: `${p.name} (dark mode)`, issue: `❌ Error: ${e.message}` });
    }
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 }, // iPhone X size
  });
  const page = await context.newPage();
  
  console.log('🔍 Visual QA Check - Split Bill App');
  console.log('=====================================');
  
  // Check Light Mode pages
  for (const p of pages) {
    await checkPage(page, p.url, p.name);
  }
  
  // Check Dark Mode
  await checkDarkMode(page);
  
  await browser.close();
  
  console.log('\n=====================================');
  console.log('📊 SUMMARY');
  console.log('=====================================');
  console.log('\nScreenshots saved to /tmp/');
  
  if (issues.length === 0) {
    console.log('\n✅ No visual issues found!');
  } else {
    console.log(`\n❌ Found ${issues.length} issue(s):\n`);
    for (const issue of issues) {
      console.log(`  ${issue.page}:`);
      console.log(`    ${issue.issue}\n`);
    }
  }
  
  process.exit(issues.length > 0 ? 1 : 0);
}

main().catch(console.error);
