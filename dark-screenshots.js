const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 375, height: 812 } });
  
  const pages = [
    { url: '/', name: 'dashboard' },
    { url: '/receipt', name: 'receipt' },
    { url: '/split', name: 'split' },
    { url: '/history', name: 'history' },
    { url: '/settings', name: 'settings' },
  ];
  
  for (const p of pages) {
    console.log(`Capturing ${p.name} dark mode...`);
    await page.goto(`http://localhost:5173${p.url}`, { waitUntil: 'networkidle' });
    
    // Enable dark mode
    await page.evaluate(() => {
      localStorage.setItem('darkMode', 'true');
      document.documentElement.classList.add('dark');
    });
    
    await page.waitForTimeout(500);
    await page.screenshot({ path: `/tmp/${p.name}-dark.png` });
  }
  
  await browser.close();
  console.log('Done!');
}

main();
