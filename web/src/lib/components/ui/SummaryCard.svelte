<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';

	interface Props extends HTMLAttributes<HTMLElement> {
		title: string;
		amount: string;
		comparison?: string;
		trend?: {
			value: string;
			up?: boolean;
		};
		icon?: string;
		color?: string;
		class?: string;
	}

	const {
		title,
		amount,
		comparison,
		trend,
		icon,
		color = 'primary',
		class: className = '',
		...restProps
	}: Props = $props();
</script>

<section class="mb-section relative group {className}" {...restProps}>
	<div
		class="absolute inset-0 bg-primary-500 rounded-3xl blur-xl opacity-20 group-hover:opacity-30 transition-opacity"
	></div>
	<div
		class="relative bg-{color}-600 rounded-3xl p-6 text-text-inverted shadow-xl overflow-hidden"
	>
		<!-- Decorative circles -->
		<div
			class="absolute top-0 right-0 w-32 h-32 bg-surface-0/10 rounded-full -mr-10 -mt-10 blur-2xl"
		></div>

		<div class="relative z-10">
			<div class="flex justify-between items-start">
				<p class="text-primary-100 text-label font-medium">{title}</p>
				{#if trend}
					<span
						class="bg-surface-0/30 px-2.5 py-1 rounded-lg text-caption font-semibold text-text-inverted flex items-center gap-1"
					>
						{@html icon || `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>`}
						{trend.value}
					</span>
				{/if}
			</div>
			<h2 class="text-heading font-bold tracking-tight mt-2 tabular-nums">{amount}</h2>
			{#if comparison}
				<p class="text-caption text-primary-200 mt-1 opacity-80">{comparison}</p>
			{/if}
		</div>
	</div>
</section>
