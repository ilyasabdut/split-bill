<script lang="ts">
  import type { Group } from '$lib/stores/groups';
  import Button from './ui/Button.svelte';
  import Card from './ui/Card.svelte';
  import { cn } from '$lib/utils';

  interface Props {
    group: Group;
    onSelect?: (group: Group) => void;
    onEdit?: (group: Group) => void;
    onDelete?: (group: Group) => void;
    class?: string;
    showActions?: boolean;
    isSelected?: boolean;
  }

  const {
    group,
    onSelect,
    onEdit,
    onDelete,
    class: className = '',
    showActions = true,
    isSelected = false
  }: Props = $props();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };
</script>

<Card
  padding="md"
  class={cn('hover:shadow-md transition-shadow cursor-pointer', className, isSelected && 'ring-2 ring-primary-500')}
  onclick={() => onSelect?.(group)}
>
  <!-- Header -->
  <div class="flex items-start justify-between mb-4">
    <div class="flex-1">
      <h3 class="font-semibold text-text text-lg mb-1 text-balance">{group.name}</h3>
      <p class="text-text-secondary text-sm">
        Created {formatDate(group.created_at)}
      </p>
    </div>

    {#if group.members.length > 0}
      <div class="flex -space-x-2">
        {#each group.members.slice(0, 3) as member}
          {#if member.avatar_url}
            <img
              src={member.avatar_url}
              alt={member.name}
              class="size-8 rounded-full border-2 border-surface-0 object-cover"
            />
          {:else}
            <div
              class="size-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-semibold border-2 border-surface-0"
            >
              {getInitials(member.name)}
            </div>
          {/if}
        {/each}
        {#if group.members.length > 3}
          <div
            class="size-8 rounded-full bg-surface-200 text-text-secondary flex items-center justify-center text-xs font-semibold border-2 border-surface-0"
          >
            <span class="tabular-nums">+{group.members.length - 3}</span>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Stats -->
  <div class="grid grid-cols-2 gap-3 mb-4">
    <div class="bg-surface-50 rounded-lg p-3">
      <p class="text-text-secondary text-xs mb-1">Members</p>
      <p class="font-semibold text-text text-lg tabular-nums">{group.members.length}</p>
    </div>
    <div class="bg-surface-50 rounded-lg p-3">
      <p class="text-text-secondary text-xs mb-1">Splits</p>
      <p class="font-semibold text-text text-lg tabular-nums">0</p>
    </div>
  </div>

  <!-- Member List -->
  {#if group.members.length > 0}
    <div class="mb-4">
      <p class="text-text-secondary text-xs mb-2">Members:</p>
      <div class="flex flex-wrap gap-2">
        {#each group.members as member}
          <span class="px-2 py-1 bg-surface-100 text-text text-xs rounded-full">
            {member.name}
          </span>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Actions -->
  {#if showActions && (onEdit || onDelete)}
    <div class="flex gap-2 pt-3 border-t border-surface-200">
      {#if onSelect}
        <Button variant="primary" size="sm" onclick={() => onSelect(group)}>
          Select Group
        </Button>
      {/if}

      <div class="flex gap-1 ml-auto">
        {#if onEdit}
          <Button variant="ghost" size="sm" onclick={(e) => {
            e.stopPropagation();
            onEdit(group);
          }} ariaLabel="Edit group">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit
          </Button>
        {/if}

        {#if onDelete}
          <Button variant="ghost" size="sm" onclick={(e) => {
            e.stopPropagation();
            onDelete(group);
          }} ariaLabel="Delete group">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </Button>
        {/if}
      </div>
    </div>
  {/if}
</Card>
