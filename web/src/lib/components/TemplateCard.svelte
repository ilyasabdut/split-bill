<script lang="ts">
  import type { Snippet } from 'svelte';
  import Button from './ui/Button.svelte';

  interface Template {
    id: string;
    name: string;
    description?: string;
    item_count: number;
    total_amount: number;
    currency: string;
    created_at: string;
    tags?: string[];
    is_favorite?: boolean;
  }

  interface Props {
    template: Template;
    onUse?: (template: Template) => void;
    onEdit?: (template: Template) => void;
    onDelete?: (template: Template) => void;
    onToggleFavorite?: (template: Template) => void;
    class?: string;
    showActions?: boolean;
  }

  const {
    template,
    onUse,
    onEdit,
    onDelete,
    onToggleFavorite,
    class: className = '',
    showActions = true
  }: Props = $props();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0
    }).format(amount);
  };
</script>

<div class="bg-surface-100 rounded-xl border border-surface-200 p-4 hover:shadow-md transition-shadow {className}">
  <!-- Header -->
  <div class="flex items-start justify-between mb-3">
    <div class="flex-1">
      <h3 class="font-semibold text-text text-lg mb-1">{template.name}</h3>
      {#if template.description}
        <p class="text-text-secondary text-sm line-clamp-2">{template.description}</p>
      {/if}
    </div>

    {#if onToggleFavorite}
      <button
        onclick={() => onToggleFavorite(template)}
        class="p-2 rounded-lg hover:bg-surface-200 transition-colors"
        aria-label={template.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
      >
        <svg
          class="w-5 h-5 {template.is_favorite ? 'text-yellow-500 fill-current' : 'text-text-secondary'}"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
          />
        </svg>
      </button>
    {/if}
  </div>

  <!-- Stats -->
  <div class="grid grid-cols-2 gap-3 mb-3">
    <div class="bg-surface-50 rounded-lg p-3">
      <p class="text-text-secondary text-xs mb-1">Items</p>
      <p class="font-semibold text-text">{template.item_count}</p>
    </div>
    <div class="bg-surface-50 rounded-lg p-3">
      <p class="text-text-secondary text-xs mb-1">Total Amount</p>
      <p class="font-semibold text-text">{formatCurrency(template.total_amount, template.currency)}</p>
    </div>
  </div>

  <!-- Tags -->
  {#if template.tags && template.tags.length > 0}
    <div class="flex flex-wrap gap-2 mb-3">
      {#each template.tags as tag}
        <span class="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
          {tag}
        </span>
      {/each}
    </div>
  {/if}

  <!-- Footer -->
  <div class="flex items-center justify-between text-xs text-text-secondary mb-3">
    <span>Created {formatDate(template.created_at)}</span>
    <span class="uppercase">{template.currency}</span>
  </div>

  <!-- Actions -->
  {#if showActions && (onUse || onEdit || onDelete)}
    <div class="flex gap-2">
      {#if onUse}
        <Button variant="primary" size="sm" onclick={() => onUse(template)}>
          Use Template
        </Button>
      {/if}

      <div class="flex gap-1 ml-auto">
        {#if onEdit}
          <Button variant="ghost" size="sm" onclick={() => onEdit(template)}>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit
          </Button>
        {/if}

        {#if onDelete}
          <Button variant="ghost" size="sm" onclick={() => onDelete(template)}>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </Button>
        {/if}
      </div>
    </div>
  {/if}
</div>
