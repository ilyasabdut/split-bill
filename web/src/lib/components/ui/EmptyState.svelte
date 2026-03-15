<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		icon?: Snippet;
		title: string;
		description?: string;
		action?: {
			label: string;
			onclick: () => void;
		};
		size?: 'sm' | 'md' | 'lg';
	}

	let {
		icon,
		title,
		description,
		action,
		size = 'md'
	}: Props = $props();

	const sizeClasses = $derived({
		sm: { icon: 'h-10 w-10', title: 'text-subheading', desc: 'text-label' },
		md: { icon: 'h-14 w-14', title: 'text-section', desc: 'text-body' },
		lg: { icon: 'h-20 w-20', title: 'text-heading', desc: 'text-subheading' }
	}[size]);
</script>

<div class="flex flex-col items-center justify-center text-center px-6 py-12">
	{#if icon}
		<div class="{sizeClasses.icon} rounded-2xl bg-surface-100 dark:bg-slate-700 text-text-tertiary flex items-center justify-center mb-4">
			{@render icon()}
		</div>
	{/if}

	<h3 class="{sizeClasses.title} font-bold text-text-primary mb-2">{title}</h3>

	{#if description}
		<p class="{sizeClasses.desc} text-text-secondary max-w-xs">{description}</p>
	{/if}

	{#if action}
		<button
			type="button"
			onclick={action.onclick}
			class="mt-6 h-12 px-6 rounded-2xl bg-primary-500 text-text-inverted font-semibold shadow-md hover:bg-primary-600 active:scale-95 transition-all"
		>
			{action.label}
		</button>
	{/if}
</div>
