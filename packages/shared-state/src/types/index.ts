/**
 * Core types for CQRS state management system
 * Provides type definitions for commands, queries, and state management
 */

import { z } from 'zod';

// Base interfaces for CQRS pattern
export interface Command<TPayload = unknown> {
  readonly type: string;
  readonly payload: TPayload;
  readonly timestamp: number;
  readonly correlationId: string;
}

export interface Query<TParams = unknown, TResult = unknown> {
  readonly key: string;
  readonly params: TParams;
  readonly cacheTime?: number;
  readonly staleTime?: number;
}

export interface CommandResult<TData = unknown> {
  readonly success: boolean;
  readonly data?: TData;
  readonly error?: Error;
  readonly timestamp: number;
}

export interface QueryResult<TData = unknown> {
  readonly data: TData;
  readonly isLoading: boolean;
  readonly isError: boolean;
  readonly error: Error | null;
  readonly isSuccess: boolean;
  readonly refetch: () => Promise<TData>;
}

// Domain entities
export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  username: z.string().min(1),
  firstName: z.string().min(1),
  lastName: z.string().min(1),
  role: z.enum(['learner', 'company', 'admin']),
  isActive: z.boolean(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  profile: z.object({
    avatar: z.string().url().optional(),
    bio: z.string().optional(),
    skills: z.array(z.string()).default([]),
    preferences: z.record(z.unknown()).default({})
  }).optional()
});

export const ProjectSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1),
  description: z.string(),
  status: z.enum(['draft', 'active', 'completed', 'archived']),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']),
  estimatedDuration: z.number().positive(),
  skills: z.array(z.string()),
  authorId: z.string().uuid(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  metadata: z.record(z.unknown()).default({})
});

export const AuthStateSchema = z.object({
  isAuthenticated: z.boolean(),
  user: UserSchema.nullable(),
  token: z.string().nullable(),
  refreshToken: z.string().nullable(),
  expiresAt: z.number().nullable(),
  permissions: z.array(z.string()).default([])
});

// Type exports
export type User = z.infer<typeof UserSchema>;
export type Project = z.infer<typeof ProjectSchema>;
export type AuthState = z.infer<typeof AuthStateSchema>;

// State interfaces
export interface RootState {
  auth: AuthState;
  users: {
    entities: Record<string, User>;
    loading: boolean;
    error: string | null;
  };
  projects: {
    entities: Record<string, Project>;
    loading: boolean;
    error: string | null;
  };
}

// Command payload types
export interface LoginCommandPayload {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface CreateUserCommandPayload {
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  role: User['role'];
  password: string;
}

export interface UpdateUserCommandPayload {
  id: string;
  updates: Partial<Omit<User, 'id' | 'createdAt' | 'updatedAt'>>;
}

export interface CreateProjectCommandPayload {
  title: string;
  description: string;
  difficulty: Project['difficulty'];
  estimatedDuration: number;
  skills: string[];
}

export interface UpdateProjectCommandPayload {
  id: string;
  updates: Partial<Omit<Project, 'id' | 'authorId' | 'createdAt' | 'updatedAt'>>;
}

// Query parameter types
export interface GetUserQueryParams {
  id: string;
}

export interface GetUsersQueryParams {
  page?: number;
  limit?: number;
  role?: User['role'];
  search?: string;
}

export interface GetProjectQueryParams {
  id: string;
}

export interface GetProjectsQueryParams {
  page?: number;
  limit?: number;
  status?: Project['status'];
  difficulty?: Project['difficulty'];
  authorId?: string;
  search?: string;
}

// Event types for micro-frontend communication
export interface DomainEvent<TPayload = unknown> {
  readonly type: string;
  readonly payload: TPayload;
  readonly timestamp: number;
  readonly source: string;
  readonly correlationId: string;
}

export interface UserCreatedEvent extends DomainEvent<User> {
  readonly type: 'user.created';
}

export interface UserUpdatedEvent extends DomainEvent<User> {
  readonly type: 'user.updated';
}

export interface ProjectCreatedEvent extends DomainEvent<Project> {
  readonly type: 'project.created';
}

export interface ProjectUpdatedEvent extends DomainEvent<Project> {
  readonly type: 'project.updated';
}

export interface AuthenticatedEvent extends DomainEvent<AuthState> {
  readonly type: 'auth.authenticated';
}

export interface LoggedOutEvent extends DomainEvent<void> {
  readonly type: 'auth.logged_out';
}

export type SystemEvent = 
  | UserCreatedEvent
  | UserUpdatedEvent
  | ProjectCreatedEvent
  | ProjectUpdatedEvent
  | AuthenticatedEvent
  | LoggedOutEvent;

// Error types
export class ValidationError extends Error {
  constructor(
    message: string,
    public readonly field: string,
    public readonly value: unknown
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends Error {
  constructor(message: string = 'Authentication failed') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends Error {
  constructor(message: string = 'Insufficient permissions') {
    super(message);
    this.name = 'AuthorizationError';
  }
}

export class NetworkError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
    public readonly statusText?: string
  ) {
    super(message);
    this.name = 'NetworkError';
  }
}