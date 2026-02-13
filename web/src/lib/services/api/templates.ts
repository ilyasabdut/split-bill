import { getApiClient } from './client';
import type { Template } from '$lib/stores/templates';

export interface CreateTemplateRequest {
  name: string;
  config: Record<string, any>;
}

export interface UpdateTemplateRequest {
  name?: string;
  config?: Record<string, any>;
}

export interface ApplyTemplateRequest {
  template_id: number;
  split_data: Record<string, any>;
}

/** Templates management service */
export class TemplatesService {
  /** Get all templates */
  async getTemplates(): Promise<Template[]> {
    const apiClient = getApiClient();
    return apiClient.get<Template[]>('/templates');
  }

  /** Get single template by ID */
  async getTemplate(id: number): Promise<Template> {
    const apiClient = getApiClient();
    return apiClient.get<Template>(`/templates/${id}`);
  }

  /** Create new template */
  async createTemplate(request: CreateTemplateRequest): Promise<Template> {
    const apiClient = getApiClient();
    return apiClient.post<Template>('/templates', request);
  }

  /** Update template */
  async updateTemplate(id: number, request: UpdateTemplateRequest): Promise<Template> {
    const apiClient = getApiClient();
    return apiClient.post<Template>(`/templates/${id}`, request);
  }

  /** Delete template */
  async deleteTemplate(id: number): Promise<void> {
    const apiClient = getApiClient();
    return apiClient.get(`/templates/${id}/delete`);
  }

  /** Apply template to split data */
  async applyTemplate(request: ApplyTemplateRequest): Promise<{
    split_data: Record<string, any>;
    applied_config: Record<string, any>;
  }> {
    const apiClient = getApiClient();
    return apiClient.post('/templates/apply', request);
  }

  /** Duplicate existing template */
  async duplicateTemplate(id: number, newName: string): Promise<Template> {
    const apiClient = getApiClient();
    return apiClient.post<Template>(`/templates/${id}/duplicate`, { name: newName });
  }

  /** Get template usage statistics */
  async getTemplateStats(id: number): Promise<{
    usage_count: number;
    last_used: string | null;
    average_savings: number;
  }> {
    const apiClient = getApiClient();
    return apiClient.get(`/templates/${id}/stats`);
  }
}

export const templatesService = new TemplatesService();
