<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';

	interface Props extends Omit<HTMLAttributes<HTMLSpanElement>, 'children'> {
		variant?: 'success' | 'warning' | 'error' | 'info' | 'slate';
		size?: 'sm' | 'md';
		dot?: boolean;
		icon?: string;
		class?: string;
		children?: Snippet;
	}

	const {
		variant = 'slate',
		size = 'sm',
		dot = false,
		icon,
		class: className = '',
		children,
		...restProps
	}: Props = $props();

	const variantClasses = {
		success: 'bg-success/10 text-success border-success/20',
		warning: 'bg-warning/10 text-warning border-warning/20',
		error: 'bg-error/10 text-error border-error/20',
		info: 'bg-info/10 text-info border-info/20',
		slate: 'bg-surface-100 text-text-secondary border-surface-200',
	};

	const dotColors = {
		success: 'bg-success',
		warning: 'bg-warning',
		error: 'bg-error',
		info: 'bg-info',
		slate: 'bg-text-tertiary',
	};

	const sizeClasses = {
		sm: 'px-2.5 py-1 text-[11px]',
		md: 'px-3 py-1.5 text-xs',
	};
</script>

<span
	class="inline-flex items-center gap-1.5 rounded-full border font-bold uppercase tracking-wide max-w-full {variantClasses[variant]} {sizeClasses[size]} {className}"
	{...restProps}
>
	{#if dot}
		<span class="w-1.5 h-1.5 rounded-full shrink-0 {dotColors[variant]}"></span>
	{/if}
	{#if icon}
		<span class="text-xs shrink-0">{@html icon}</span>
	{/if}
	{#if children}
		<span class="truncate">{@render children()}</span>
	{/if}
</span>
