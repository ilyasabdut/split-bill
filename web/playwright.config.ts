import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Lightpanda browser integration
 *
 * This configuration connects to Lightpanda via Chrome DevTools Protocol (CDP)
 * on ws://127.0.0.1:9222. Start Lightpanda first with: npm run lightpanda:start
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: 'html',

  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Start Lightpanda CDP server before running tests
  // webServer: {
  //   command: 'npm run lightpanda:start',
  //   port: 9222,
  //   reuseExistingServer: !process.env.CI,
  // },
});
