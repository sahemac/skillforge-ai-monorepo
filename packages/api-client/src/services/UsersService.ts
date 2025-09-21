/**
 * UsersService - User management service
 * Handles CRUD operations for users and user-related functionality
 */

import { ApiClient } from '../client/ApiClient';
import type {
  UserResponse,
  CreateUserRequest,
  UpdateUserRequest,
  GetUsersQuery,
  PaginatedResponse,
  RequestConfig,
} from '../types';

export class UsersService {
  constructor(private apiClient: ApiClient) {}

  /**
   * Get paginated list of users
   */
  async getUsers(
    params: GetUsersQuery = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<UserResponse>> {
    return this.apiClient.get<PaginatedResponse<UserResponse>>('/users', params, config);
  }

  /**
   * Get user by ID
   */
  async getUserById(id: string, config?: RequestConfig): Promise<UserResponse> {
    return this.apiClient.get<UserResponse>(`/users/${id}`, undefined, config);
  }

  /**
   * Create new user
   */
  async createUser(userData: CreateUserRequest, config?: RequestConfig): Promise<UserResponse> {
    return this.apiClient.post<UserResponse>('/users', userData, config);
  }

  /**
   * Update user
   */
  async updateUser(
    id: string,
    updates: UpdateUserRequest,
    config?: RequestConfig
  ): Promise<UserResponse> {
    return this.apiClient.patch<UserResponse>(`/users/${id}`, updates, config);
  }

  /**
   * Delete user
   */
  async deleteUser(id: string, config?: RequestConfig): Promise<{ message: string }> {
    return this.apiClient.delete<{ message: string }>(`/users/${id}`, config);
  }

  /**
   * Activate user account
   */
  async activateUser(id: string, config?: RequestConfig): Promise<UserResponse> {
    return this.apiClient.post<UserResponse>(`/users/${id}/activate`, {}, config);
  }

  /**
   * Deactivate user account
   */
  async deactivateUser(id: string, config?: RequestConfig): Promise<UserResponse> {
    return this.apiClient.post<UserResponse>(`/users/${id}/deactivate`, {}, config);
  }

  /**
   * Get users by role
   */
  async getUsersByRole(
    role: 'learner' | 'company' | 'admin',
    params: Omit<GetUsersQuery, 'role'> = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<UserResponse>> {
    return this.getUsers({ ...params, role }, config);
  }

  /**
   * Search users by term
   */
  async searchUsers(
    searchTerm: string,
    params: Omit<GetUsersQuery, 'search'> = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<UserResponse>> {
    return this.getUsers({ ...params, search: searchTerm }, config);
  }

  /**
   * Get user profile
   */
  async getUserProfile(id: string, config?: RequestConfig): Promise<UserResponse['profile']> {
    return this.apiClient.get<UserResponse['profile']>(`/users/${id}/profile`, undefined, config);
  }

  /**
   * Update user profile
   */
  async updateUserProfile(
    id: string,
    profile: NonNullable<UserResponse['profile']>,
    config?: RequestConfig
  ): Promise<UserResponse['profile']> {
    return this.apiClient.patch<UserResponse['profile']>(`/users/${id}/profile`, profile, config);
  }

  /**
   * Upload user avatar
   */
  async uploadAvatar(
    id: string,
    file: File,
    config?: RequestConfig & { onUploadProgress?: (progress: number) => void }
  ): Promise<{ avatarUrl: string }> {
    return this.apiClient.upload<{ avatarUrl: string }>(
      `/users/${id}/avatar`,
      file,
      {
        ...config,
        onUploadProgress: (progressEvent) => {
          if (config?.onUploadProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            config.onUploadProgress(progress);
          }
        },
      }
    );
  }

  /**
   * Delete user avatar
   */
  async deleteAvatar(id: string, config?: RequestConfig): Promise<{ message: string }> {
    return this.apiClient.delete<{ message: string }>(`/users/${id}/avatar`, config);
  }

  /**
   * Get user skills
   */
  async getUserSkills(id: string, config?: RequestConfig): Promise<string[]> {
    return this.apiClient.get<string[]>(`/users/${id}/skills`, undefined, config);
  }

  /**
   * Update user skills
   */
  async updateUserSkills(
    id: string,
    skills: string[],
    config?: RequestConfig
  ): Promise<string[]> {
    return this.apiClient.patch<string[]>(`/users/${id}/skills`, { skills }, config);
  }

  /**
   * Add skill to user
   */
  async addUserSkill(id: string, skill: string, config?: RequestConfig): Promise<string[]> {
    return this.apiClient.post<string[]>(`/users/${id}/skills`, { skill }, config);
  }

  /**
   * Remove skill from user
   */
  async removeUserSkill(id: string, skill: string, config?: RequestConfig): Promise<string[]> {
    return this.apiClient.delete<string[]>(`/users/${id}/skills/${encodeURIComponent(skill)}`, config);
  }

  /**
   * Get user preferences
   */
  async getUserPreferences(
    id: string,
    config?: RequestConfig
  ): Promise<Record<string, any>> {
    return this.apiClient.get<Record<string, any>>(`/users/${id}/preferences`, undefined, config);
  }

  /**
   * Update user preferences
   */
  async updateUserPreferences(
    id: string,
    preferences: Record<string, any>,
    config?: RequestConfig
  ): Promise<Record<string, any>> {
    return this.apiClient.patch<Record<string, any>>(`/users/${id}/preferences`, preferences, config);
  }

  /**
   * Get user activity log
   */
  async getUserActivity(
    id: string,
    params: {
      page?: number;
      limit?: number;
      startDate?: string;
      endDate?: string;
      activityType?: string;
    } = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<{
    id: string;
    userId: string;
    type: string;
    description: string;
    metadata: Record<string, any>;
    createdAt: string;
  }>> {
    return this.apiClient.get<PaginatedResponse<any>>(`/users/${id}/activity`, params, config);
  }

  /**
   * Get user statistics
   */
  async getUserStats(
    id: string,
    config?: RequestConfig
  ): Promise<{
    projectsCompleted: number;
    projectsInProgress: number;
    skillsAcquired: number;
    totalTimeSpent: number;
    lastActive: string;
    joinedAt: string;
  }> {
    return this.apiClient.get<any>(`/users/${id}/stats`, undefined, config);
  }

  /**
   * Get user notifications settings
   */
  async getUserNotificationSettings(
    id: string,
    config?: RequestConfig
  ): Promise<{
    email: boolean;
    push: boolean;
    inApp: boolean;
    digest: 'daily' | 'weekly' | 'never';
    categories: Record<string, boolean>;
  }> {
    return this.apiClient.get<any>(`/users/${id}/notification-settings`, undefined, config);
  }

  /**
   * Update user notification settings
   */
  async updateUserNotificationSettings(
    id: string,
    settings: {
      email?: boolean;
      push?: boolean;
      inApp?: boolean;
      digest?: 'daily' | 'weekly' | 'never';
      categories?: Record<string, boolean>;
    },
    config?: RequestConfig
  ): Promise<{
    email: boolean;
    push: boolean;
    inApp: boolean;
    digest: 'daily' | 'weekly' | 'never';
    categories: Record<string, boolean>;
  }> {
    return this.apiClient.patch<any>(`/users/${id}/notification-settings`, settings, config);
  }

  /**
   * Bulk update users
   */
  async bulkUpdateUsers(
    updates: Array<{ id: string; updates: UpdateUserRequest }>,
    config?: RequestConfig
  ): Promise<{ updated: UserResponse[]; errors: Array<{ id: string; error: string }> }> {
    return this.apiClient.post<any>('/users/bulk-update', { updates }, config);
  }

  /**
   * Export users data
   */
  async exportUsers(
    params: GetUsersQuery & { format?: 'csv' | 'json' | 'xlsx' } = {},
    config?: RequestConfig
  ): Promise<{ downloadUrl: string; expiresAt: string }> {
    return this.apiClient.post<any>('/users/export', params, config);
  }

  /**
   * Import users from file
   */
  async importUsers(
    file: File,
    config?: RequestConfig & { onUploadProgress?: (progress: number) => void }
  ): Promise<{
    imported: number;
    failed: number;
    errors: Array<{ row: number; error: string }>;
  }> {
    return this.apiClient.upload<any>('/users/import', file, {
      ...config,
      onUploadProgress: (progressEvent) => {
        if (config?.onUploadProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          config.onUploadProgress(progress);
        }
      },
    });
  }
}

export default UsersService;