/**
 * Preact Signals for fine-grained reactivity
 * Provides reactive state management with minimal re-renders
 */

import { signal, computed, effect, batch } from '@preact/signals-react';
import type { User, Project, AuthState } from '../types';

// Core reactive signals for global state
export const authSignal = signal<AuthState>({
  isAuthenticated: false,
  user: null,
  token: null,
  refreshToken: null,
  expiresAt: null,
  permissions: []
});

export const currentUserSignal = signal<User | null>(null);
export const usersSignal = signal<Record<string, User>>({});
export const projectsSignal = signal<Record<string, Project>>({});

// UI state signals
export const loadingSignal = signal<{
  auth: boolean;
  users: boolean;
  projects: boolean;
  global: boolean;
}>({
  auth: false,
  users: false,
  projects: false,
  global: false
});

export const errorsSignal = signal<{
  auth: string | null;
  users: string | null;
  projects: string | null;
  global: string | null;
}>({
  auth: null,
  users: null,
  projects: null,
  global: null
});

// Navigation signals
export const routeSignal = signal<{
  path: string;
  params: Record<string, any>;
  query: Record<string, any>;
}>({
  path: '/',
  params: {},
  query: {}
});

// UI component signals
export const modalSignal = signal<{
  isOpen: boolean;
  component: string | null;
  props: any;
  id: string | null;
}>({
  isOpen: false,
  component: null,
  props: null,
  id: null
});

export const notificationSignal = signal<{
  visible: boolean;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration: number;
}>({
  visible: false,
  message: '',
  type: 'info',
  duration: 5000
});

export const toastSignal = signal<Array<{
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timestamp: number;
}>>([]);

// Computed signals for derived state
export const isLoggedInSignal = computed(() => authSignal.value.isAuthenticated);

export const currentUserRoleSignal = computed(() => 
  authSignal.value.user?.role || null
);

export const currentUserPermissionsSignal = computed(() => 
  authSignal.value.permissions || []
);

export const allUsersSignal = computed(() => 
  Object.values(usersSignal.value)
);

export const allProjectsSignal = computed(() => 
  Object.values(projectsSignal.value)
);

export const activeProjectsSignal = computed(() => 
  allProjectsSignal.value.filter(project => project.status === 'active')
);

export const userProjectsSignal = computed(() => {
  const currentUserId = authSignal.value.user?.id;
  if (!currentUserId) return [];
  
  return allProjectsSignal.value.filter(project => project.authorId === currentUserId);
});

export const isLoadingAnySignal = computed(() => {
  const loading = loadingSignal.value;
  return loading.auth || loading.users || loading.projects || loading.global;
});

export const hasErrorsSignal = computed(() => {
  const errors = errorsSignal.value;
  return !!(errors.auth || errors.users || errors.projects || errors.global);
});

export const errorMessagesSignal = computed(() => {
  const errors = errorsSignal.value;
  return [errors.auth, errors.users, errors.projects, errors.global].filter(Boolean);
});

// Signal mutation helpers
export const signalActions = {
  // Auth actions
  setAuth: (authState: Partial<AuthState>) => {
    authSignal.value = { ...authSignal.value, ...authState };
  },

  setCurrentUser: (user: User | null) => {
    currentUserSignal.value = user;
    if (user) {
      authSignal.value = { ...authSignal.value, user };
    }
  },

  clearAuth: () => {
    batch(() => {
      authSignal.value = {
        isAuthenticated: false,
        user: null,
        token: null,
        refreshToken: null,
        expiresAt: null,
        permissions: []
      };
      currentUserSignal.value = null;
    });
  },

  // User actions
  setUsers: (users: User[]) => {
    const userMap = users.reduce((acc, user) => {
      acc[user.id] = user;
      return acc;
    }, {} as Record<string, User>);
    usersSignal.value = userMap;
  },

  addUser: (user: User) => {
    usersSignal.value = { ...usersSignal.value, [user.id]: user };
  },

  updateUser: (userId: string, updates: Partial<User>) => {
    const currentUser = usersSignal.value[userId];
    if (currentUser) {
      usersSignal.value = {
        ...usersSignal.value,
        [userId]: { ...currentUser, ...updates }
      };
    }
  },

  removeUser: (userId: string) => {
    const newUsers = { ...usersSignal.value };
    delete newUsers[userId];
    usersSignal.value = newUsers;
  },

  // Project actions
  setProjects: (projects: Project[]) => {
    const projectMap = projects.reduce((acc, project) => {
      acc[project.id] = project;
      return acc;
    }, {} as Record<string, Project>);
    projectsSignal.value = projectMap;
  },

  addProject: (project: Project) => {
    projectsSignal.value = { ...projectsSignal.value, [project.id]: project };
  },

  updateProject: (projectId: string, updates: Partial<Project>) => {
    const currentProject = projectsSignal.value[projectId];
    if (currentProject) {
      projectsSignal.value = {
        ...projectsSignal.value,
        [projectId]: { ...currentProject, ...updates }
      };
    }
  },

  removeProject: (projectId: string) => {
    const newProjects = { ...projectsSignal.value };
    delete newProjects[projectId];
    projectsSignal.value = newProjects;
  },

  // Loading actions
  setLoading: (key: keyof typeof loadingSignal.value, loading: boolean) => {
    loadingSignal.value = { ...loadingSignal.value, [key]: loading };
  },

  // Error actions
  setError: (key: keyof typeof errorsSignal.value, error: string | null) => {
    errorsSignal.value = { ...errorsSignal.value, [key]: error };
  },

  clearErrors: () => {
    errorsSignal.value = {
      auth: null,
      users: null,
      projects: null,
      global: null
    };
  },

  // Navigation actions
  setRoute: (path: string, params: Record<string, any> = {}, query: Record<string, any> = {}) => {
    routeSignal.value = { path, params, query };
  },

  // Modal actions
  openModal: (component: string, props: any = {}, id: string = Date.now().toString()) => {
    modalSignal.value = {
      isOpen: true,
      component,
      props,
      id
    };
  },

  closeModal: () => {
    modalSignal.value = {
      isOpen: false,
      component: null,
      props: null,
      id: null
    };
  },

  // Notification actions
  showNotification: (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', duration = 5000) => {
    notificationSignal.value = {
      visible: true,
      message,
      type,
      duration
    };

    // Auto-hide notification
    setTimeout(() => {
      notificationSignal.value = { ...notificationSignal.value, visible: false };
    }, duration);
  },

  hideNotification: () => {
    notificationSignal.value = { ...notificationSignal.value, visible: false };
  },

  // Toast actions
  addToast: (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    const toast = {
      id: Date.now().toString(),
      message,
      type,
      timestamp: Date.now()
    };

    toastSignal.value = [...toastSignal.value, toast];

    // Auto-remove toast after 5 seconds
    setTimeout(() => {
      signalActions.removeToast(toast.id);
    }, 5000);
  },

  removeToast: (toastId: string) => {
    toastSignal.value = toastSignal.value.filter(toast => toast.id !== toastId);
  },

  clearToasts: () => {
    toastSignal.value = [];
  }
};

// Permission helper functions
export const signalPermissions = {
  hasPermission: computed(() => (permission: string) => {
    return currentUserPermissionsSignal.value.includes(permission);
  }),

  hasAnyPermission: computed(() => (permissions: string[]) => {
    const userPermissions = currentUserPermissionsSignal.value;
    return permissions.some(permission => userPermissions.includes(permission));
  }),

  hasAllPermissions: computed(() => (permissions: string[]) => {
    const userPermissions = currentUserPermissionsSignal.value;
    return permissions.every(permission => userPermissions.includes(permission));
  }),

  isAdmin: computed(() => currentUserRoleSignal.value === 'admin'),
  isCompany: computed(() => currentUserRoleSignal.value === 'company'),
  isLearner: computed(() => currentUserRoleSignal.value === 'learner'),
};

// Effect helpers for side effects
export const signalEffects = {
  // Watch auth changes
  watchAuth: (callback: (authState: AuthState) => void) => {
    return effect(() => {
      callback(authSignal.value);
    });
  },

  // Watch route changes
  watchRoute: (callback: (route: typeof routeSignal.value) => void) => {
    return effect(() => {
      callback(routeSignal.value);
    });
  },

  // Watch errors
  watchErrors: (callback: (hasErrors: boolean, errors: string[]) => void) => {
    return effect(() => {
      callback(hasErrorsSignal.value, errorMessagesSignal.value);
    });
  },

  // Watch loading state
  watchLoading: (callback: (isLoading: boolean) => void) => {
    return effect(() => {
      callback(isLoadingAnySignal.value);
    });
  }
};

// Debugging helpers
export const signalDebug = {
  logAllSignals: () => {
    console.group('[Signals Debug]');
    console.log('Auth:', authSignal.value);
    console.log('Current User:', currentUserSignal.value);
    console.log('Users:', usersSignal.value);
    console.log('Projects:', projectsSignal.value);
    console.log('Loading:', loadingSignal.value);
    console.log('Errors:', errorsSignal.value);
    console.log('Route:', routeSignal.value);
    console.log('Modal:', modalSignal.value);
    console.log('Notification:', notificationSignal.value);
    console.log('Toasts:', toastSignal.value);
    console.groupEnd();
  },

  subscribeToChanges: () => {
    effect(() => {
      console.log('[Signal Change] Auth:', authSignal.value);
    });

    effect(() => {
      console.log('[Signal Change] Users:', Object.keys(usersSignal.value));
    });

    effect(() => {
      console.log('[Signal Change] Projects:', Object.keys(projectsSignal.value));
    });

    effect(() => {
      console.log('[Signal Change] Route:', routeSignal.value.path);
    });
  }
};

// Export everything
export {
  signal,
  computed,
  effect,
  batch
} from '@preact/signals-react';