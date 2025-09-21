/**
 * React hooks for EventBus integration
 * Provides convenient React hooks for event handling
 */

import { useEffect, useCallback, useRef } from 'react';
import { EventBus, EventUtils } from './EventBus';
import type { DomainEvent } from '../types';

type EventHandler<T = any> = (event: DomainEvent<T>) => void;

/**
 * Hook to listen to events from the EventBus
 */
export function useEventListener<T = any>(
  eventType: string,
  handler: EventHandler<T>,
  deps: React.DependencyList = []
): void {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    const wrappedHandler = (event: DomainEvent<T>) => {
      handlerRef.current(event);
    };

    const unsubscribe = EventBus.on(eventType as any, wrappedHandler);
    return unsubscribe;
  }, [eventType, ...deps]);
}

/**
 * Hook to emit events to the EventBus
 */
export function useEventEmitter() {
  return useCallback((eventType: string, payload: any, source?: string) => {
    EventBus.emit(eventType as any, payload, source);
  }, []);
}

/**
 * Hook for user-related events
 */
export function useUserEvents() {
  const emit = useEventEmitter();

  return {
    onUserCreated: useCallback((handler: EventHandler) => {
      return EventBus.on('user.created', handler);
    }, []),

    onUserUpdated: useCallback((handler: EventHandler) => {
      return EventBus.on('user.updated', handler);
    }, []),

    onUserDeleted: useCallback((handler: EventHandler<string>) => {
      return EventBus.on('user.deleted', handler);
    }, []),

    emitUserCreated: useCallback((user: any, source?: string) => {
      EventUtils.userCreated(user, source);
    }, []),

    emitUserUpdated: useCallback((user: any, source?: string) => {
      EventUtils.userUpdated(user, source);
    }, []),

    emitUserDeleted: useCallback((userId: string, source?: string) => {
      EventUtils.userDeleted(userId, source);
    }, []),
  };
}

/**
 * Hook for project-related events
 */
export function useProjectEvents() {
  return {
    onProjectCreated: useCallback((handler: EventHandler) => {
      return EventBus.on('project.created', handler);
    }, []),

    onProjectUpdated: useCallback((handler: EventHandler) => {
      return EventBus.on('project.updated', handler);
    }, []),

    onProjectDeleted: useCallback((handler: EventHandler<string>) => {
      return EventBus.on('project.deleted', handler);
    }, []),

    emitProjectCreated: useCallback((project: any, source?: string) => {
      EventUtils.projectCreated(project, source);
    }, []),

    emitProjectUpdated: useCallback((project: any, source?: string) => {
      EventUtils.projectUpdated(project, source);
    }, []),

    emitProjectDeleted: useCallback((projectId: string, source?: string) => {
      EventUtils.projectDeleted(projectId, source);
    }, []),
  };
}

/**
 * Hook for authentication events
 */
export function useAuthEvents() {
  return {
    onAuthenticated: useCallback((handler: EventHandler) => {
      return EventBus.on('auth.authenticated', handler);
    }, []),

    onLoggedOut: useCallback((handler: EventHandler<void>) => {
      return EventBus.on('auth.logged_out', handler);
    }, []),

    emitAuthenticated: useCallback((authState: any, source?: string) => {
      EventUtils.authenticated(authState, source);
    }, []),

    emitLoggedOut: useCallback((source?: string) => {
      EventUtils.loggedOut(source);
    }, []),
  };
}

/**
 * Hook for navigation events
 */
export function useNavigationEvents() {
  return {
    onNavigationChange: useCallback((handler: EventHandler<{ route: string; params?: Record<string, any> }>) => {
      return EventBus.on('navigation.change', handler);
    }, []),

    emitNavigate: useCallback((route: string, params?: Record<string, any>, source?: string) => {
      EventUtils.navigate(route, params, source);
    }, []),
  };
}

/**
 * Hook for UI events (notifications, modals, etc.)
 */
export function useUIEvents() {
  return {
    onNotificationShow: useCallback((handler: EventHandler<{ type: 'success' | 'error' | 'warning' | 'info'; message: string; duration?: number }>) => {
      return EventBus.on('notification.show', handler);
    }, []),

    onToastShow: useCallback((handler: EventHandler<{ message: string; type?: 'success' | 'error' | 'warning' | 'info' }>) => {
      return EventBus.on('toast.show', handler);
    }, []),

    onModalOpen: useCallback((handler: EventHandler<{ id: string; component: string; props?: any }>) => {
      return EventBus.on('modal.open', handler);
    }, []),

    onModalClose: useCallback((handler: EventHandler<{ id: string }>) => {
      return EventBus.on('modal.close', handler);
    }, []),

    emitNotification: useCallback((message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', source?: string) => {
      EventUtils.showNotification(message, type, source);
    }, []),

    emitToast: useCallback((message: string, type?: 'success' | 'error' | 'warning' | 'info', source?: string) => {
      EventUtils.showToast(message, type, source);
    }, []),

    emitOpenModal: useCallback((id: string, component: string, props?: any, source?: string) => {
      EventUtils.openModal(id, component, props, source);
    }, []),

    emitCloseModal: useCallback((id: string, source?: string) => {
      EventUtils.closeModal(id, source);
    }, []),
  };
}

/**
 * Hook for error events
 */
export function useErrorEvents() {
  return {
    onNetworkError: useCallback((handler: EventHandler<{ error: Error; context: string }>) => {
      return EventBus.on('error.network', handler);
    }, []),

    onValidationError: useCallback((handler: EventHandler<{ field: string; message: string }>) => {
      return EventBus.on('error.validation', handler);
    }, []),

    onPermissionError: useCallback((handler: EventHandler<{ action: string; resource: string }>) => {
      return EventBus.on('error.permission', handler);
    }, []),

    emitNetworkError: useCallback((error: Error, context: string, source?: string) => {
      EventUtils.networkError(error, context, source);
    }, []),

    emitValidationError: useCallback((field: string, message: string, source?: string) => {
      EventUtils.validationError(field, message, source);
    }, []),

    emitPermissionError: useCallback((action: string, resource: string, source?: string) => {
      EventUtils.permissionError(action, resource, source);
    }, []),
  };
}

/**
 * Master hook that provides access to all event types
 */
export function useEvents() {
  const userEvents = useUserEvents();
  const projectEvents = useProjectEvents();
  const authEvents = useAuthEvents();
  const navigationEvents = useNavigationEvents();
  const uiEvents = useUIEvents();
  const errorEvents = useErrorEvents();

  return {
    users: userEvents,
    projects: projectEvents,
    auth: authEvents,
    navigation: navigationEvents,
    ui: uiEvents,
    errors: errorEvents,
    
    // Direct access to EventBus for custom events
    on: EventBus.on.bind(EventBus),
    emit: EventBus.emit.bind(EventBus),
    off: EventBus.off.bind(EventBus),
    
    // Debugging helpers
    getHistory: EventBus.getEventHistory.bind(EventBus),
    getListenerCount: EventBus.getListenerCount.bind(EventBus),
    clearHistory: EventBus.clearHistory.bind(EventBus),
  };
}

/**
 * Hook for debugging events
 */
export function useEventDebugger() {
  useEventListener('*', (event) => {
    console.log('[EventBus Debug]', event);
  });

  return {
    getHistory: () => EventBus.getEventHistory(),
    getListenerCount: (type?: string) => EventBus.getListenerCount(type as any),
    getRegisteredTypes: () => EventBus.getRegisteredEventTypes(),
    clearHistory: () => EventBus.clearHistory(),
  };
}