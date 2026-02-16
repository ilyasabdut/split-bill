import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { templatesStore } from '../templates';

describe('templatesStore', () => {
  beforeEach(() => {
    templatesStore.reset();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = get(templatesStore);
      expect(state).toEqual({
        templates: [],
        loading: false,
        error: null
      });
 });
  });

  describe('setTemplates', () => {
    it('should set templates data', () => {
      const templatesData = [
        { id: 1, name: 'Template 1', config: {}, created_at: '2024-01-01' },
        { id: 2, name: 'Template 2', config: {}, created_at: '2024-01-02' }
      ];

      templatesStore.setTemplates(templatesData);

      const state = get(templatesStore);
      expect(state.templates).toEqual(templatesData);
      expect(state.loading).toBe(false);
    });

    it('should replace existing templates', () => {
      const templates1 = [{ id: 1, name: 'Template 1', config: {}, created_at: '2024-01-01' }];
      const templates2 = [{ id: 2, name: 'Template 2', config: {}, created_at: '2024-01-02' }];

      templatesStore.setTemplates(templates1);
      expect(get(templatesStore).templates).toEqual(templates1);

      templatesStore.setTemplates(templates2);
      expect(get(templatesStore).templates).toEqual(templates2);
    });
  });

  describe('addTemplate', () => {
    it('should add a template', () => {
      const newTemplate = { id: 1, name: 'New Template', config: {}, created_at: '2024-01-01' };

      templatesStore.addTemplate(newTemplate);

      const state = get(templatesStore);
      expect(state.templates).toHaveLength(1);
      expect(state.templates[0]).toEqual(newTemplate);
    });

    it('should add multiple templates', () => {
      const template1 = { id: 1, name: 'Template 1', config: {}, created_at: '2024-01-01' };
      const template2 = { id: 2, name: 'Template 2', config: {}, created_at: '2024-01-02' };

      templatesStore.addTemplate(template1);
      templatesStore.addTemplate(template2);

      const state = get(templatesStore);
      expect(state.templates).toHaveLength(2);
    });
  });

  describe('removeTemplate', () => {
    it('should remove a template by ID', () => {
      const template1 = { id: 1, name: 'Template 1', config: {}, created_at: '2024-01-01' };
      const template2 = { id: 2, name: 'Template 2', config: {}, created_at: '2024-01-02' };

      templatesStore.addTemplate(template1);
      templatesStore.addTemplate(template2);

      templatesStore.removeTemplate(1);

      const state = get(templatesStore);
      expect(state.templates).toHaveLength(1);
      expect(state.templates[0]).toEqual(template2);
    });

    it('should handle removing non-existent template', () => {
      const template1 = { id: 1, name: 'Template 1', config: {}, created_at: '2024-01-01' };

      templatesStore.addTemplate(template1);

      templatesStore.removeTemplate(999);

      const state = get(templatesStore);
      expect(state.templates).toHaveLength(1);
    });
  });

  describe('setLoading', () => {
    it('should set loading state', () => {
      templatesStore.setLoading(true);
      expect(get(templatesStore).loading).toBe(true);

      templatesStore.setLoading(false);
      expect(get(templatesStore).loading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should set error message', () => {
      const errorMessage = 'Failed to load templates';
      templatesStore.setError(errorMessage);

      const state = get(templatesStore);
      expect(state.error).toBe(errorMessage);
      expect(state.loading).toBe(false);
    });

    it('should clear error when null is passed', () => {
      templatesStore.setError('Some error');
      expect(get(templatesStore).error).toBe('Some error');

      templatesStore.setError(null);
      expect(get(templatesStore).error).toBeNull();
    });
  });

  describe('selectors', () => {
    it('should select templates', () => {
      const templatesData = [{ id: 1, name: 'Template 1', config: {}, created_at: '2024-01-01' }];
      templatesStore.setTemplates(templatesData);

      const templates = get(templatesStore.templates);
      expect(templates).toEqual(templatesData);
    });

    it('should select loading state', () => {
      templatesStore.setLoading(true);
      const loading = get(templatesStore.isLoading);
      expect(loading).toBe(true);
    });

    it('should select error', () => {
      templatesStore.setError('Test error');
      const error = get(templatesStore.error);
      expect(error).toBe('Test error');
    });
  });

  describe('reset', () => {
    it('should reset to all initial state', () => {
      const templatesData = [{ id: 1, name: 'Template 1', config: {}, created_at: '2024-01-01' }];
      templatesStore.setTemplates(templatesData);
      templatesStore.setLoading(true);
      templatesStore.setError('Test error');

      templatesStore.reset();

      const state = get(templatesStore);
      expect(state).toEqual({
        templates: [],
        loading: false,
        error: null
      });
    });
  });
});
