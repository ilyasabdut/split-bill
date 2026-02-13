import { render } from '@testing-library/svelte';
import { tick } from 'svelte';

export * from '@testing-library/svelte';

export async function waitFor(callback: () => void | Promise<void>, options: { timeout?: number; interval?: number } = {}) {
	const { timeout = 1000, interval = 50 } = options;
	const startTime = Date.now();

	while (Date.now() - startTime < timeout) {
		try {
			await callback();
			return;
		} catch (error) {
			await new Promise(resolve => setTimeout(resolve, interval));
		}
	}

	throw new Error('Timed out waiting for condition');
}

export function renderWithContext(Component: any, props = {}, context = new Map()) {
	return render(Component, {
		props,
		context: (key: any) => context.get(key)
	});
}

export async function typeInput(input: HTMLInputElement, value: string) {
	input.value = value;
	input.dispatchEvent(new Event('input', { bubbles: true }));
	await tick();
}

export async function clickButton(button: HTMLButtonElement) {
	button.click();
	await tick();
}
