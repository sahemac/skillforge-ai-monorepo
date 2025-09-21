/**
 * React hooks for Preact Signals integration
 * Provides convenient React hooks for reactive state management
 */

import { useSignal, useComputed, useSignalEffect } from '@preact/signals-react';
import { useCallback } from 'react';
import {
  authSignal,
  currentUserSignal,
  usersSignal,
  projectsSignal,
  loadingSignal,
  errorsSignal,
  routeSignal,
  modalSignal,
  notificationSignal,
  toastSignal,
  isLoggedInSignal,
  currentUserRoleSignal,
  currentUserPermissionsSignal,
  allUsersSignal,
  allProjectsSignal,
  activeProjectsSignal,
  userProjectsSignal,
  isLoadingAnySignal,
  hasErrorsSignal,
  errorMessagesSignal,
  signalActions,
  signalPermissions,
  signalEffects
} from './index';
import type { User, Project, AuthState } from '../types';

/**
 * Hook for authentication state
 */
export function useAuthSignal() {
  return {
    // Read-only access to auth state
    auth: authSignal.value,
    isLoggedIn: isLoggedInSignal.value,
    currentUser: currentUserSignal.value,
    userRole: currentUserRoleSignal.value,
    permissions: currentUserPermissionsSignal.value,
    
    // Actions
    setAuth: signalActions.setAuth,
    setCurrentUser: signalActions.setCurrentUser,
    clearAuth: signalActions.clearAuth,
    
    // Permission helpers
    hasPermission: signalPermissions.hasPermission.value,
    hasAnyPermission: signalPermissions.hasAnyPermission.value,
    hasAllPermissions: signalPermissions.hasAllPermissions.value,
    isAdmin: signalPermissions.isAdmin.value,
    isCompany: signalPermissions.isCompany.value,
    isLearner: signalPermissions.isLearner.value,
  };
}

/**
 * Hook for users state
 */
export function useUsersSignal() {
  return {
    // Read-only access to users state
    users: usersSignal.value,
    allUsers: allUsersSignal.value,
    
    // Actions
    setUsers: signalActions.setUsers,
    addUser: signalActions.addUser,
    updateUser: signalActions.updateUser,
    removeUser: signalActions.removeUser,
    
    // Helpers
    getUserById: useCallback((id: string) => usersSignal.value[id], []),
    getUsersByRole: useCallback((role: User['role']) => 
      allUsersSignal.value.filter(user => user.role === role), []),
  };
}

/**
 * Hook for projects state
 */
export function useProjectsSignal() {
  return {
    // Read-only access to projects state
    projects: projectsSignal.value,
    allProjects: allProjectsSignal.value,
    activeProjects: activeProjectsSignal.value,
    userProjects: userProjectsSignal.value,
    
    // Actions
    setProjects: signalActions.setProjects,
    addProject: signalActions.addProject,
    updateProject: signalActions.updateProject,
    removeProject: signalActions.removeProject,
    
    // Helpers
    getProjectById: useCallback((id: string) => projectsSignal.value[id], []),
    getProjectsByStatus: useCallback((status: Project['status']) => 
      allProjectsSignal.value.filter(project => project.status === status), []),
    getProjectsByDifficulty: useCallback((difficulty: Project['difficulty']) => 
      allProjectsSignal.value.filter(project => project.difficulty === difficulty), []),
  };
}

/**
 * Hook for loading state
 */
export function useLoadingSignal() {
  return {
    // Read-only access to loading state
    loading: loadingSignal.value,
    isLoadingAny: isLoadingAnySignal.value,
    
    // Actions
    setLoading: signalActions.setLoading,
    
    // Specific loading states
    isAuthLoading: loadingSignal.value.auth,
    isUsersLoading: loadingSignal.value.users,
    isProjectsLoading: loadingSignal.value.projects,
    isGlobalLoading: loadingSignal.value.global,
  };
}

/**
 * Hook for error state
 */
export function useErrorsSignal() {
  return {
    // Read-only access to error state
    errors: errorsSignal.value,
    hasErrors: hasErrorsSignal.value,
    errorMessages: errorMessagesSignal.value,
    
    // Actions
    setError: signalActions.setError,
    clearErrors: signalActions.clearErrors,
    
    // Specific error states
    authError: errorsSignal.value.auth,
    usersError: errorsSignal.value.users,
    projectsError: errorsSignal.value.projects,
    globalError: errorsSignal.value.global,
  };
}

/**
 * Hook for navigation state
 */
export function useNavigationSignal() {
  return {
    // Read-only access to route state
    route: routeSignal.value,
    currentPath: routeSignal.value.path,
    routeParams: routeSignal.value.params,
    queryParams: routeSignal.value.query,
    
    // Actions
    setRoute: signalActions.setRoute,
    
    // Navigation helpers
    navigate: useCallback((path: string, params?: Record<string, any>, query?: Record<string, any>) => {
      signalActions.setRoute(path, params, query);
    }, []),
  };
}

/**
 * Hook for modal state
 */
export function useModalSignal() {
  return {
    // Read-only access to modal state
    modal: modalSignal.value,
    isModalOpen: modalSignal.value.isOpen,
    modalComponent: modalSignal.value.component,
    modalProps: modalSignal.value.props,
    modalId: modalSignal.value.id,
    
    // Actions
    openModal: signalActions.openModal,
    closeModal: signalActions.closeModal,
  };
}

/**
 * Hook for notification state
 */
export function useNotificationSignal() {
  return {
    // Read-only access to notification state
    notification: notificationSignal.value,
    isNotificationVisible: notificationSignal.value.visible,
    notificationMessage: notificationSignal.value.message,
    notificationType: notificationSignal.value.type,
    
    // Actions
    showNotification: signalActions.showNotification,
    hideNotification: signalActions.hideNotification,
  };
}

/**
 * Hook for toast state
 */
export function useToastSignal() {
  return {
    // Read-only access to toast state
    toasts: toastSignal.value,
    toastCount: toastSignal.value.length,
    
    // Actions
    addToast: signalActions.addToast,
    removeToast: signalActions.removeToast,
    clearToasts: signalActions.clearToasts,
  };
}

/**
 * Hook for UI state (combines modal, notification, and toast)
 */
export function useUISignal() {
  const modal = useModalSignal();
  const notification = useNotificationSignal();
  const toast = useToastSignal();
  
  return {
    modal,
    notification,
    toast,
    
    // Convenient UI actions
    showSuccess: useCallback((message: string) => {
      signalActions.showNotification(message, 'success');
      signalActions.addToast(message, 'success');
    }, []),
    
    showError: useCallback((message: string) => {
      signalActions.showNotification(message, 'error');
      signalActions.addToast(message, 'error');
    }, []),
    
    showWarning: useCallback((message: string) => {
      signalActions.showNotification(message, 'warning');
      signalActions.addToast(message, 'warning');
    }, []),
    
    showInfo: useCallback((message: string) => {
      signalActions.showNotification(message, 'info');
      signalActions.addToast(message, 'info');
    }, []),
  };
}

/**
 * Master hook that provides access to all signals
 */
export function useAllSignals() {
  const auth = useAuthSignal();
  const users = useUsersSignal();
  const projects = useProjectsSignal();
  const loading = useLoadingSignal();
  const errors = useErrorsSignal();
  const navigation = useNavigationSignal();
  const ui = useUISignal();
  
  return {
    auth,
    users,
    projects,
    loading,
    errors,
    navigation,
    ui,
  };
}

/**
 * Hook for watching signal changes with effects
 */
export function useSignalWatcher() {
  return {
    watchAuth: useCallback((callback: (authState: AuthState) => void) => {
      return signalEffects.watchAuth(callback);
    }, []),
    
    watchRoute: useCallback((callback: (route: typeof routeSignal.value) => void) => {
      return signalEffects.watchRoute(callback);
    }, []),
    
    watchErrors: useCallback((callback: (hasErrors: boolean, errors: string[]) => void) => {
      return signalEffects.watchErrors(callback);
    }, []),
    
    watchLoading: useCallback((callback: (isLoading: boolean) => void) => {
      return signalEffects.watchLoading(callback);
    }, []),
  };
}

/**
 * Hook for creating custom signals in components
 */
export function useCustomSignal<T>(initialValue: T) {
  const customSignal = useSignal(initialValue);
  
  return {
    value: customSignal.value,
    setValue: useCallback((newValue: T | ((prev: T) => T)) => {
      if (typeof newValue === 'function') {
        customSignal.value = (newValue as (prev: T) => T)(customSignal.value);
      } else {
        customSignal.value = newValue;
      }
    }, [customSignal]),
    signal: customSignal,
  };
}

/**
 * Hook for creating computed values based on multiple signals
 */
export function useComputedSignal<T>(computeFn: () => T) {
  return useComputed(computeFn);
}

/**
 * Hook for side effects based on signal changes
 */
export function useSignalSideEffect(effectFn: () => void | (() => void), deps: any[] = []) {
  useSignalEffect(() => {
    return effectFn();
  });
}