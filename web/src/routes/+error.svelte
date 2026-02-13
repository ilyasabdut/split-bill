<script lang="ts">
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';

  interface Props {
    data: unknown;
    form: unknown;
    status: number;
    error: Error & { message: string };
  }

  const { status, error }: Props = $props();
</script>

<svelte:head>
  <title>Error {status} - Split Bill</title>
</svelte:head>

<Card>
  <div class="text-center py-8">
    <div class="text-6xl mb-4" aria-hidden="true">⚠️</div>
    <h1 class="text-2xl font-bold mb-2">Error {status}</h1>
    <p class="text-text-secondary mb-6">{error.message}</p>
    <Button onclick={() => window.history.back()}>Go Back</Button>
  </div>
</Card>
