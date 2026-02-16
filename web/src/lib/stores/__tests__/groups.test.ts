import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { groupsStore } from '../groups';

describe('groupsStore', () => {
  beforeEach(() => {
    groupsStore.reset();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = get(groupsStore);
      expect(state).toEqual({
        groups: [],
        currentGroupId: null,
        loading: false,
        error: null
      });
    });
  });

  describe('setGroups', () => {
    it('should set groups data', () => {
      const groupsData = [
        { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' },
        { id: 2, name: 'Group 2', members: [], created_at: '2024-01-02' }
      ];

      groupsStore.setGroups(groupsData);

      const state = get(groupsStore);
      expect(state.groups).toEqual(groupsData);
      expect(state.loading).toBe(false);
    });
  });

  describe('setCurrentGroup', () => {
    it('should set current group ID', () => {
      groupsStore.setCurrentGroup(1);
      expect(get(groupsStore).currentGroupId).toBe(1);
    });

    it('should clear current group ID', () => {
      groupsStore.setCurrentGroup(1);
      expect(get(groupsStore).currentGroupId).toBe(1);

      groupsStore.setCurrentGroup(null);
      expect(get(groupsStore).currentGroupId).toBeNull();
    });
  });

  describe('addGroup', () => {
    it('should add a group', () => {
      const newGroup = { id: 1, name: 'New Group', members: [], created_at: '2024-01-01' };

      groupsStore.addGroup(newGroup);

      const state = get(groupsStore);
      expect(state.groups).toHaveLength(1);
      expect(state.groups[0]).toEqual(newGroup);
    });

    it('should add multiple groups', () => {
      const group1 = { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' };
      const group2 = { id: 2, name: 'Group 2', members: [], created_at: '2024-01-02' };

      groupsStore.addGroup(group1);
      groupsStore.addGroup(group2);

      const state = get(groupsStore);
      expect(state.groups).toHaveLength(2);
    });
  });

  describe('updateGroup', () => {
    it('should update an existing group', () => {
      const group1 = { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' };
      const group2 = { id: 2, name: 'Group 2', members: [], created_at: '2024-01-02' };

      groupsStore.addGroup(group1);
      groupsStore.addGroup(group2);

      const updatedGroup = { id: 1, name: 'Updated Group 1', members: [], created_at: '2024-01-01' };
      groupsStore.updateGroup(updatedGroup);

      const state = get(groupsStore);
      expect(state.groups[0]).toEqual(updatedGroup);
      expect(state.groups[1]).toEqual(group2);
    });

    it('should handle non-existent group', () => {
      const group1 = { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' };

      groupsStore.addGroup(group1);

      const nonExistentGroup = { id: 999, name: 'Non-existent', members: [], created_at: '2024-01-01' };
      groupsStore.updateGroup(nonExistentGroup);

      const state = get(groupsStore);
      expect(state.groups).toHaveLength(1);
    });
  });

  describe('removeGroup', () => {
    it('should remove a group by ID', () => {
      const group1 = { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' };
      const group2 = { id: 2, name: 'Group 2', members: [], created_at: '2024-01-02' };

      groupsStore.addGroup(group1);
      groupsStore.addGroup(group2);

      groupsStore.removeGroup(1);

      const state = get(groupsStore);
      expect(state.groups).toHaveLength(1);
      expect(state.groups[0]).toEqual(group2);
    });

    it('should clear current group ID when removing current group', () => {
      const group1 = { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' };

      groupsStore.addGroup(group1);
      groupsStore.setCurrentGroup(1);

      groupsStore.removeGroup(1);

      expect(get(groupsStore).currentGroupId).toBeNull();
    });

    it('should keep current group ID when removing different group', () => {
      const group1 = { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' };
      const group2 = { id: 2, name: 'Group 2', members: [], created_at: '2024-01-02' };

      groupsStore.addGroup(group1);
      groupsStore.addGroup(group2);
      groupsStore.setCurrentGroup(1);

      groupsStore.removeGroup(2);

      expect(get(groupsStore).currentGroupId).toBe(1);
    });
  });

  describe('setLoading', () => {
    it('should set loading state', () => {
      groupsStore.setLoading(true);
      expect(get(groupsStore).loading).toBe(true);

      groupsStore.setLoading(false);
      expect(get(groupsStore).loading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should set error message', () => {
      const errorMessage = 'Failed to load groups';
      groupsStore.setError(errorMessage);

      const state = get(groupsStore);
      expect(state.error).toBe(errorMessage);
      expect(state.loading).toBe(false);
    });

    it('should clear error when null is passed', () => {
      groupsStore.setError('Some error');
      expect(get(groupsStore).error).toBe('Some error');

      groupsStore.setError(null);
      expect(get(groupsStore).error).toBeNull();
    });
  });

  describe('selectors', () => {
    it('should select groups', () => {
      const groupsData = [
        { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' }
      ];

      groupsStore.setGroups(groupsData);

      const groups = get(groupsStore.groups);
      expect(groups).toEqual(groupsData);
    });

    it('should select current group', () => {
      const group1 = { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' };
      const group2 = { id: 2, name: 'Group 2', members: [], created_at: '2024-01-02' };

      groupsStore.addGroup(group1);
      groupsStore.addGroup(group2);
      groupsStore.setCurrentGroup(1);

      const currentGroup = get(groupsStore.currentGroup);
      expect(currentGroup).toEqual(group1);
    });

    it('should return null when no current group is set', () => {
      const currentGroup = get(groupsStore.currentGroup);
      expect(currentGroup).toBeNull();
    });

    it('should select loading state', () => {
      groupsStore.setLoading(true);
      const loading = get(groupsStore.isLoading);
      expect(loading).toBe(true);
    });

    it('should select error', () => {
      groupsStore.setError('Test error');
      const error = get(groupsStore.error);
      expect(error).toBe('Test error');
    });
    });

  describe('reset', () => {
    it('should reset to initial state', () => {
      const groupsData = [
        { id: 1, name: 'Group 1', members: [], created_at: '2024-01-01' }
      ];

      groupsStore.setGroups(groupsData);
      groupsStore.setCurrentGroup(1);
      groupsStore.setLoading(true);
      groupsStore.setError('Test error');

      groupsStore.reset();

      const state = get(groupsStore);
      expect(state).toEqual({
        groups: [],
        currentGroupId: null,
        loading: false,
        error: null
      });
    });
  });
});
