<script lang="ts">
  interface Settlement {
    from: string;
    to: string;
    amount: number;
    currency: string;
  }

  interface Props {
    settlements: Settlement[];
    class?: string;
    showAmounts?: boolean;
    interactive?: boolean;
    onSelectSettlement?: (settlement: Settlement) => void;
  }

  const {
    settlements,
    class: className = '',
    showAmounts = true,
    interactive = false,
    onSelectSettlement
  }: Props = $props();

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0
    }).format(amount);
  };

  // Group settlements by payer-payee pairs
  const groupedSettlements = $derived(() => {
    const groups = new Map<string, Settlement[]>();

    settlements.forEach(settlement => {
      const key = `${settlement.from}-${settlement.to}`;
      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key)!.push(settlement);
    });

    // Combine settlements with same from-to pair
    const combined: Settlement[] = [];
    groups.forEach((group, key) => {
      if (group.length === 1) {
        combined.push(group[0]);
      } else {
        const total = group.reduce((sum, s) => sum + s.amount, 0);
        combined.push({
          from: group[0].from,
          to: group[0].to,
          amount: total,
          currency: group[0].currency
        });
      }
    });

    return combined.sort((a, b) => b.amount - a.amount);
  });

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarColor = (name: string) => {
    const colors = [
      'bg-red-100 text-red-700',
      'bg-blue-100 text-blue-700',
      'bg-green-100 text-green-700',
      'bg-yellow-100 text-yellow-700',
      'bg-purple-100 text-purple-700',
      'bg-pink-100 text-pink-700',
      'bg-indigo-100 text-indigo-700',
      'bg-teal-100 text-teal-700'
    ];

    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  function handleSelect(settlement: Settlement) {
    if (interactive && onSelectSettlement) {
      onSelectSettlement(settlement);
    }
  }

  function handleKeydown(event: KeyboardEvent, settlement: Settlement) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleSelect(settlement);
    }
  }
</script>

<div class="space-y-4 {className}">
  {#if groupedSettlements().length === 0}
    <div class="text-center py-8 text-text-secondary">
      <svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm">All settlements are complete!</p>
    </div>
  {:else}
    {#each groupedSettlements() as settlement}
      <div
        role={interactive ? 'button' : undefined}
        tabindex={interactive ? 0 : -1}
        class="flex items-center justify-between p-4 bg-surface-50 rounded-lg {interactive ? 'hover:bg-surface-100 cursor-pointer transition-colors' : ''}"
        onclick={() => handleSelect(settlement)}
        onkeydown={(e) => handleKeydown(e, settlement)}
      >
        <!-- Payer -->
        <div class="flex items-center gap-3 flex-1">
          <div class="w-10 h-10 rounded-full {getAvatarColor(settlement.from)} flex items-center justify-center font-semibold text-sm">
            {getInitials(settlement.from)}
          </div>
          <div class="min-w-0">
            <p class="font-medium text-text truncate">{settlement.from}</p>
            <p class="text-xs text-text-secondary">owes</p>
          </div>
        </div>

        <!-- Arrow and Amount -->
        <div class="flex flex-col items-center gap-1 px-4">
          <svg class="w-6 h-6 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
          {#if showAmounts}
            <p class="font-semibold text-primary-600 text-sm">
              {formatCurrency(settlement.amount, settlement.currency)}
            </p>
          {/if}
        </div>

        <!-- Payee -->
        <div class="flex items-center gap-3 flex-1 justify-end">
          <div class="min-w-0 text-right">
            <p class="font-medium text-text truncate">{settlement.to}</p>
            <p class="text-xs text-text-secondary">receives</p>
          </div>
          <div class="w-10 h-10 rounded-full {getAvatarColor(settlement.to)} flex items-center justify-center font-semibold text-sm">
            {getInitials(settlement.to)}
          </div>
        </div>
      </div>
    {/each}
  {/if}
</div>

<!-- Legend -->
{#if showAmounts && settlements.length > 0}
  <div class="mt-6 p-3 bg-surface-100 rounded-lg">
    <p class="text-xs text-text-secondary text-center">
      Total to settle: {formatCurrency(
        settlements.reduce((sum, s) => sum + s.amount, 0),
        settlements[0]?.currency || 'USD'
      )}
    </p>
  </div>
{/if}
