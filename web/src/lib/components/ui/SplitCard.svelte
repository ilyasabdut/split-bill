<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import Badge from './Badge.svelte';
	import Avatar from './Avatar.svelte';

	interface Person {
		name: string;
		color?: 'slate' | 'primary' | 'emerald' | 'rose' | 'amber' | 'violet' | 'indigo' | 'pink' | 'sky' | 'orange';
	}

	interface Props extends HTMLAttributes<HTMLAnchorElement> {
		title: string;
		date: string;
		amount: string;
		icon: string;
		status: 'unpaid' | 'completed' | 'pending';
		people: Person[];
		paidBy?: string;
		paidDate?: string;
		href: string;
		class?: string;
	}

	const {
		title,
		date,
		amount,
		icon,
		status,
		people,
		paidBy,
		paidDate,
		href,
		class: className = '',
		...restProps
	}: Props = $props();

	const statusColors = {
		unpaid: 'bg-amber-400',
		completed: 'bg-emerald-500',
		pending: 'bg-slate-400',
	};

	const iconBgColors = {
		unpaid: 'bg-slate-50 border-slate-100 text-slate-700 hover:bg-primary-50 hover:border-primary-100 hover:text-primary-600',
		completed: 'bg-emerald-50 border-emerald-100 text-emerald-600',
		pending: 'bg-slate-50 border-slate-100 text-slate-700',
	};
</script>

<a
	{href}
	class="group block bg-white border border-slate-200 shadow-sm rounded-2xl p-4 active:scale-[0.99] transition-all relative overflow-hidden {className}"
	{...restProps}
>
	<!-- Status Line Indicator -->
	<div class="absolute left-0 top-0 bottom-0 w-1 {statusColors[status]}"></div>

	<div class="flex items-start gap-4">
		<div
			class="w-12 h-12 rounded-2xl border flex items-center justify-center shrink-0 transition-colors {iconBgColors[status]}"
		>
			{@html icon}
		</div>
		<div class="flex-1 min-w-0">
			<div class="flex items-start justify-between gap-3">
				<div class="min-w-0">
					<h3 class="text-[15px] font-bold text-slate-900 truncate">{title}</h3>
					<p class="text-[12px] text-slate-500 mt-0.5">{date}</p>
				</div>
				<div class="text-right shrink-0">
					<p class="text-[17px] font-bold text-slate-900 leading-none tabular-nums">{amount}</p>
					{#if status === 'unpaid'}
						<Badge variant="warning" dot={true} class="mt-2">Unpaid</Badge>
					{:else if status === 'completed'}
						<div class="mt-1.5 flex flex-col items-end">
							<Badge variant="success" icon="<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'></path><polyline points='22 4 12 14.01 9 11.01'></polyline></svg>"
								>Completed</Badge
							>
							{#if paidDate}
								<span class="text-[10px] text-slate-400 font-medium">Paid on {paidDate}</span>
							{/if}
						</div>
					{:else if status === 'pending'}
						<Badge variant="slate" class="mt-2">Pending</Badge>
					{/if}
				</div>
			</div>

			<div class="mt-3 pt-3 border-t border-slate-50 flex items-center justify-between">
				<div class="flex items-center gap-2 text-slate-500">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="14"
						height="14"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
						<circle cx="9" cy="7" r="4" />
						<path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
					</svg>
					<span class="text-[12px] font-medium">{people.length} people</span>
				</div>
				<div class="flex -space-x-2">
					{#each people.slice(0, 4) as person}
						<Avatar name={person.name} size="sm" color={person.color || 'slate'} variant="soft" />
					{/each}
					{#if people.length > 4}
						<div
							class="w-6 h-6 rounded-full bg-slate-200 ring-2 ring-white flex items-center justify-center text-[9px] font-bold text-slate-700"
						>
							+{people.length - 4}
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</a>
