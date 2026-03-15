<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';

	interface Props extends HTMLAttributes<HTMLDivElement> {
		label: string;
		value: string;
		icon?: string;
		trend?: {
			value: string;
			up?: boolean;
		};
		variant?: 'slate' | 'primary' | 'emerald' | 'amber' | 'rose';
		class?: string;
	}

	const {
		label,
		value,
		icon,
		trend,
		variant = 'slate',
		class: className = '',
		...restProps
	}: Props = $props();

	const variantClasses = {
		slate: 'bg-surface-50 border-surface-200',
		primary: 'bg-primary-50 border-primary-500/15',
		emerald: 'bg-success/10 border-success/20',
		amber: 'bg-warning/10 border-warning/20',
		rose: 'bg-error/10 border-error/20',
	};

	const iconClasses = {
		slate: 'bg-surface-100 text-text-secondary',
		primary: 'bg-primary-100 text-primary-600',
		emerald: 'bg-success/10 text-success',
		amber: 'bg-warning/10 text-warning',
		rose: 'bg-error/10 text-error',
	};
</script>

<div
	class="border shadow-sm rounded-2xl pl-3 pr-4 py-2.5 flex items-center gap-3 {variantClasses[variant]} {className}"
	{...restProps}
>
	{#if icon}
		<span class="w-10 h-10 rounded-xl flex items-center justify-center {iconClasses[variant]}">
			{@html icon}
		</span>
	{/if}
	<div>
		<p class="text-caption uppercase tracking-wider text-text-tertiary font-bold leading-tight">{label}</p>
		<p class="text-label font-bold text-text-primary tabular-nums">{value}</p>
		{#if trend}
			<p
				class="text-caption font-medium {trend.up ? 'text-success' : 'text-error'}"
			>
				{trend.up ? '+' : '-'}{trend.value}
			</p>
		{/if}
	</div>
</div>
