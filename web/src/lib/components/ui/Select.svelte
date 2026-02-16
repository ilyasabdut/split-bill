<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';

	interface Option {
		value: string;
		label: string;
		icon?: string;
		disabled?: boolean;
	}

	interface Props extends HTMLAttributes<HTMLSelectElement> {
		options: Option[];
		value?: string;
		label?: string;
		error?: string;
		placeholder?: string;
		class?: string;
	}

	let {
		options,
		value,
		label,
		error,
		placeholder = 'Select an option',
		class: className = '',
		...restProps
	}: Props = $props();

	let selectedValue = $state(value || '');
</script>

<div class="flex flex-col gap-1.5">
	{#if label}
		<label for={restProps.id} class="block text-sm font-bold text-slate-700">
			{label}
		</label>
	{/if}
	<div class="relative">
		<select
			bind:value={selectedValue}
			class="h-11 w-full appearance-none rounded-2xl border border-slate-200 bg-slate-50 px-4 pr-10 text-sm font-bold text-slate-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all placeholder:text-slate-300"
			class:border-rose-300={error}
			class:focus:ring-rose-500={error}
			class:focus:border-rose-500={error}
			{...restProps}
		>
			<option value="" disabled>{placeholder}</option>
			{#each options as option}
				<option value={option.value} disabled={option.disabled}>
					{option.icon ? `${option.icon} ` : ''}{option.label}
				</option>
			{/each}
		</select>
		<span
			class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 transition-transform"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="16"
				height="16"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<path d="m6 9 6 6 6-6" />
			</svg>
		</span>
	</div>
	{#if error}
		<p class="text-xs font-semibold text-rose-600">{error}</p>
	{/if}
</div>
