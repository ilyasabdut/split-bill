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
			solid: 'bg-slate-600 text-white',
			soft: 'bg-slate-200 text-slate-700 ring-2 ring-white',
		},
		primary: {
			solid: 'bg-primary-600 text-white',
			soft: 'bg-primary-200 text-primary-800 ring-2 ring-white',
		},
		emerald: {
			solid: 'bg-emerald-600 text-white',
			soft: 'bg-emerald-200 text-emerald-800 ring-2 ring-white',
		},
		rose: {
			solid: 'bg-rose-600 text-white',
			soft: 'bg-rose-200 text-rose-900 ring-2 ring-white',
		},
		amber: {
			solid: 'bg-amber-600 text-white',
			soft: 'bg-amber-200 text-amber-900 ring-2 ring-white',
		},
		violet: {
			solid: 'bg-violet-600 text-white',
			soft: 'bg-violet-200 text-violet-700 ring-2 ring-white',
		},
		indigo: {
			solid: 'bg-indigo-600 text-white',
			soft: 'bg-indigo-200 text-indigo-700 ring-2 ring-white',
		},
		pink: {
			solid: 'bg-pink-600 text-white',
			soft: 'bg-pink-200 text-pink-700 ring-2 ring-white',
		},
		sky: {
			solid: 'bg-sky-600 text-white',
			soft: 'bg-sky-200 text-sky-800 ring-2 ring-white',
		},
		orange: {
			solid: 'bg-orange-600 text-white',
			soft: 'bg-orange-200 text-orange-500 ring-2 ring-white',
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
	class={\`rounded-full flex items-center justify-center font-bold shrink-0 \${sizeClasses[size]} \${colorClasses[color][variant]} \${className}\`}
	{...restProps}
>
	{#if src}
		<img {src} {alt} class="h-full w-full rounded-full object-cover" />
	{:else}
		{initials}
	{/if}
</div>
