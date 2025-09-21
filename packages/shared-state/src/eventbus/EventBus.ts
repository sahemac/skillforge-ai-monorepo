/**
 * EventBus for micro-frontend communication
 * Enables decoupled communication between different micro-frontend apps
 */

import mitt, { Emitter } from 'mitt';
import type { DomainEvent, SystemEvent } from '../types';

// Event bus type with all possible events
type EventMap = {
  // System events
  'user.created': DomainEvent<any>;
  'user.updated': DomainEvent<any>;
  'user.deleted': DomainEvent<string>;
  'project.created': DomainEvent<any>;
  'project.updated': DomainEvent<any>;
  'project.deleted': DomainEvent<string>;
  'auth.authenticated': DomainEvent<any>;
  'auth.logged_out': DomainEvent<void>;
  
  // Navigation events
  'navigation.change': DomainEvent<{ route: string; params?: Record<string, any> }>;
  'navigation.back': DomainEvent<void>;
  'navigation.forward': DomainEvent<void>;
  
  // UI events
  'modal.open': DomainEvent<{ id: string; component: string; props?: any }>;
  'modal.close': DomainEvent<{ id: string }>;
  'notification.show': DomainEvent<{ type: 'success' | 'error' | 'warning' | 'info'; message: string; duration?: number }>;
  'toast.show': DomainEvent<{ message: string; type?: 'success' | 'error' | 'warning' | 'info' }>;
  
  // Data events
  'data.refresh': DomainEvent<{ entity: string; id?: string }>;
  'data.sync': DomainEvent<{ entity: string; data: any }>;
  
  // Error events
  'error.network': DomainEvent<{ error: Error; context: string }>;
  'error.validation': DomainEvent<{ field: string; message: string }>;
  'error.permission': DomainEvent<{ action: string; resource: string }>;
  
  // Wildcard for any event
  '*': DomainEvent<any>;
};

class EventBusClass {
  private emitter: Emitter<EventMap>;
  private listeners: Map<string, Set<Function>> = new Map();
  private eventHistory: DomainEvent<any>[] = [];
  private maxHistorySize = 100;

  constructor() {
    this.emitter = mitt<EventMap>();
    
    // Store all events in history for debugging
    this.emitter.on('*', (event: DomainEvent<any>) => {
      this.addToHistory(event);
    });
  }

  /**
   * Emit a domain event to all listeners
   */
  emit<T extends keyof EventMap>(type: T, payload: EventMap[T]['payload'], source = 'unknown'): void {
    const event: DomainEvent = {
      type: type as string,
      payload,
      timestamp: Date.now(),
      source,
      correlationId: this.generateCorrelationId(),
    };

    console.debug(`[EventBus] Emitting event: ${type}`, event);
    this.emitter.emit(type, event);
  }

  /**
   * Listen to a specific event type
   */
  on<T extends keyof EventMap>(type: T, handler: (event: EventMap[T]) => void): () => void {
    console.debug(`[EventBus] Registering listener for: ${type}`);
    
    this.emitter.on(type, handler);
    
    // Track listeners for debugging
    if (!this.listeners.has(type as string)) {
      this.listeners.set(type as string, new Set());
    }
    this.listeners.get(type as string)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.emitter.off(type, handler);
      this.listeners.get(type as string)?.delete(handler);
    };
  }

  /**
   * Listen to an event once
   */
  once<T extends keyof EventMap>(type: T, handler: (event: EventMap[T]) => void): () => void {
    const wrappedHandler = (event: EventMap[T]) => {
      handler(event);
      this.emitter.off(type, wrappedHandler);
    };

    this.emitter.on(type, wrappedHandler);
    
    return () => {
      this.emitter.off(type, wrappedHandler);
    };
  }

  /**
   * Remove all listeners for a specific event type
   */
  off<T extends keyof EventMap>(type?: T): void {
    if (type) {
      this.emitter.off(type);
      this.listeners.delete(type as string);
    } else {
      this.emitter.all.clear();
      this.listeners.clear();
    }
  }

  /**
   * Get the last N events from history
   */
  getEventHistory(limit = 10): DomainEvent<any>[] {
    return this.eventHistory.slice(-limit);
  }

  /**
   * Get current listener count for debugging
   */
  getListenerCount(type?: keyof EventMap): number {
    if (type) {
      return this.listeners.get(type as string)?.size || 0;
    }
    return Array.from(this.listeners.values()).reduce((sum, set) => sum + set.size, 0);
  }

  /**
   * Clear event history
   */
  clearHistory(): void {
    this.eventHistory = [];
  }

  /**
   * Get all registered event types
   */
  getRegisteredEventTypes(): string[] {
    return Array.from(this.listeners.keys());
  }

  private addToHistory(event: DomainEvent<any>): void {
    this.eventHistory.push(event);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Singleton instance
export const EventBus = new EventBusClass();

// Utility functions for common events
export const EventUtils = {
  // User events
  userCreated: (user: any, source = 'user-service') => 
    EventBus.emit('user.created', user, source),
  
  userUpdated: (user: any, source = 'user-service') => 
    EventBus.emit('user.updated', user, source),
  
  userDeleted: (userId: string, source = 'user-service') => 
    EventBus.emit('user.deleted', userId, source),

  // Project events
  projectCreated: (project: any, source = 'project-service') => 
    EventBus.emit('project.created', project, source),
  
  projectUpdated: (project: any, source = 'project-service') => 
    EventBus.emit('project.updated', project, source),
  
  projectDeleted: (projectId: string, source = 'project-service') => 
    EventBus.emit('project.deleted', projectId, source),

  // Auth events
  authenticated: (authState: any, source = 'auth-service') => 
    EventBus.emit('auth.authenticated', authState, source),
  
  loggedOut: (source = 'auth-service') => 
    EventBus.emit('auth.logged_out', undefined, source),

  // Navigation events
  navigate: (route: string, params?: Record<string, any>, source = 'shell') => 
    EventBus.emit('navigation.change', { route, params }, source),

  // UI events
  showNotification: (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', source = 'ui') => 
    EventBus.emit('notification.show', { type, message }, source),
  
  showToast: (message: string, type?: 'success' | 'error' | 'warning' | 'info', source = 'ui') => 
    EventBus.emit('toast.show', { message, type }, source),

  openModal: (id: string, component: string, props?: any, source = 'ui') => 
    EventBus.emit('modal.open', { id, component, props }, source),
  
  closeModal: (id: string, source = 'ui') => 
    EventBus.emit('modal.close', { id }, source),

  // Data events
  refreshData: (entity: string, id?: string, source = 'data-service') => 
    EventBus.emit('data.refresh', { entity, id }, source),

  // Error events
  networkError: (error: Error, context: string, source = 'api-client') => 
    EventBus.emit('error.network', { error, context }, source),
  
  validationError: (field: string, message: string, source = 'form') => 
    EventBus.emit('error.validation', { field, message }, source),
  
  permissionError: (action: string, resource: string, source = 'auth') => 
    EventBus.emit('error.permission', { action, resource }, source),
};

export default EventBus;