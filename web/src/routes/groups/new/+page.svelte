<script lang="ts">
	import { goto } from '$app/navigation';

	interface Member {
		id: string;
		name: string;
		email: string;
		color: 'indigo' | 'emerald' | 'rose' | 'amber' | 'sky' | 'violet' | 'slate';
	}

	let groupName = $state('');
	let groupDescription = $state('');
	let members = $state<Member[]>([
		{ id: '1', name: 'You', email: '', color: 'indigo' },
	]);
	let isCreating = $state(false);
	let errors = $state<Record<string, string>>({});

	const colors: Array<'indigo' | 'emerald' | 'rose' | 'amber' | 'sky' | 'violet' | 'slate'> =
		['indigo', 'emerald', 'rose', 'amber', 'sky', 'violet', 'slate'];

	function addMember() {
		const newMember: Member = {
			id: Date.now().toString(),
			name: '',
			email: '',
			color: colors[members.length % colors.length]
		};
		members = [...members, newMember];
	}

	function removeMember(id: string) {
		if (members.length > 1) {
			members = members.filter(m => m.id !== id);
		}
	}

	function updateMember(id: string, field: 'name' | 'email', value: string) {
		members = members.map(m =>
			m.id === id ? { ...m, [field]: value } : m
		);
	}

	function validateForm(): boolean {
		errors = {};
		let isValid = true;

		if (!groupName.trim()) {
			errors.groupName = 'Group name is required';
			isValid = false;
		}

		if (members.length < 2) {
			errors.members = 'At least 2 members are required';
			isValid = false;
		}

		members.forEach((member, index) => {
			if (!member.name.trim()) {
				errors[`member-${index}-name`] = 'Name is required';
				isValid = false;
			}
			if (member.email && !isValidEmail(member.email)) {
				errors[`member-${index}-email`] = 'Invalid email format';
				isValid = false;
			}
		});

		return isValid;
	}

	function isValidEmail(email: string): boolean {
		return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
	}

	async function handleCreateGroup() {
		if (!validateForm()) return;

		isCreating = true;

		await new Promise(resolve => setTimeout(resolve, 1000));

		const groupId = 'group-' + Date.now();

		goto(`/groups/${groupId}`);
	}
</script>

<svelte:head>
	<title>Create Group - Split Bill</title>
	<meta name="color-scheme" content="light" />
</svelte:head>

<div class="w-full min-h-dvh flex flex-col bg-surface-50 text-text-primary font-sans">
	<!-- Decorative background -->
	<div class="pointer-events-none absolute inset-0 overflow-hidden -z-10">
		<div class="absolute -top-24 -right-20 h-72 w-72 rounded-full bg-violet-500/15 blur-2xl"></div>
		<div class="absolute top-28 -left-24 h-72 w-72 rounded-full bg-emerald-400/10 blur-2xl"></div>
	</div>

	<!-- Header -->
	<header class="shrink-0 px-4" style="padding-top: max(env(safe-area-inset-top), 3rem);">
		<div class="flex items-center justify-between max-w-lg mx-auto">
			<a href="/" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-2xl bg-surface-0 shadow-md border border-surface-200 active:scale-95 transition-transform hover:bg-surface-50" aria-label="Go back home">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="m15 18-6-6 6-6"/><path d="M18 6 6 18"/></svg>
			</a>
			<div class="text-center">
				<div class="text-xs font-bold text-text-secondary uppercase tracking-wider">New Group</div>
				<h1 class="text-lg font-black tracking-tight text-text-primary">Create Group</h1>
			</div>
			<div class="h-11 w-11"></div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="flex-1 overflow-y-auto px-4 py-4 space-y-5 max-w-lg mx-auto w-full" style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 2rem);">

		<!-- Group Info Card -->
		<section class="rounded-3xl bg-surface-0 shadow-md border border-surface-200 overflow-hidden">
			<div class="px-5 py-3 border-b border-surface-100 bg-surface-50/50">
				<div class="flex items-center gap-2">
					<div class="h-8 w-8 rounded-xl bg-violet-100 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-violet-600"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
					</div>
					<h2 class="text-sm font-bold text-text-primary">Group Details</h2>
				</div>
			</div>

			<div class="p-5 space-y-4">
				<!-- Group Name -->
				<div>
					<label for="group-name" class="block text-sm font-bold text-text-secondary mb-2">Group Name *</label>
					<input
						id="group-name"
						type="text"
						bind:value={groupName}
						placeholder="e.g., Roommates, Trip to Bali"
						class="h-12 w-full rounded-2xl border border-surface-200 bg-surface-50 px-4 text-base font-medium text-text-primary shadow-sm focus-visible:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-all placeholder:text-text-tertiary {errors.groupName ? 'border-red-500' : ''}"
					/>
					{#if errors.groupName}
						<p class="mt-1 text-xs text-red-600">{errors.groupName}</p>
					{/if}
				</div>

				<!-- Description -->
				<div>
					<label for="group-desc" class="block text-sm font-bold text-text-secondary mb-2">Description <span class="text-text-tertiary font-normal">(optional)</span></label>
					<textarea
						id="group-desc"
						bind:value={groupDescription}
						placeholder="What's this group for?"
						rows="2"
						class="w-full rounded-2xl border border-surface-200 bg-surface-50 px-4 py-3 text-base font-medium text-text-primary shadow-sm focus-visible:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-all placeholder:text-text-tertiary resize-none"
					></textarea>
				</div>
			</div>
		</section>

		<!-- Members Card -->
		<section class="rounded-3xl bg-surface-0 shadow-md border border-surface-200 overflow-hidden">
			<div class="px-5 py-3 border-b border-surface-100 bg-surface-50/50 flex items-center justify-between">
				<div class="flex items-center gap-2">
					<div class="h-8 w-8 rounded-xl bg-emerald-100 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-600"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
					</div>
					<h2 class="text-sm font-bold text-text-primary">Members</h2>
				</div>
				<span class="bg-surface-100 text-text-secondary px-2.5 py-0.5 rounded-lg text-xs font-bold">{members.length}</span>
			</div>

			<div class="p-5 space-y-4">
				{#each members as member, index (member.id)}
					<div class="bg-surface-50 rounded-2xl p-4 border border-surface-200 relative">
						{#if index > 0}
							<button
								type="button"
								onclick={() => removeMember(member.id)}
								class="absolute right-2 top-2 h-8 w-8 rounded-lg text-text-tertiary hover:bg-rose-50 hover:text-rose-500 transition-colors flex items-center justify-center"
								aria-label="Remove member"
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
							</button>
						{/if}

						<div class="flex items-start gap-3">
							<!-- Avatar -->
							<div class="h-11 w-11 rounded-full bg-{member.color}-200 border-2 border-surface-0 flex items-center justify-center text-sm font-bold text-{member.color}-700 shrink-0 shadow-sm">
								{member.name ? member.name[0].toUpperCase() : '?'}
							</div>

							<div class="flex-1 space-y-3">
								<!-- Name Input -->
								<div>
									<label for="member-{index}-name" class="block text-xs font-semibold text-text-secondary mb-1">Name *</label>
									<input
										id="member-{index}-name"
										type="text"
										value={member.name}
										oninput={(e) => updateMember(member.id, 'name', e.currentTarget.value)}
										placeholder="Enter name"
										class="h-10 w-full rounded-xl border border-surface-200 bg-surface-0 px-3 text-sm font-medium text-text-primary focus-visible:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-all placeholder:text-text-tertiary {errors[`member-${index}-name`] ? 'border-red-500' : ''}"
									/>
									{#if errors[`member-${index}-name`]}
										<p class="mt-1 text-xs text-red-600">{errors[`member-${index}-name`]}</p>
									{/if}
								</div>

								<!-- Email Input -->
								<div>
									<label for="member-{index}-email" class="block text-xs font-semibold text-text-secondary mb-1">Email <span class="text-text-tertiary font-normal">(optional)</span></label>
									<input
										id="member-{index}-email"
										type="email"
										value={member.email}
										oninput={(e) => updateMember(member.id, 'email', e.currentTarget.value)}
										placeholder="email@example.com"
										class="h-10 w-full rounded-xl border border-surface-200 bg-surface-0 px-3 text-sm font-medium text-text-primary focus-visible:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-all placeholder:text-text-tertiary {errors[`member-${index}-email`] ? 'border-red-500' : ''}"
									/>
									{#if errors[`member-${index}-email`]}
										<p class="mt-1 text-xs text-red-600">{errors[`member-${index}-email`]}</p>
									{/if}
								</div>
							</div>
						</div>
					</div>
				{/each}

				{#if errors.members}
					<p class="text-xs text-red-600 text-center">{errors.members}</p>
				{/if}

				<!-- Add Member Button -->
				<button
					type="button"
					onclick={addMember}
					class="w-full h-12 rounded-2xl border-2 border-dashed border-surface-300 text-text-secondary font-bold text-sm flex items-center justify-center gap-2 hover:border-violet-300 hover:text-violet-600 hover:bg-violet-50 transition-all active:scale-[0.99]"
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
					Add Member
				</button>
			</div>
		</section>

		<!-- Quick Add Contacts -->
		<section class="rounded-3xl bg-violet-50 border border-violet-200 p-4">
			<div class="flex items-start gap-3">
				<div class="h-10 w-10 rounded-2xl bg-surface-0 border border-violet-200 flex items-center justify-center shadow-sm">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-violet-600"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
				</div>
				<div class="min-w-0 flex-1">
					<p class="text-sm font-bold text-text-primary">Quick Add</p>
					<p class="text-xs text-text-secondary mt-0.5">Import contacts from your device for faster setup.</p>
					<button type="button" class="mt-2 h-9 px-4 rounded-xl bg-violet-500 text-white text-xs font-bold shadow-md active:scale-95 transition-transform">
						Import Contacts
					</button>
				</div>
			</div>
		</section>

		<!-- Action Buttons -->
		<section class="pt-2 space-y-3">
			<button
				type="button"
				onclick={handleCreateGroup}
				disabled={isCreating}
				class="w-full h-14 rounded-2xl bg-violet-500 text-white font-extrabold text-lg shadow-lg shadow-violet-500/30 flex items-center justify-center gap-2 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed"
			>
				{#if isCreating}
					<svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					Creating...
				{:else}
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
					Create Group
				{/if}
			</button>

			<a
				href="/"
				class="w-full h-12 rounded-2xl bg-surface-0 border border-surface-200 text-text-secondary font-bold text-sm shadow-sm flex items-center justify-center gap-2 active:scale-[0.98] transition-all hover:bg-surface-50"
			>
				Cancel
			</a>
		</section>
	</main>
</div>
