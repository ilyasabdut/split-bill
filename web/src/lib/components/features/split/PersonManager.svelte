<script lang="ts">
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { cn } from '$lib/utils';

  interface Props {
    people: string[];
    onUpdate: (people: string[]) => void;
  }

  const { people, onUpdate }: Props = $props();

  let newPersonName = $state('');

  function addPerson() {
    if (newPersonName.trim()) {
      onUpdate([...people, newPersonName.trim()]);
      newPersonName = '';
    }
  }

  function removePerson(index: number) {
    const updated = people.filter((_, i) => i !== index);
    onUpdate(updated);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      addPerson();
    }
  }
</script>

<Card>
  <div class="space-y-4">
    <h2 class="font-semibold text-balance">People (<span class="tabular-nums">{people.length}</span>)</h2>

    <!-- Add Person Input -->
    <div class="flex gap-2">
      <Input
        bind:value={newPersonName}
        placeholder="Add person..."
        onkeydown={handleKeydown}
        class="flex-1"
      />
      <Button variant="primary" onclick={addPerson} disabled={!newPersonName.trim()} ariaLabel="Add person">
        Add
      </Button>
    </div>

    <!-- People List -->
    <div class="space-y-2">
      {#each people as person, index}
        <div class="flex items-center gap-2 p-2 bg-surface-50 rounded-lg">
          <span class="flex-1 font-medium text-balance">{person}</span>
          <button
            onclick={() => removePerson(index)}
            class="text-red-600 hover:text-red-700 p-2 min-h-[44px]"
            aria-label="Remove {person}"
          >
            ✕
          </button>
        </div>
      {/each}
    </div>
  </div>
</Card>
