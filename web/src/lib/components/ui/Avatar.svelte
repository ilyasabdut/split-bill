<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';

	interface Props extends HTMLAttributes<HTMLDivElement> {
		src?: string;
		alt?: string;
		name?: string;
		size?: 'sm' | 'md' | 'lg';
		variant?: 'solid' | 'soft';
		color?: 'slate' | 'primary' | 'emerald' | 'rose' | 'amber' | 'violet' | 'indigo' | 'pink' | 'sky' | 'orange';
		class?: string;
	}

	const {
		src,
		alt = '',
		name = '',
		size = 'md',
		variant = 'soft',
		color = 'slate',
		class: className = '',
		...restProps
	}: Props = $props();

	const sizeClasses = {
		sm: 'h-6 w-6 text-[9px]',
		md: 'h-10 w-10 text-sm',
		lg: 'h-12 w-12 text-base',
	};

	const colorClasses = {
		slate: {
			solid: 'bg-text-tertiary text-text-inverted',
			soft: 'bg-surface-200 text-text-secondary ring-2 ring-surface-0',
		},
		primary: {
			solid: 'bg-primary-600 text-text-inverted',
			soft: 'bg-primary-100 text-primary-700 ring-2 ring-surface-0',
		},
		emerald: {
			solid: 'bg-success text-text-inverted',
			soft: 'bg-success/10 text-success ring-2 ring-surface-0',
		},
		rose: {
			solid: 'bg-error text-text-inverted',
			soft: 'bg-error/10 text-error ring-2 ring-surface-0',
		},
		amber: {
			solid: 'bg-warning text-text-inverted',
			soft: 'bg-warning/10 text-warning ring-2 ring-surface-0',
		},
		violet: {
			solid: 'bg-violet-600 text-text-inverted',
			soft: 'bg-violet-100 text-violet-700 ring-2 ring-surface-0',
		},
		indigo: {
			solid: 'bg-indigo-600 text-text-inverted',
			soft: 'bg-indigo-100 text-indigo-700 ring-2 ring-surface-0',
		},
		pink: {
			solid: 'bg-pink-600 text-text-inverted',
			soft: 'bg-pink-100 text-pink-700 ring-2 ring-surface-0',
		},
		sky: {
			solid: 'bg-info text-text-inverted',
			soft: 'bg-info/10 text-info ring-2 ring-surface-0',
		},
		orange: {
			solid: 'bg-orange-600 text-text-inverted',
			soft: 'bg-orange-100 text-orange-600 ring-2 ring-surface-0',
		},
	};

	const initials = $derived(
		name
			.split(' ')
			.map((n) => n[0])
			.join('')
			.toUpperCase()
			.slice(0, 2)
	);

	const showInitials = $derived(!src);
</script>

<div
	class={`rounded-full flex items-center justify-center font-bold shrink-0 ${sizeClasses[size]} ${colorClasses[color][variant]} ${className}`}
	{...restProps}
>
	{#if src}
		<img {src} {alt} class="h-full w-full rounded-full object-cover" loading="lazy" />
	{:else}
		{initials}
	{/if}
</div>
