// Generate PWA icons from SVG
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// SVG template for the icon
const iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="80" fill="#0ea5e9"/>
  <text x="256" y="340" font-family="Arial, sans-serif" font-size="240" font-weight="bold" text-anchor="middle" fill="white">$</text>
</svg>`;

// Save SVG icon
fs.writeFileSync(path.join(__dirname, 'icon.svg'), iconSvg);

console.log('Icon SVG generated. You can use online tools to convert to PNG at 192x192 and 512x512 sizes.');
console.log('Recommended: https://www.iloveimg.com/convert-to-png or similar tool');
