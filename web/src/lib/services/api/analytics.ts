import { getApiClient } from './client';

export interface SplitAnalytics {
  total_splits: number;
  total_amount: number;
  average_split_amount: number;
  splits_by_currency: Record<string, number>;
  splits_by_month: Array<{
    month: string;
    count: number;
    amount: number;
  }>;
}

export interface UserAnalytics {
  user_id: number;
  total_paid: number;
  total_owed: number;
  average_payment: number;
  most_frequent_currency: string;
  splits_participated: number;
}

export interface GroupAnalytics {
  group_id: number;
  total_splits: number;
  total_amount: number;
  average_per_member: number;
  member_contributions: Array<{
    member_id: number;
    name: string;
    total_paid: number;
    total_owed: number;
  }>;
}

export interface AppAnalytics {
  active_users: number;
  total_splits_created: number;
  total_amount_processed: number;
  average_split_size: number;
  top_currencies: Array<{
    currency: string;
    count: number;
    percentage: number;
  }>;
}

/** Analytics service */
export class AnalyticsService {
  /** Get split analytics */
  async getSplitAnalytics(timeRange: 'week' | 'month' | 'year' = 'month'): Promise<SplitAnalytics> {
    const apiClient = getApiClient();
    return apiClient.get<SplitAnalytics>(`/analytics/splits?range=${timeRange}`);
  }

  /** Get user analytics */
  async getUserAnalytics(userId: number, timeRange: 'week' | 'month' | 'year' = 'month'): Promise<UserAnalytics> {
    const apiClient = getApiClient();
    return apiClient.get<UserAnalytics>(`/analytics/users/${userId}?range=${timeRange}`);
  }

  /** Get group analytics */
  async getGroupAnalytics(groupId: number, timeRange: 'week' | 'month' | 'year' = 'month'): Promise<GroupAnalytics> {
    const apiClient = getApiClient();
    return apiClient.get<GroupAnalytics>(`/analytics/groups/${groupId}?range=${timeRange}`);
  }

  /** Get app-wide analytics */
  async getAppAnalytics(): Promise<AppAnalytics> {
    const apiClient = getApiClient();
    return apiClient.get<AppAnalytics>('/analytics/app');
  }

  /** Get popular splits */
  async getPopularSplits(limit: number = 10): Promise<Array<{
    split_id: string;
    name: string;
    view_count: number;
    total_amount: number;
    created_at: string;
  }>> {
    const apiClient = getApiClient();
    return apiClient.get(`/analytics/popular-splits?limit=${limit}`);
  }

  /** Get trending templates */
  async getTrendingTemplates(limit: number = 10): Promise<Array<{
    template_id: number;
    name: string;
    usage_count: number;
    average_amount: number;
  }>> {
    const apiClient = getApiClient();
    return apiClient.get(`/analytics/trending-templates?limit=${limit}`);
  }

  /** Export analytics data */
  async exportAnalytics(
    type: 'splits' | 'payments' | 'groups',
    format: 'csv' | 'json',
    dateFrom?: string,
    dateTo?: string
  ): Promise<{
    download_url: string;
    expires_at: string;
  }> {
    const apiClient = getApiClient();
    const params = new URLSearchParams({ type, format });
    if (dateFrom) params.append('from', dateFrom);
    if (dateTo) params.append('to', dateTo);
    return apiClient.get(`/analytics/export?${params}`);
  }
}

export const analyticsService = new AnalyticsService();
