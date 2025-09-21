/**
 * API Types - Generated from OpenAPI specification
 * Provides type-safe interfaces for all API endpoints
 */

import { z } from 'zod';

// Base API response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  timestamp: string;
}

export interface ApiError {
  error: string;
  message: string;
  statusCode: number;
  details?: Record<string, any>;
  timestamp: string;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  message?: string;
  timestamp: string;
}

// Request configuration types
export interface RequestConfig {
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  cache?: boolean;
  cacheTTL?: number;
}

// Authentication types
export const LoginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
  rememberMe: z.boolean().optional(),
});

export const AuthResponseSchema = z.object({
  accessToken: z.string(),
  refreshToken: z.string(),
  expiresIn: z.number(),
  expiresAt: z.number(),
  tokenType: z.string().default('Bearer'),
  user: z.object({
    id: z.string().uuid(),
    email: z.string().email(),
    username: z.string(),
    firstName: z.string(),
    lastName: z.string(),
    role: z.enum(['learner', 'company', 'admin']),
    isActive: z.boolean(),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
    profile: z.object({
      avatar: z.string().url().optional(),
      bio: z.string().optional(),
      skills: z.array(z.string()).default([]),
      preferences: z.record(z.unknown()).default({}),
    }).optional(),
  }),
});

export const RefreshTokenRequestSchema = z.object({
  refreshToken: z.string(),
});

// User types
export const CreateUserRequestSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3).max(50),
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
  password: z.string().min(8),
  role: z.enum(['learner', 'company', 'admin']).default('learner'),
});

export const UpdateUserRequestSchema = z.object({
  username: z.string().min(3).max(50).optional(),
  firstName: z.string().min(1).max(100).optional(),
  lastName: z.string().min(1).max(100).optional(),
  email: z.string().email().optional(),
  isActive: z.boolean().optional(),
  profile: z.object({
    avatar: z.string().url().optional(),
    bio: z.string().optional(),
    skills: z.array(z.string()).optional(),
    preferences: z.record(z.unknown()).optional(),
  }).optional(),
});

export const UserResponseSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  username: z.string(),
  firstName: z.string(),
  lastName: z.string(),
  role: z.enum(['learner', 'company', 'admin']),
  isActive: z.boolean(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  profile: z.object({
    avatar: z.string().url().optional(),
    bio: z.string().optional(),
    skills: z.array(z.string()).default([]),
    preferences: z.record(z.unknown()).default({}),
  }).optional(),
});

export const GetUsersQuerySchema = z.object({
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().max(100).default(20),
  search: z.string().optional(),
  role: z.enum(['learner', 'company', 'admin']).optional(),
  isActive: z.boolean().optional(),
  sortBy: z.enum(['createdAt', 'updatedAt', 'username', 'email']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});

// Project types
export const CreateProjectRequestSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().min(1),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']),
  estimatedDuration: z.number().positive(),
  skills: z.array(z.string()).min(1),
  requirements: z.array(z.string()).default([]),
  deliverables: z.array(z.string()).default([]),
  resources: z.array(z.object({
    title: z.string(),
    url: z.string().url(),
    type: z.enum(['video', 'article', 'documentation', 'tutorial', 'other']),
  })).default([]),
  metadata: z.record(z.unknown()).default({}),
});

export const UpdateProjectRequestSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  description: z.string().min(1).optional(),
  status: z.enum(['draft', 'active', 'completed', 'archived']).optional(),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']).optional(),
  estimatedDuration: z.number().positive().optional(),
  skills: z.array(z.string()).optional(),
  requirements: z.array(z.string()).optional(),
  deliverables: z.array(z.string()).optional(),
  resources: z.array(z.object({
    title: z.string(),
    url: z.string().url(),
    type: z.enum(['video', 'article', 'documentation', 'tutorial', 'other']),
  })).optional(),
  metadata: z.record(z.unknown()).optional(),
});

export const ProjectResponseSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  status: z.enum(['draft', 'active', 'completed', 'archived']),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']),
  estimatedDuration: z.number(),
  skills: z.array(z.string()),
  requirements: z.array(z.string()),
  deliverables: z.array(z.string()),
  resources: z.array(z.object({
    title: z.string(),
    url: z.string().url(),
    type: z.enum(['video', 'article', 'documentation', 'tutorial', 'other']),
  })),
  authorId: z.string().uuid(),
  author: UserResponseSchema.optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  metadata: z.record(z.unknown()),
});

export const GetProjectsQuerySchema = z.object({
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().max(100).default(20),
  search: z.string().optional(),
  status: z.enum(['draft', 'active', 'completed', 'archived']).optional(),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']).optional(),
  authorId: z.string().uuid().optional(),
  skills: z.array(z.string()).optional(),
  sortBy: z.enum(['createdAt', 'updatedAt', 'title', 'difficulty']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});

// File upload types
export const FileUploadResponseSchema = z.object({
  id: z.string().uuid(),
  filename: z.string(),
  originalName: z.string(),
  mimeType: z.string(),
  size: z.number(),
  url: z.string().url(),
  uploadedAt: z.string().datetime(),
});

// Analytics types
export const AnalyticsQuerySchema = z.object({
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  granularity: z.enum(['hour', 'day', 'week', 'month']).default('day'),
  metrics: z.array(z.enum(['users', 'projects', 'completions', 'engagement'])).default(['users']),
});

export const AnalyticsResponseSchema = z.object({
  period: z.object({
    start: z.string().datetime(),
    end: z.string().datetime(),
    granularity: z.enum(['hour', 'day', 'week', 'month']),
  }),
  metrics: z.record(z.array(z.object({
    timestamp: z.string().datetime(),
    value: z.number(),
  }))),
  summary: z.record(z.object({
    total: z.number(),
    average: z.number(),
    change: z.number(),
    changePercent: z.number(),
  })),
});

// Notification types
export const NotificationResponseSchema = z.object({
  id: z.string().uuid(),
  type: z.enum(['info', 'success', 'warning', 'error']),
  title: z.string(),
  message: z.string(),
  read: z.boolean(),
  userId: z.string().uuid(),
  metadata: z.record(z.unknown()).default({}),
  createdAt: z.string().datetime(),
  readAt: z.string().datetime().optional(),
});

export const CreateNotificationRequestSchema = z.object({
  type: z.enum(['info', 'success', 'warning', 'error']),
  title: z.string().min(1).max(200),
  message: z.string().min(1),
  userId: z.string().uuid(),
  metadata: z.record(z.unknown()).default({}),
});

// Type inference from schemas
export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type AuthResponse = z.infer<typeof AuthResponseSchema>;
export type RefreshTokenRequest = z.infer<typeof RefreshTokenRequestSchema>;

export type CreateUserRequest = z.infer<typeof CreateUserRequestSchema>;
export type UpdateUserRequest = z.infer<typeof UpdateUserRequestSchema>;
export type UserResponse = z.infer<typeof UserResponseSchema>;
export type GetUsersQuery = z.infer<typeof GetUsersQuerySchema>;

export type CreateProjectRequest = z.infer<typeof CreateProjectRequestSchema>;
export type UpdateProjectRequest = z.infer<typeof UpdateProjectRequestSchema>;
export type ProjectResponse = z.infer<typeof ProjectResponseSchema>;
export type GetProjectsQuery = z.infer<typeof GetProjectsQuerySchema>;

export type FileUploadResponse = z.infer<typeof FileUploadResponseSchema>;

export type AnalyticsQuery = z.infer<typeof AnalyticsQuerySchema>;
export type AnalyticsResponse = z.infer<typeof AnalyticsResponseSchema>;

export type NotificationResponse = z.infer<typeof NotificationResponseSchema>;
export type CreateNotificationRequest = z.infer<typeof CreateNotificationRequestSchema>;

// API endpoints configuration
export interface ApiEndpoints {
  // Authentication
  'POST /auth/login': {
    request: LoginRequest;
    response: AuthResponse;
  };
  'POST /auth/logout': {
    request: void;
    response: { message: string };
  };
  'POST /auth/refresh': {
    request: RefreshTokenRequest;
    response: AuthResponse;
  };
  'GET /auth/me': {
    request: void;
    response: UserResponse;
  };

  // Users
  'GET /users': {
    request: GetUsersQuery;
    response: PaginatedResponse<UserResponse>;
  };
  'GET /users/:id': {
    request: { id: string };
    response: UserResponse;
  };
  'POST /users': {
    request: CreateUserRequest;
    response: UserResponse;
  };
  'PATCH /users/:id': {
    request: { id: string } & UpdateUserRequest;
    response: UserResponse;
  };
  'DELETE /users/:id': {
    request: { id: string };
    response: { message: string };
  };
  'POST /users/:id/activate': {
    request: { id: string };
    response: UserResponse;
  };
  'POST /users/:id/deactivate': {
    request: { id: string };
    response: UserResponse;
  };

  // Projects
  'GET /projects': {
    request: GetProjectsQuery;
    response: PaginatedResponse<ProjectResponse>;
  };
  'GET /projects/:id': {
    request: { id: string };
    response: ProjectResponse;
  };
  'POST /projects': {
    request: CreateProjectRequest;
    response: ProjectResponse;
  };
  'PATCH /projects/:id': {
    request: { id: string } & UpdateProjectRequest;
    response: ProjectResponse;
  };
  'DELETE /projects/:id': {
    request: { id: string };
    response: { message: string };
  };
  'POST /projects/:id/publish': {
    request: { id: string };
    response: ProjectResponse;
  };
  'POST /projects/:id/archive': {
    request: { id: string };
    response: ProjectResponse;
  };
  'POST /projects/:id/duplicate': {
    request: { id: string; title?: string };
    response: ProjectResponse;
  };

  // Files
  'POST /files/upload': {
    request: FormData;
    response: FileUploadResponse;
  };
  'DELETE /files/:id': {
    request: { id: string };
    response: { message: string };
  };

  // Analytics
  'GET /analytics': {
    request: AnalyticsQuery;
    response: AnalyticsResponse;
  };

  // Notifications
  'GET /notifications': {
    request: { page?: number; limit?: number; read?: boolean };
    response: PaginatedResponse<NotificationResponse>;
  };
  'POST /notifications': {
    request: CreateNotificationRequest;
    response: NotificationResponse;
  };
  'PATCH /notifications/:id/read': {
    request: { id: string };
    response: NotificationResponse;
  };
  'DELETE /notifications/:id': {
    request: { id: string };
    response: { message: string };
  };
}

// Type helpers
export type ApiEndpointKeys = keyof ApiEndpoints;
export type ApiMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
export type ApiPath = string;

export type ExtractRequest<T extends ApiEndpointKeys> = ApiEndpoints[T]['request'];
export type ExtractResponse<T extends ApiEndpointKeys> = ApiEndpoints[T]['response'];

// Error types
export class ApiValidationError extends Error {
  constructor(
    message: string,
    public field: string,
    public value: unknown
  ) {
    super(message);
    this.name = 'ApiValidationError';
  }
}

export class ApiNetworkError extends Error {
  constructor(
    message: string,
    public status?: number,
    public statusText?: string
  ) {
    super(message);
    this.name = 'ApiNetworkError';
  }
}

export class ApiAuthenticationError extends Error {
  constructor(message: string = 'Authentication required') {
    super(message);
    this.name = 'ApiAuthenticationError';
  }
}

export class ApiAuthorizationError extends Error {
  constructor(message: string = 'Insufficient permissions') {
    super(message);
    this.name = 'ApiAuthorizationError';
  }
}

export class ApiRateLimitError extends Error {
  constructor(
    message: string = 'Rate limit exceeded',
    public retryAfter?: number
  ) {
    super(message);
    this.name = 'ApiRateLimitError';
  }
}