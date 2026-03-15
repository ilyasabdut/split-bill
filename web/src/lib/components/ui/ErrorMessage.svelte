<script lang="ts">
	interface Props {
		title?: string;
		message: string;
		onRetry?: () => void;
		onDismiss?: () => void;
		variant?: 'card' | 'inline';
	}

	let {
		title = 'Something went wrong',
		message,
		onRetry,
		onDismiss,
		variant = 'card'
	}: Props = $props();
</script>

{#if variant === 'inline'}
	<div class="flex items-start gap-3 p-4 rounded-2xl bg-error/10 border border-error/20">
		<div class="h-10 w-10 rounded-xl bg-error/20 text-error flex items-center justify-center shrink-0">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="20"
				height="20"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="text-error"
			>
				<circle cx="12" cy="12" r="10" />
				<line x1="15" y1="9" x2="9" y2="15" />
				<line x1="9" y1="9" x2="15" y2="15" />
			</svg>
		</div>

		<div class="min-w-0 flex-1">
			{#if title}
				<p class="text-label font-bold text-text-primary">{title}</p>
			{/if}
			<p class="text-caption text-text-secondary">{message}</p>

			{#if onRetry}
				<button
					type="button"
					onclick={onRetry}
					class="mt-2 text-caption font-semibold text-primary-600 hover:text-primary-700 transition-colors"
				>
					Try again
				</button>
			{/if}
		</div>

		{#if onDismiss}
			<button
				type="button"
				onclick={onDismiss}
				class="h-8 w-8 rounded-lg text-text-tertiary hover:text-text-primary hover:bg-surface-100 transition-colors flex items-center justify-center"
				aria-label="Dismiss error"
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
					<path d="M18 6 6 18" />
					<path d="m6 6 12 12" />
				</svg>
			</button>
		{/if}
	</div>
{:else}
	<div class="flex flex-col items-center justify-center px-6 py-12 text-center">
		<div class="h-20 w-20 rounded-3xl bg-error/10 text-error flex items-center justify-center mb-4">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="32"
				height="32"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<circle cx="12" cy="12" r="10" />
				<line x1="15" y1="9" x2="9" y2="15" />
				<line x1="9" y1="9" x2="15" y2="15" />
			</svg>
		</div>

		<h3 class="text-section font-bold text-text-primary mb-2">{title}</h3>
		<p class="text-body text-text-secondary max-w-sm mb-6">{message}</p>

		<div class="flex items-center gap-3">
			{#if onRetry}
				<button
					type="button"
					onclick={onRetry}
					class="h-12 px-6 rounded-2xl bg-primary-500 text-text-inverted font-semibold shadow-md hover:bg-primary-600 active:scale-95 transition-all"
				>
					Try Again
				</button>
			{/if}

			{#if onDismiss}
				<button
					type="button"
					onclick={onDismiss}
					class="h-12 px-6 rounded-2xl bg-surface-0 text-text-primary font-semibold shadow-sm border border-surface-200 hover:bg-surface-50 active:scale-95 transition-all"
				>
					Go Back
				</button>
			{/if}
		</div>
	</div>
{/if}
