const puppeteer = require('puppeteer-core');

const CHROMIUM_PATH = '/home/ubuntu/.cache/ms-playwright/chromium-1208/chrome-linux/chrome';

async function takeScreenshot(url, filename, viewport = { width: 390, height: 844 }) {
  const browser = await puppeteer.launch({
    executablePath: CHROMIUM_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });

  const page = await browser.newPage();
  await page.setViewport(viewport);
  
  console.log(`Navigating to ${url}...`);
  await page.goto(url, { waitUntil: 'networkidle0' });
  
  await new Promise(r => setTimeout(r, 1000));
  
  console.log(`Taking screenshot: ${filename}`);
  await page.screenshot({ path: filename, fullPage: false });
  
  await browser.close();
  console.log(`Saved: ${filename}`);
}

const routes = [
  { path: '/', filename: 'snapshots/current-home.png', name: 'Home' },
  { path: '/history', filename: 'snapshots/current-history.png', name: 'History' },
  { path: '/receipt', filename: 'snapshots/current-receipt.png', name: 'Receipt' },
  { path: '/settings', filename: 'snapshots/current-settings.png', name: 'Settings' },
  { path: '/split', filename: 'snapshots/current-split.png', name: 'Split' },
];

async function main() {
  const baseUrl = process.env.URL || 'http://localhost:5173';
  
  for (const route of routes) {
    try {
      await takeScreenshot(`${baseUrl}${route.path}`, route.filename);
    } catch (err) {
      console.error(`Error capturing ${route.name}:`, err.message);
    }
  }
  
  console.log('All screenshots captured!');
}

main();
