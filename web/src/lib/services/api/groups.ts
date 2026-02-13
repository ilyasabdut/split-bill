import { getApiClient } from './client';
import type { Group, GroupMember } from '$lib/stores/groups';

export interface CreateGroupRequest {
  name: string;
  member_names: string[];
}

export interface UpdateGroupRequest {
  name?: string;
  members?: Array<{
    id?: number;
    name: string;
  }>;
}

export interface AddGroupMemberRequest {
  name: string;
}

/** Groups management service */
export class GroupsService {
  /** Get all groups */
  async getGroups(): Promise<Group[]> {
    const apiClient = getApiClient();
    return apiClient.get<Group[]>('/groups');
  }

  /** Get single group by ID */
  async getGroup(id: number): Promise<Group> {
    const apiClient = getApiClient();
    return apiClient.get<Group>(`/groups/${id}`);
  }

  /** Create new group */
  async createGroup(request: CreateGroupRequest): Promise<Group> {
    const apiClient = getApiClient();
    return apiClient.post<Group>('/groups', request);
  }

  /** Update group */
  async updateGroup(id: number, request: UpdateGroupRequest): Promise<Group> {
    const apiClient = getApiClient();
    return apiClient.post<Group>(`/groups/${id}`, request);
  }

  /** Delete group */
  async deleteGroup(id: number): Promise<void> {
    const apiClient = getApiClient();
    return apiClient.get(`/groups/${id}/delete`);
  }

  /** Add member to group */
  async addMember(groupId: number, request: AddGroupMemberRequest): Promise<GroupMember> {
    const apiClient = getApiClient();
    return apiClient.post<GroupMember>(`/groups/${groupId}/members`, request);
  }

  /** Remove member from group */
  async removeMember(groupId: number, memberId: number): Promise<void> {
    const apiClient = getApiClient();
    return apiClient.get(`/groups/${groupId}/members/${memberId}/delete`);
  }

  /** Get group statistics */
  async getGroupStats(id: number): Promise<{
    total_members: number;
    total_splits: number;
    total_amount: number;
    average_per_member: number;
  }> {
    const apiClient = getApiClient();
    return apiClient.get(`/groups/${id}/stats`);
  }
}

export const groupsService = new GroupsService();
