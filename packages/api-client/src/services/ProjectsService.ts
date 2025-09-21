/**
 * ProjectsService - Project management service
 * Handles CRUD operations for projects and project-related functionality
 */

import { ApiClient } from '../client/ApiClient';
import type {
  ProjectResponse,
  CreateProjectRequest,
  UpdateProjectRequest,
  GetProjectsQuery,
  PaginatedResponse,
  RequestConfig,
} from '../types';

export class ProjectsService {
  constructor(private apiClient: ApiClient) {}

  /**
   * Get paginated list of projects
   */
  async getProjects(
    params: GetProjectsQuery = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    return this.apiClient.get<PaginatedResponse<ProjectResponse>>('/projects', params, config);
  }

  /**
   * Get project by ID
   */
  async getProjectById(id: string, config?: RequestConfig): Promise<ProjectResponse> {
    return this.apiClient.get<ProjectResponse>(`/projects/${id}`, undefined, config);
  }

  /**
   * Create new project
   */
  async createProject(
    projectData: CreateProjectRequest,
    config?: RequestConfig
  ): Promise<ProjectResponse> {
    return this.apiClient.post<ProjectResponse>('/projects', projectData, config);
  }

  /**
   * Update project
   */
  async updateProject(
    id: string,
    updates: UpdateProjectRequest,
    config?: RequestConfig
  ): Promise<ProjectResponse> {
    return this.apiClient.patch<ProjectResponse>(`/projects/${id}`, updates, config);
  }

  /**
   * Delete project
   */
  async deleteProject(id: string, config?: RequestConfig): Promise<{ message: string }> {
    return this.apiClient.delete<{ message: string }>(`/projects/${id}`, config);
  }

  /**
   * Publish project (make it active)
   */
  async publishProject(id: string, config?: RequestConfig): Promise<ProjectResponse> {
    return this.apiClient.post<ProjectResponse>(`/projects/${id}/publish`, {}, config);
  }

  /**
   * Archive project
   */
  async archiveProject(id: string, config?: RequestConfig): Promise<ProjectResponse> {
    return this.apiClient.post<ProjectResponse>(`/projects/${id}/archive`, {}, config);
  }

  /**
   * Duplicate project
   */
  async duplicateProject(
    id: string,
    title?: string,
    config?: RequestConfig
  ): Promise<ProjectResponse> {
    return this.apiClient.post<ProjectResponse>(`/projects/${id}/duplicate`, { title }, config);
  }

  /**
   * Get projects by status
   */
  async getProjectsByStatus(
    status: 'draft' | 'active' | 'completed' | 'archived',
    params: Omit<GetProjectsQuery, 'status'> = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    return this.getProjects({ ...params, status }, config);
  }

  /**
   * Get projects by difficulty
   */
  async getProjectsByDifficulty(
    difficulty: 'beginner' | 'intermediate' | 'advanced',
    params: Omit<GetProjectsQuery, 'difficulty'> = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    return this.getProjects({ ...params, difficulty }, config);
  }

  /**
   * Get projects by author
   */
  async getProjectsByAuthor(
    authorId: string,
    params: Omit<GetProjectsQuery, 'authorId'> = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    return this.getProjects({ ...params, authorId }, config);
  }

  /**
   * Search projects
   */
  async searchProjects(
    searchTerm: string,
    params: Omit<GetProjectsQuery, 'search'> = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    return this.getProjects({ ...params, search: searchTerm }, config);
  }

  /**
   * Get projects by skills
   */
  async getProjectsBySkills(
    skills: string[],
    params: Omit<GetProjectsQuery, 'skills'> = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    return this.getProjects({ ...params, skills }, config);
  }

  /**
   * Get featured projects
   */
  async getFeaturedProjects(
    params: GetProjectsQuery = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    return this.apiClient.get<PaginatedResponse<ProjectResponse>>('/projects/featured', params, config);
  }

  /**
   * Get recommended projects for user
   */
  async getRecommendedProjects(
    userId?: string,
    params: GetProjectsQuery = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    const url = userId ? `/projects/recommended/${userId}` : '/projects/recommended';
    return this.apiClient.get<PaginatedResponse<ProjectResponse>>(url, params, config);
  }

  /**
   * Get project statistics
   */
  async getProjectStats(
    id: string,
    config?: RequestConfig
  ): Promise<{
    views: number;
    enrollments: number;
    completions: number;
    averageRating: number;
    totalRatings: number;
    completionRate: number;
    averageCompletionTime: number;
  }> {
    return this.apiClient.get<any>(`/projects/${id}/stats`, undefined, config);
  }

  /**
   * Get project reviews
   */
  async getProjectReviews(
    id: string,
    params: {
      page?: number;
      limit?: number;
      rating?: number;
      sortBy?: 'createdAt' | 'rating' | 'helpful';
      sortOrder?: 'asc' | 'desc';
    } = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<{
    id: string;
    userId: string;
    user: {
      id: string;
      username: string;
      avatar?: string;
    };
    rating: number;
    comment: string;
    helpful: number;
    createdAt: string;
  }>> {
    return this.apiClient.get<PaginatedResponse<any>>(`/projects/${id}/reviews`, params, config);
  }

  /**
   * Add project review
   */
  async addProjectReview(
    id: string,
    review: {
      rating: number;
      comment: string;
    },
    config?: RequestConfig
  ): Promise<{
    id: string;
    userId: string;
    rating: number;
    comment: string;
    createdAt: string;
  }> {
    return this.apiClient.post<any>(`/projects/${id}/reviews`, review, config);
  }

  /**
   * Update project review
   */
  async updateProjectReview(
    projectId: string,
    reviewId: string,
    updates: {
      rating?: number;
      comment?: string;
    },
    config?: RequestConfig
  ): Promise<{
    id: string;
    userId: string;
    rating: number;
    comment: string;
    updatedAt: string;
  }> {
    return this.apiClient.patch<any>(`/projects/${projectId}/reviews/${reviewId}`, updates, config);
  }

  /**
   * Delete project review
   */
  async deleteProjectReview(
    projectId: string,
    reviewId: string,
    config?: RequestConfig
  ): Promise<{ message: string }> {
    return this.apiClient.delete<{ message: string }>(`/projects/${projectId}/reviews/${reviewId}`, config);
  }

  /**
   * Mark review as helpful
   */
  async markReviewHelpful(
    projectId: string,
    reviewId: string,
    config?: RequestConfig
  ): Promise<{ helpful: number }> {
    return this.apiClient.post<{ helpful: number }>(`/projects/${projectId}/reviews/${reviewId}/helpful`, {}, config);
  }

  /**
   * Enroll in project
   */
  async enrollInProject(id: string, config?: RequestConfig): Promise<{
    enrollmentId: string;
    projectId: string;
    userId: string;
    enrolledAt: string;
    status: 'enrolled' | 'in_progress' | 'completed' | 'dropped';
  }> {
    return this.apiClient.post<any>(`/projects/${id}/enroll`, {}, config);
  }

  /**
   * Unenroll from project
   */
  async unenrollFromProject(id: string, config?: RequestConfig): Promise<{ message: string }> {
    return this.apiClient.post<{ message: string }>(`/projects/${id}/unenroll`, {}, config);
  }

  /**
   * Get enrollment status
   */
  async getEnrollmentStatus(
    id: string,
    userId?: string,
    config?: RequestConfig
  ): Promise<{
    enrolled: boolean;
    enrollmentId?: string;
    status?: 'enrolled' | 'in_progress' | 'completed' | 'dropped';
    progress?: number;
    enrolledAt?: string;
    completedAt?: string;
  }> {
    const params = userId ? { userId } : undefined;
    return this.apiClient.get<any>(`/projects/${id}/enrollment`, params, config);
  }

  /**
   * Update project progress
   */
  async updateProjectProgress(
    id: string,
    progress: number,
    config?: RequestConfig
  ): Promise<{
    enrollmentId: string;
    progress: number;
    status: 'enrolled' | 'in_progress' | 'completed' | 'dropped';
    updatedAt: string;
  }> {
    return this.apiClient.patch<any>(`/projects/${id}/progress`, { progress }, config);
  }

  /**
   * Complete project
   */
  async completeProject(id: string, config?: RequestConfig): Promise<{
    enrollmentId: string;
    completedAt: string;
    certificate?: {
      id: string;
      url: string;
    };
  }> {
    return this.apiClient.post<any>(`/projects/${id}/complete`, {}, config);
  }

  /**
   * Get project materials
   */
  async getProjectMaterials(
    id: string,
    config?: RequestConfig
  ): Promise<Array<{
    id: string;
    title: string;
    type: 'document' | 'video' | 'image' | 'code' | 'other';
    url: string;
    size?: number;
    createdAt: string;
  }>> {
    return this.apiClient.get<any[]>(`/projects/${id}/materials`, undefined, config);
  }

  /**
   * Upload project material
   */
  async uploadProjectMaterial(
    id: string,
    file: File,
    title: string,
    type: 'document' | 'video' | 'image' | 'code' | 'other',
    config?: RequestConfig & { onUploadProgress?: (progress: number) => void }
  ): Promise<{
    id: string;
    title: string;
    type: string;
    url: string;
    size: number;
    createdAt: string;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('type', type);

    return this.apiClient.upload<any>(`/projects/${id}/materials`, formData, {
      ...config,
      onUploadProgress: (progressEvent) => {
        if (config?.onUploadProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          config.onUploadProgress(progress);
        }
      },
    });
  }

  /**
   * Delete project material
   */
  async deleteProjectMaterial(
    projectId: string,
    materialId: string,
    config?: RequestConfig
  ): Promise<{ message: string }> {
    return this.apiClient.delete<{ message: string }>(`/projects/${projectId}/materials/${materialId}`, config);
  }

  /**
   * Export project data
   */
  async exportProject(
    id: string,
    format: 'json' | 'pdf' | 'markdown' = 'json',
    config?: RequestConfig
  ): Promise<{ downloadUrl: string; expiresAt: string }> {
    return this.apiClient.post<any>(`/projects/${id}/export`, { format }, config);
  }

  /**
   * Import project from file
   */
  async importProject(
    file: File,
    config?: RequestConfig & { onUploadProgress?: (progress: number) => void }
  ): Promise<ProjectResponse> {
    return this.apiClient.upload<ProjectResponse>('/projects/import', file, {
      ...config,
      onUploadProgress: (progressEvent) => {
        if (config?.onUploadProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          config.onUploadProgress(progress);
        }
      },
    });
  }

  /**
   * Get project templates
   */
  async getProjectTemplates(
    params: {
      category?: string;
      difficulty?: 'beginner' | 'intermediate' | 'advanced';
      page?: number;
      limit?: number;
    } = {},
    config?: RequestConfig
  ): Promise<PaginatedResponse<ProjectResponse>> {
    return this.apiClient.get<PaginatedResponse<ProjectResponse>>('/projects/templates', params, config);
  }

  /**
   * Create project from template
   */
  async createProjectFromTemplate(
    templateId: string,
    customizations: {
      title: string;
      description?: string;
      difficulty?: 'beginner' | 'intermediate' | 'advanced';
      estimatedDuration?: number;
    },
    config?: RequestConfig
  ): Promise<ProjectResponse> {
    return this.apiClient.post<ProjectResponse>(`/projects/templates/${templateId}/create`, customizations, config);
  }
}

export default ProjectsService;