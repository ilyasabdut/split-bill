import { writable, derived } from 'svelte/store';

export interface GroupMember {
  id: number;
  name: string;
  avatar_url?: string;
}

export interface Group {
  id: number;
  name: string;
  members: GroupMember[];
  created_at: string;
}

interface GroupsState {
  groups: Group[];
  currentGroupId: number | null;
  loading: boolean;
  error: string | null;
}

const initialState: GroupsState = {
  groups: [],
  currentGroupId: null,
  loading: false,
  error: null
};

function createGroupsStore() {
  const { subscribe, update, set } = writable(initialState);

  return {
    subscribe,

    groups: derived({ subscribe }, $s => $s.groups),
    currentGroup: derived({ subscribe }, $s => $s.groups.find(g => g.id === $s.currentGroupId) || null),
    isLoading: derived({ subscribe }, $s => $s.loading),
    error: derived({ subscribe }, $s => $s.error),

    setGroups: (groups: Group[]) => update(s => ({ ...s, groups, loading: false })),

    setCurrentGroup: (id: number | null) => update(s => ({ ...s, currentGroupId: id })),

    addGroup: (group: Group) => update(s => ({
      ...s,
      groups: [...s.groups, group]
    })),

    updateGroup: (updatedGroup: Group) => update(s => ({
      ...s,
      groups: s.groups.map(g => g.id === updatedGroup.id ? updatedGroup : g)
    })),

    removeGroup: (id: number) => update(s => ({
      ...s,
      groups: s.groups.filter(g => g.id !== id),
      currentGroupId: s.currentGroupId === id ? null : s.currentGroupId
    })),

    setLoading: (loading: boolean) => update(s => ({ ...s, loading })),

    setError: (error: string | null) => update(s => ({ ...s, error, loading: false })),

    reset: () => set(initialState),

    /** Load groups from API */
    async loadGroups() {
      update(s => ({ ...s, loading: true }));
      try {
        const response = await fetch('/api/groups');
        if (!response.ok) throw new Error('Failed to load groups');

        const data = await response.json();
        update(s => ({
          ...s,
          groups: data || [],
          loading: false
        }));
      } catch (err) {
        const error = err instanceof Error ? err.message : 'Unknown error';
        update(s => ({ ...s, error, loading: false }));
      }
    },
  }
}

export const groupsStore = createGroupsStore();
