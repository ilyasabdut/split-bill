import { writable, derived } from 'svelte/store';

export interface Template {
  id: number;
  name: string;
  config: Record<string, any>; // JSON config
  created_at: string;
}

interface TemplatesState {
  templates: Template[];
  loading: boolean;
  error: string | null;
}

const initialState: TemplatesState = {
  templates: [],
  loading: false,
  error: null
};

function createTemplatesStore() {
  const { subscribe, update, set } = writable(initialState);

  return {
    subscribe,

    templates: derived({ subscribe }, $s => $s.templates),
    isLoading: derived({ subscribe }, $s => $s.loading),
    error: derived({ subscribe }, $s => $s.error),

    setTemplates: (templates: Template[]) => update(s => ({ ...s, templates, loading: false })),

    addTemplate: (template: Template) => update(s => ({
      ...s,
      templates: [...s.templates, template]
    })),

    removeTemplate: (id: number) => update(s => ({
      ...s,
      templates: s.templates.filter(t => t.id !== id)
    })),

    setLoading: (loading: boolean) => update(s => ({ ...s, loading })),

    setError: (error: string | null) => update(s => ({ ...s, error, loading: false })),

    reset: () => set(initialState),

    /** Load templates from API */
    async loadTemplates() {
      update(s => ({ ...s, loading: true }));
      try {
        const response = await fetch('/api/templates');
        if (!response.ok) throw new Error('Failed to load templates');

        const data = await response.json();
        update(s => ({
          ...s,
          templates: data || [],
          loading: false
        }));
      } catch (err) {
        const error = err instanceof Error ? err.message : 'Unknown error';
        update(s => ({ ...s, error, loading: false }));
      }
    },
  }
}

export const templatesStore = createTemplatesStore();
