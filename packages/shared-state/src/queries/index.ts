/**
 * TanStack Query setup for CQRS read operations
 * Handles all query (read) operations with caching and synchronization
 */

import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import type { 
  User, 
  Project, 
  GetUserQueryParams,
  GetUsersQueryParams,
  GetProjectQueryParams,
  GetProjectsQueryParams 
} from '../types';

// Query client configuration
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Query keys factory for consistent key management
export const queryKeys = {
  // User queries
  users: {
    all: ['users'] as const,
    lists: () => [...queryKeys.users.all, 'list'] as const,
    list: (params: GetUsersQueryParams) => [...queryKeys.users.lists(), params] as const,
    details: () => [...queryKeys.users.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.users.details(), id] as const,
  },
  // Project queries
  projects: {
    all: ['projects'] as const,
    lists: () => [...queryKeys.projects.all, 'list'] as const,
    list: (params: GetProjectsQueryParams) => [...queryKeys.projects.lists(), params] as const,
    details: () => [...queryKeys.projects.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.projects.details(), id] as const,
  },
  // Auth queries
  auth: {
    me: ['auth', 'me'] as const,
    permissions: ['auth', 'permissions'] as const,
  },
} as const;

// API functions (these would integrate with the actual API client)
const api = {
  // User queries
  async getUser(params: GetUserQueryParams): Promise<User> {
    const response = await fetch(`/api/users/${params.id}`);
    if (!response.ok) throw new Error('Failed to fetch user');
    return response.json();
  },

  async getUsers(params: GetUsersQueryParams): Promise<{ users: User[]; total: number; page: number; limit: number }> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.role) searchParams.append('role', params.role);
    if (params.search) searchParams.append('search', params.search);

    const response = await fetch(`/api/users?${searchParams}`);
    if (!response.ok) throw new Error('Failed to fetch users');
    return response.json();
  },

  // Project queries
  async getProject(params: GetProjectQueryParams): Promise<Project> {
    const response = await fetch(`/api/projects/${params.id}`);
    if (!response.ok) throw new Error('Failed to fetch project');
    return response.json();
  },

  async getProjects(params: GetProjectsQueryParams): Promise<{ projects: Project[]; total: number; page: number; limit: number }> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.status) searchParams.append('status', params.status);
    if (params.difficulty) searchParams.append('difficulty', params.difficulty);
    if (params.authorId) searchParams.append('authorId', params.authorId);
    if (params.search) searchParams.append('search', params.search);

    const response = await fetch(`/api/projects?${searchParams}`);
    if (!response.ok) throw new Error('Failed to fetch projects');
    return response.json();
  },

  // Auth queries
  async getCurrentUser(): Promise<User> {
    const response = await fetch('/api/auth/me');
    if (!response.ok) throw new Error('Failed to fetch current user');
    return response.json();
  },

  async getUserPermissions(): Promise<string[]> {
    const response = await fetch('/api/auth/permissions');
    if (!response.ok) throw new Error('Failed to fetch permissions');
    return response.json();
  },
};

// Query hooks
export function useUser(params: GetUserQueryParams, enabled = true) {
  return useQuery({
    queryKey: queryKeys.users.detail(params.id),
    queryFn: () => api.getUser(params),
    enabled: enabled && !!params.id,
  });
}

export function useUsers(params: GetUsersQueryParams = {}) {
  return useQuery({
    queryKey: queryKeys.users.list(params),
    queryFn: () => api.getUsers(params),
    placeholderData: (previousData) => previousData,
  });
}

export function useProject(params: GetProjectQueryParams, enabled = true) {
  return useQuery({
    queryKey: queryKeys.projects.detail(params.id),
    queryFn: () => api.getProject(params),
    enabled: enabled && !!params.id,
  });
}

export function useProjects(params: GetProjectsQueryParams = {}) {
  return useQuery({
    queryKey: queryKeys.projects.list(params),
    queryFn: () => api.getProjects(params),
    placeholderData: (previousData) => previousData,
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: api.getCurrentUser,
    staleTime: Infinity, // Don't refetch until manually invalidated
  });
}

export function useUserPermissions() {
  return useQuery({
    queryKey: queryKeys.auth.permissions,
    queryFn: api.getUserPermissions,
    staleTime: Infinity, // Don't refetch until manually invalidated
  });
}

// Mutation hooks with automatic cache invalidation
export function useInvalidateQueries() {
  const queryClient = useQueryClient();

  return {
    // User cache invalidation
    invalidateUser: (userId: string) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.detail(userId) });
    },
    invalidateUsers: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.lists() });
    },
    invalidateAllUsers: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },

    // Project cache invalidation
    invalidateProject: (projectId: string) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(projectId) });
    },
    invalidateProjects: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.lists() });
    },
    invalidateAllProjects: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
    },

    // Auth cache invalidation
    invalidateAuth: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me });
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.permissions });
    },

    // Global invalidation
    invalidateAll: () => {
      queryClient.invalidateQueries();
    },
  };
}

// Optimistic update helpers
export function useOptimisticUpdates() {
  const queryClient = useQueryClient();

  return {
    // Optimistic user update
    updateUserOptimistically: (userId: string, updates: Partial<User>) => {
      queryClient.setQueryData(queryKeys.users.detail(userId), (old: User | undefined) => {
        if (!old) return old;
        return { ...old, ...updates, updatedAt: new Date().toISOString() };
      });
    },

    // Optimistic project update
    updateProjectOptimistically: (projectId: string, updates: Partial<Project>) => {
      queryClient.setQueryData(queryKeys.projects.detail(projectId), (old: Project | undefined) => {
        if (!old) return old;
        return { ...old, ...updates, updatedAt: new Date().toISOString() };
      });
    },

    // Rollback helper
    rollbackQuery: (queryKey: any) => {
      queryClient.invalidateQueries({ queryKey });
    },
  };
}

// React Query provider component
export { QueryClientProvider, ReactQueryDevtools };

// Export API for direct usage
export { api };

// Type exports
export type { 
  User, 
  Project, 
  GetUserQueryParams, 
  GetUsersQueryParams,
  GetProjectQueryParams,
  GetProjectsQueryParams
} from '../types';