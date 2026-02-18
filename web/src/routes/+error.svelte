<script lang="ts">
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import { goto } from '$app/navigation';

  interface Props {
    data: unknown;
    form: unknown;
    status: number;
    error: Error & { message: string };
  }

  const { status, error }: Props = $props();

  function goHome() {
    goto('/');
  }

  function goBack() {
    window.history.back();
  }
</script>

<svelte:head>
  <title>{status === 404 ? 'Page Not Found' : 'Error'} - Split Bill</title>
</svelte:head>

<div class="min-h-screen bg-slate-50 flex items-center justify-center px-4">
  <Card class="max-w-md w-full">
    <div class="text-center py-12">
      {#if status === 404}
        <div class="text-8xl mb-6" aria-hidden="true">🔍</div>
        <h1 class="text-3xl font-bold text-slate-900 mb-2">Page Not Found</h1>
        <p class="text-slate-600 mb-8">Sorry, we couldn't find the page you're looking for. It might have been moved or deleted.</p>
        <div class="space-y-3">
          <Button onclick={goHome} variant="primary" class="w-full">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="m3 9 9-7 7"/><path d="M9 21V9"/></svg>
            Go Home
          </Button>
          <Button onclick={goBack} variant="secondary" class="w-full">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="m15 18-6-6 6-6"/></svg>
            Go Back
          </Button>
        </div>
      {:else}
        <div class="text-6xl mb-4" aria-hidden="true">⚠️</div>
        <h1 class="text-2xl font-bold mb-2">Error {status}</h1>
        <p class="text-slate-600 mb-8">{error.message || 'An unexpected error occurred.'}</p>
        <div class="space-y-3">
          <Button onclick={goBack} variant="primary" class="w-full">Go Back</Button>
          <Button onclick={goHome} variant="secondary" class="w-full">Go Home</Button>
        </div>
      {/if}
    </div>
  </Card>
</div>
