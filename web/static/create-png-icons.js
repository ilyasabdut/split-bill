// Create PNG icons for PWA
import { createCanvas } from 'canvas';
import fs from 'fs';

function createIcon(size) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');

  // Background
  ctx.fillStyle = '#0ea5e9';
  ctx.fillRect(0, 0, size, size);

  // Rounded corners
  const radius = size * 0.15;
  ctx.globalCompositeOperation = 'destination-in';
  ctx.beginPath();
  ctx.moveTo(radius, 0);
  ctx.lineTo(size - radius, 0);
  ctx.quadraticCurveTo(size, 0, size, radius);
  ctx.lineTo(size, size - radius);
  ctx.quadraticCurveTo(size, size, size - radius, size);
  ctx.lineTo(radius, size);
  ctx.quadraticCurveTo(0, size, 0, size - radius);
  ctx.lineTo(0, radius);
  ctx.quadraticCurveTo(0, 0, radius, 0);
  ctx.closePath();
  ctx.fill();

  // Reset composite operation
  ctx.globalCompositeOperation = 'source-over';

  // Dollar sign
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${size * 0.5}px Arial, sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('$', size / 2, size / 2);

  return canvas.toBuffer('image/png');
}

// Create icons
try {
  // 192x192 icon
  const icon192 = createIcon(192);
  fs.writeFileSync('icon-192.png', icon192);
  console.log('✅ Created icon-192.png');

  // 512x512 icon
  const icon512 = createIcon(512);
  fs.writeFileSync('icon-512.png', icon512);
  console.log('✅ Created icon-512.png');

  console.log('\nAll PWA icons created successfully!');
} catch (error) {
  console.error('Failed to create icons:', error);
  console.log('\n⚠️  Please install canvas package: npm install canvas');
}
