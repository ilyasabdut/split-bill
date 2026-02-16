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
		slate: 'bg-slate-50 border-slate-200',
		primary: 'bg-primary-50 border-primary-500/15',
		emerald: 'bg-emerald-50 border-emerald-500/15',
		amber: 'bg-amber-50 border-amber-500/15',
		rose: 'bg-rose-50 border-rose-500/15',
	};

	const iconClasses = {
		slate: 'bg-slate-50 text-slate-600',
		primary: 'bg-primary-100 text-primary-600',
		emerald: 'bg-emerald-100 text-emerald-600',
		amber: 'bg-amber-100 text-amber-600',
		rose: 'bg-rose-100 text-rose-600',
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
		<p class="text-[11px] uppercase tracking-wider text-slate-500 font-bold leading-tight">{label}</p>
		<p class="text-[15px] font-bold text-slate-900 tabular-nums">{value}</p>
		{#if trend}
			<p
				class="text-[10px] font-medium {trend.up ? 'text-emerald-600' : 'text-rose-600'}"
			>
				{trend.up ? '+' : '-'}{trend.value}
			</p>
		{/if}
	</div>
</div>
