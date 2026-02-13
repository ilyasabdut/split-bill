import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		environment: 'jsdom',
		globals: true,
		setupFiles: ['./src/lib/tests/setup.js'],
		coverage: {
			provider: 'v8',
			reporter: ['text', 'json', 'html'],
			extensions: ['js', 'ts', 'svelte'],
			include: ['src/lib/**/*'],
			exclude: [
				'src/lib/tests/**',
				'src/lib/**/*.test.{js,ts}',
				'src/lib/**/*.spec.{js,ts}',
				'**/*.d.ts',
				'**/*.config.{js,ts}'
			],
			thresholds: {
				lines: 90,
				functions: 90,
				branches: 90,
				statements: 90
			}
		}
	},
	resolve: {
		alias: {
			$lib: '/src/lib',
			$app: '/src/app'
		}
	}
});
