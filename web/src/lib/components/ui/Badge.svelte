<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';

	interface Props extends HTMLAttributes<HTMLSpanElement> {
		variant?: 'success' | 'warning' | 'error' | 'info' | 'slate';
		size?: 'sm' | 'md';
		dot?: boolean;
		icon?: string;
		class?: string;
		children?: string;
	}

	const {
		variant = 'slate',
		size = 'sm',
		dot = false,
		icon,
		class: className = '',
		children = '',
		...restProps
	}: Props = $props();

	const variantClasses = {
		success: 'bg-emerald-50 text-emerald-700 border-emerald-100',
		warning: 'bg-amber-50 text-amber-700 border-amber-100',
		error: 'bg-rose-50 text-rose-700 border-rose-100',
		info: 'bg-primary-50 text-primary-700 border-primary-100',
		slate: 'bg-slate-50 text-slate-700 border-slate-200',
	};

	const dotColors = {
		success: 'bg-emerald-500',
		warning: 'bg-amber-500',
		error: 'bg-rose-500',
		info: 'bg-primary-500',
		slate: 'bg-slate-400',
	};

	const sizeClasses = {
		sm: 'px-2.5 py-1 text-[11px]',
		md: 'px-3 py-1.5 text-xs',
	};
</script>

<span
	class={\`inline-flex items-center gap-1.5 rounded-full border font-bold uppercase tracking-wide \${variantClasses[variant]} \${sizeClasses[size]} \${className}\`}
	{...restProps}
>
	{#if dot}
		<span class={\`w-1.5 h-1.5 rounded-full \${dotColors[variant]}\`}></span>
	{/if}
	{#if icon}
		<span class="text-xs">{@html icon}</span>
	{/if}
	{children}
</span>
