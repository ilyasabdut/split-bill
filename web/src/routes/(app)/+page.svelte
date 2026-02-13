<script lang="ts">
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
</script>

<svelte:head>
  <title>Split Bill - Home</title>
</svelte:head>

<div class="space-y-4">
  <Card>
    <h2 class="text-lg font-semibold mb-2">Welcome to Split Bill</h2>
    <p class="text-text-secondary">Split bills easily with friends using your phone.</p>
  </Card>

  <div class="grid grid-cols-2 gap-4">
    <a href="/receipt">
      <Card class="text-center hover:bg-surface-50 transition-colors cursor-pointer">
        <div class="text-4xl mb-2" aria-hidden="true">📸</div>
        <h3 class="font-semibold">Upload Receipt</h3>
        <p class="text-sm text-text-secondary">Scan or upload</p>
      </Card>
    </a>

    <a href="/split">
      <Card class="text-center hover:bg-surface-50 transition-colors cursor-pointer">
        <div class="text-4xl mb-2" aria-hidden="true">💰</div>
        <h3 class="font-semibold">New Split</h3>
        <p class="text-sm text-text-secondary">Create a split</p>
      </Card>
    </a>
  </div>
</div>
