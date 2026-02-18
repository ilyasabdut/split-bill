<script lang="ts">
  interface Props {
    count?: number;
    height?: string;
  }

  let { count = 3, height = 'h-24' }: Props = $props();
</script>

<div class="space-y-4">
  {#each Array(count) as _, i}
    <div class="bg-white border border-slate-200 rounded-2xl p-4 animate-pulse">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 rounded-2xl bg-slate-200"></div>
        <div class="flex-1 space-y-3">
          <div class="h-4 bg-slate-200 rounded w-3/4"></div>
          <div class="h-3 bg-slate-200 rounded w-1/2"></div>
          <div class="h-3 bg-slate-200 rounded w-1/4"></div>
        </div>
      </div>
    </div>
  {/each}
</div>