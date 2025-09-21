/**
 * Main entry point for @skillforge-ai/shared-state package
 * Exports all CQRS functionality for use across micro-frontends
 */

// Core types
export * from './types';

// Store (Commands - Write operations)
export { store, persistor } from './store';
export { default as authSlice } from './store/slices/authSlice';
export { default as usersSlice } from './store/slices/usersSlice';
export { default as projectsSlice } from './store/slices/projectsSlice';

// Queries (Read operations)
export * from './queries';

// Hooks
export * from './hooks';

// Providers
export { default as StateProvider } from './providers/StateProvider';

// EventBus
export { EventBus, EventUtils } from './eventbus/EventBus';
export * from './eventbus/useEventBus';

// Signals
export * from './signals';
export * from './signals/useSignals';

// Commands exports for direct access
export {
  loginCommand,
  logoutCommand,
  refreshTokenCommand,
  setAuthenticated,
  setUser,
  updateUserProfile,
  setPermissions,
  clearAuth,
} from './store/slices/authSlice';

export {
  createUserCommand,
  updateUserCommand,
  deleteUserCommand,
  activateUserCommand,
  deactivateUserCommand,
  addUser,
  addUsers,
  updateUser,
  removeUser,
  clearUsers,
  selectAllUsers,
  selectUserById,
  selectUserIds,
  selectUserEntities,
  selectUsersTotal,
} from './store/slices/usersSlice';

export {
  createProjectCommand,
  updateProjectCommand,
  deleteProjectCommand,
  publishProjectCommand,
  archiveProjectCommand,
  duplicateProjectCommand,
  addProject,
  addProjects,
  updateProject,
  removeProject,
  clearProjects,
  optimisticUpdateStatus,
  selectAllProjects,
  selectProjectById,
  selectProjectIds,
  selectProjectEntities,
  selectProjectsTotal,
} from './store/slices/projectsSlice';

// Re-export React Query essentials
export type {
  UseQueryResult,
  UseMutationResult,
  QueryKey,
} from '@tanstack/react-query';

export {
  useQuery,
  useMutation,
  useQueryClient,
  useIsFetching,
  useIsMutating,
} from '@tanstack/react-query';

// Type guards and utilities
export function isValidUser(user: any): user is import('./types').User {
  return (
    user &&
    typeof user === 'object' &&
    typeof user.id === 'string' &&
    typeof user.email === 'string' &&
    typeof user.username === 'string' &&
    ['learner', 'company', 'admin'].includes(user.role)
  );
}

export function isValidProject(project: any): project is import('./types').Project {
  return (
    project &&
    typeof project === 'object' &&
    typeof project.id === 'string' &&
    typeof project.title === 'string' &&
    ['draft', 'active', 'completed', 'archived'].includes(project.status)
  );
}

// Constants
export const USER_ROLES = ['learner', 'company', 'admin'] as const;
export const PROJECT_STATUSES = ['draft', 'active', 'completed', 'archived'] as const;
export const PROJECT_DIFFICULTIES = ['beginner', 'intermediate', 'advanced'] as const;

// Default configurations
export const DEFAULT_PAGINATION = {
  page: 1,
  limit: 20,
} as const;

export const CACHE_TIMES = {
  short: 1 * 60 * 1000, // 1 minute
  medium: 5 * 60 * 1000, // 5 minutes
  long: 10 * 60 * 1000, // 10 minutes
  infinity: Infinity,
} as const;