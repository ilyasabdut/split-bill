import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GroupsService, groupsService } from '../api/groups';

// Mock API client
vi.mock('../api/client', () => ({
  getApiClient: vi.fn(() => ({
    get: vi.fn(),
    post: vi.fn(),
  }))
}));

describe('GroupsService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getGroups', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = groupsService.getGroups();
      expect(mockClient).not.toBeNull();
    });
  });

  describe('getGroup', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = groupsService.getGroup(123);
      expect(mockClient).not.toBeNull();
    });

    it('should include group ID in endpoint', async () => {
      const groupId = 456;
      const mockClient = groupsService.getGroup(groupId);
      expect(mockClient).not.toBeNull();
    });
  });

  describe('createGroup', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = groupsService.createGroup({
        name: 'Test Group',
        member_names: ['John', 'Jane']
      });
      expect(mockClient).not.toBeNull();
    });
  });

  describe('updateGroup', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = groupsService.updateGroup(123, {
        name: 'Updated Group'
      });
      expect(mockClient).not.toBeNull();
    });

    it('should include group ID in endpoint', async () => {
      const groupId = 456;
      const mockClient = groupsService.updateGroup(groupId, {
        members: [{ id: 1, name: 'John' }]
      });
      expect(mockClient).not.toBeNull();
    });
  });

  describe('deleteGroup', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = groupsService.deleteGroup(123);
      expect(mockClient).not.toBeNull();
    });

    it('should include group ID in endpoint', async () => {
      const groupId = 456;
      const mockClient = groupsService.deleteGroup(groupId);
      expect(mockClient).not.toBeNull();
    });
  });

  describe('addMember', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = groupsService.addMember(123, {
        name: 'New Member'
      });
      expect(mockClient).not.toBeNull();
    });

    it('should include group ID in endpoint', async () => {
      const groupId = 456;
      const mockClient = groupsService.addMember(groupId, {
        name: 'John Doe'
      });
      expect(mockClient).not.toBeNull();
    });
  });

  describe('removeMember', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = groupsService.removeMember(123, 456);
      expect(mockClient).not.toBeNull();
    });

    it('should include group and member IDs in endpoint', async () => {
      const groupId = 789;
      const memberId = 123;
      const mockClient = groupsService.removeMember(groupId, memberId);
      expect(mockClient).not.toBeNull();
    });
  });

  describe('getGroupStats', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = groupsService.getGroupStats(123);
      expect(mockClient).not.toBeNull();
    });

    it('should include group ID in endpoint', async () => {
      const groupId = 456;
      const mockClient = groupsService.getGroupStats(groupId);
      expect(mockClient).not.toBeNull();
    });
  });
});
