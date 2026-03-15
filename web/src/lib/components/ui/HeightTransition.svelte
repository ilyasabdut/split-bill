<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		show: boolean;
		duration?: number;
		easing?: string;
		children: Snippet;
	}

	let {
		show,
		duration = 200,
		easing = 'cubic-bezier(0.25, 1, 0.5, 1)',
		children
	}: Props = $props();

	let contentElement: HTMLElement;
	let height = $state(0);
	let opacity = $state(0);

	$effect(() => {
		if (!contentElement) return;

		if (show) {
			// Measure the actual height
			height = contentElement.offsetHeight;
			opacity = 1;
		} else {
			height = 0;
			opacity = 0;
		}
	});
</script>

{#if show || height > 0}
	<div
		bind:this={contentElement}
		style="height: {height}px; opacity: {opacity}; overflow: hidden; transition: height {duration}ms {easing}, opacity {duration}ms {easing};"
	>
		{@render children()}
	</div>
{/if}
