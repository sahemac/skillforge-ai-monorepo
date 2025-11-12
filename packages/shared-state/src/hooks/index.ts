/**
 * React hooks for CQRS state management
 * Provides convenient hooks for both commands and queries
 */

import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import { useCallback } from 'react';
import type { AppDispatch, AppRootState } from '../store';
import { 
  useInvalidateQueries, 
  useOptimisticUpdates 
} from '../queries';
import {
  loginCommand,
  logoutCommand,
  refreshTokenCommand,
} from '../store/slices/authSlice';
import {
  createUserCommand,
  updateUserCommand,
  deleteUserCommand,
  activateUserCommand,
  deactivateUserCommand,
} from '../store/slices/usersSlice';
import {
  createProjectCommand,
  updateProjectCommand,
  deleteProjectCommand,
  publishProjectCommand,
  archiveProjectCommand,
  duplicateProjectCommand,
} from '../store/slices/projectsSlice';

// Typed hooks for Redux
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<AppRootState> = useSelector;

// Auth hooks
export function useAuth() {
  const dispatch = useAppDispatch();
  const authState = useAppSelector((state) => state.auth);
  const { invalidateAuth } = useInvalidateQueries();

  const login = useCallback(
    async (credentials: { email: string; password: string; rememberMe?: boolean }) => {
      const result = await dispatch(loginCommand(credentials));
      if (loginCommand.fulfilled.match(result)) {
        invalidateAuth();
      }
      return result;
    },
    [dispatch, invalidateAuth]
  );

  const logout = useCallback(async () => {
    const result = await dispatch(logoutCommand());
    if (logoutCommand.fulfilled.match(result)) {
      invalidateAuth();
    }
    return result;
  }, [dispatch, invalidateAuth]);

  const refreshToken = useCallback(
    async (token: string) => {
      return dispatch(refreshTokenCommand(token));
    },
    [dispatch]
  );

  return {
    ...authState,
    login,
    logout,
    refreshToken,
  };
}

// User command hooks
export function useUserCommands() {
  const dispatch = useAppDispatch();
  const { invalidateUsers, invalidateUser } = useInvalidateQueries();
  const { updateUserOptimistically } = useOptimisticUpdates();

  const createUser = useCallback(
    async (userData: Parameters<typeof createUserCommand>[0]) => {
      const result = await dispatch(createUserCommand(userData));
      if (createUserCommand.fulfilled.match(result)) {
        invalidateUsers();
      }
      return result;
    },
    [dispatch, invalidateUsers]
  );

  const updateUser = useCallback(
    async (updates: Parameters<typeof updateUserCommand>[0]) => {
      // Optimistic update
      updateUserOptimistically(updates.id, updates.updates);
      
      const result = await dispatch(updateUserCommand(updates));
      if (updateUserCommand.fulfilled.match(result)) {
        invalidateUser(updates.id);
        invalidateUsers();
      }
      return result;
    },
    [dispatch, invalidateUser, invalidateUsers, updateUserOptimistically]
  );

  const deleteUser = useCallback(
    async (userId: string) => {
      const result = await dispatch(deleteUserCommand(userId));
      if (deleteUserCommand.fulfilled.match(result)) {
        invalidateUsers();
      }
      return result;
    },
    [dispatch, invalidateUsers]
  );

  const activateUser = useCallback(
    async (userId: string) => {
      const result = await dispatch(activateUserCommand(userId));
      if (activateUserCommand.fulfilled.match(result)) {
        invalidateUser(userId);
        invalidateUsers();
      }
      return result;
    },
    [dispatch, invalidateUser, invalidateUsers]
  );

  const deactivateUser = useCallback(
    async (userId: string) => {
      const result = await dispatch(deactivateUserCommand(userId));
      if (deactivateUserCommand.fulfilled.match(result)) {
        invalidateUser(userId);
        invalidateUsers();
      }
      return result;
    },
    [dispatch, invalidateUser, invalidateUsers]
  );

  return {
    createUser,
    updateUser,
    deleteUser,
    activateUser,
    deactivateUser,
  };
}

// Project command hooks
export function useProjectCommands() {
  const dispatch = useAppDispatch();
  const { invalidateProjects, invalidateProject } = useInvalidateQueries();
  const { updateProjectOptimistically } = useOptimisticUpdates();

  const createProject = useCallback(
    async (projectData: Parameters<typeof createProjectCommand>[0]) => {
      const result = await dispatch(createProjectCommand(projectData));
      if (createProjectCommand.fulfilled.match(result)) {
        invalidateProjects();
      }
      return result;
    },
    [dispatch, invalidateProjects]
  );

  const updateProject = useCallback(
    async (updates: Parameters<typeof updateProjectCommand>[0]) => {
      // Optimistic update
      updateProjectOptimistically(updates.id, updates.updates);
      
      const result = await dispatch(updateProjectCommand(updates));
      if (updateProjectCommand.fulfilled.match(result)) {
        invalidateProject(updates.id);
        invalidateProjects();
      }
      return result;
    },
    [dispatch, invalidateProject, invalidateProjects, updateProjectOptimistically]
  );

  const deleteProject = useCallback(
    async (projectId: string) => {
      const result = await dispatch(deleteProjectCommand(projectId));
      if (deleteProjectCommand.fulfilled.match(result)) {
        invalidateProjects();
      }
      return result;
    },
    [dispatch, invalidateProjects]
  );

  const publishProject = useCallback(
    async (projectId: string) => {
      // Optimistic update
      updateProjectOptimistically(projectId, { status: 'active' });
      
      const result = await dispatch(publishProjectCommand(projectId));
      if (publishProjectCommand.fulfilled.match(result)) {
        invalidateProject(projectId);
        invalidateProjects();
      }
      return result;
    },
    [dispatch, invalidateProject, invalidateProjects, updateProjectOptimistically]
  );

  const archiveProject = useCallback(
    async (projectId: string) => {
      // Optimistic update
      updateProjectOptimistically(projectId, { status: 'archived' });
      
      const result = await dispatch(archiveProjectCommand(projectId));
      if (archiveProjectCommand.fulfilled.match(result)) {
        invalidateProject(projectId);
        invalidateProjects();
      }
      return result;
    },
    [dispatch, invalidateProject, invalidateProjects, updateProjectOptimistically]
  );

  const duplicateProject = useCallback(
    async (params: { projectId: string; title?: string }) => {
      const result = await dispatch(duplicateProjectCommand(params));
      if (duplicateProjectCommand.fulfilled.match(result)) {
        invalidateProjects();
      }
      return result;
    },
    [dispatch, invalidateProjects]
  );

  return {
    createProject,
    updateProject,
    deleteProject,
    publishProject,
    archiveProject,
    duplicateProject,
  };
}

// Selector hooks for convenient state access
export function useAuthState() {
  return useAppSelector((state) => state.auth);
}

export function useUsersState() {
  return useAppSelector((state) => state.users);
}

export function useProjectsState() {
  return useAppSelector((state) => state.projects);
}

// Permission hooks
export function usePermissions() {
  const permissions = useAppSelector((state) => state.auth?.permissions || []);

  const hasPermission = useCallback(
    (permission: string) => permissions.includes(permission),
    [permissions]
  );

  const hasAnyPermission = useCallback(
    (perms: string[]) => perms.some((perm) => permissions.includes(perm)),
    [permissions]
  );

  const hasAllPermissions = useCallback(
    (perms: string[]) => perms.every((perm) => permissions.includes(perm)),
    [permissions]
  );

  return {
    permissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };
}

// Loading state hooks
export function useLoadingStates() {
  const usersLoading = useAppSelector((state) => state.users?.loading || false);
  const projectsLoading = useAppSelector((state) => state.projects?.loading || false);

  return {
    usersLoading,
    projectsLoading,
    isAnyLoading: usersLoading || projectsLoading,
  };
}

// Error state hooks
export function useErrorStates() {
  const usersError = useAppSelector((state) => state.users?.error || null);
  const projectsError = useAppSelector((state) => state.projects?.error || null);

  return {
    usersError,
    projectsError,
    hasErrors: !!(usersError || projectsError),
    errors: [usersError, projectsError].filter(Boolean),
  };
}

// Combined hook for complete CQRS functionality
export function useCQRS() {
  const auth = useAuth();
  const userCommands = useUserCommands();
  const projectCommands = useProjectCommands();
  const permissions = usePermissions();
  const loadingStates = useLoadingStates();
  const errorStates = useErrorStates();

  return {
    // Authentication
    auth,
    permissions,
    
    // Commands
    commands: {
      users: userCommands,
      projects: projectCommands,
    },
    
    // State
    loading: loadingStates,
    errors: errorStates,
  };
}