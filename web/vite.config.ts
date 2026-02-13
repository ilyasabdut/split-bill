import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
	test: {
		globals: true,
		environment: 'jsdom',
		setupFiles: ['./src/lib/tests/setup.ts'],
		coverage: {
			provider: 'v8',
			reporter: ['text', 'json', 'html'],
			include: ['src/lib/**/*.{js,ts,svelte}'],
			exclude: [
				'src/lib/tests/**',
				'src/lib/**/*.test.{js,ts}',
				'src/lib/**/*.spec.{js,ts}',
				'**/*.d.ts',
				'**/*.config.{js,ts}'
			],
			thresholds: {
				global: {
					branches: 90,
					functions: 90,
					lines: 90,
					statements: 90
				}
			}
		}
	},
	server: {
		port: 15173,
		strictPort: true,
	},
	plugins: [
		sveltekit(),
		VitePWA({

			registerType: 'autoUpdate',
			includeAssets: ['favicon.svg', 'icon-192.png', 'icon-512.png'],
			manifest: {
				name: 'Split Bill',
				short_name: 'SplitBill',
				description: 'Split bills easily with friends',
				theme_color: '#0ea5e9',
				background_color: '#ffffff',
				display: 'standalone',
				orientation: 'portrait',
				scope: '/',
				start_url: '/',
				icons: [
					{
						src: '/icon-192.png',
						sizes: '192x192',
						type: 'image/png',
						purpose: 'any maskable'
					},
					{
						src: '/icon-512.png',
						sizes: '512x512',
						type: 'image/png',
						purpose: 'any maskable'
					}
				],
				categories: ['finance', 'productivity']
			},
			workbox: {
				globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
				runtimeCaching: [
					{
						urlPattern: /^https:\/\/.*/,
						handler: 'NetworkFirst',
						options: {
							cacheName: 'api-cache',
							networkTimeoutSeconds: 10,
							expiration: {
								maxEntries: 100,
								maxAgeSeconds: 60 * 60 * 24
							}
						}
					}
				],
				navigateFallback: '/offline'
			},
			devOptions: {
				enabled: process.env.NODE_ENV !== 'development',
				type: 'module',
			}
		})
	]
});
