/**
 * API mocks using Mock Service Worker (MSW)
 * Provides realistic API responses for testing
 */

import { http, HttpResponse } from 'msw';
import {
  createMockUser,
  createMockProject,
  createMockAuthResponse,
  createMockApiResponse,
  createMockPaginatedResponse,
  createMockApiError,
  createMockNotification,
  createMockAnalyticsData,
  createMockFileUploadResponse,
  createMockUsers,
  createMockProjects,
  createMockNotifications,
} from '../fixtures';

// Base API URL
const API_BASE = process.env.VITE_API_URL || 'http://localhost:8000/api';

// Mock data stores
let mockUsers = createMockUsers(50);
let mockProjects = createMockProjects(30);
let mockNotifications = createMockNotifications(20);
let mockAuthToken: string | null = null;

/**
 * Authentication handlers
 */
const authHandlers = [
  // Login
  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    const body = await request.json() as any;
    
    // Simulate login validation
    if (body.email === 'test@example.com' && body.password === 'password') {
      const authResponse = createMockAuthResponse({
        user: createMockUser({ email: body.email }),
      });
      mockAuthToken = authResponse.accessToken;
      
      return HttpResponse.json(createMockApiResponse(authResponse));
    }
    
    return HttpResponse.json(
      createMockApiError({
        error: 'INVALID_CREDENTIALS',
        message: 'Invalid email or password',
        statusCode: 401,
      }),
      { status: 401 }
    );
  }),

  // Logout
  http.post(`${API_BASE}/auth/logout`, () => {
    mockAuthToken = null;
    return HttpResponse.json(
      createMockApiResponse({ message: 'Logged out successfully' })
    );
  }),

  // Refresh token
  http.post(`${API_BASE}/auth/refresh`, async ({ request }) => {
    const body = await request.json() as any;
    
    if (body.refreshToken) {
      const authResponse = createMockAuthResponse();
      mockAuthToken = authResponse.accessToken;
      
      return HttpResponse.json(createMockApiResponse(authResponse));
    }
    
    return HttpResponse.json(
      createMockApiError({
        error: 'INVALID_REFRESH_TOKEN',
        message: 'Invalid refresh token',
        statusCode: 401,
      }),
      { status: 401 }
    );
  }),

  // Get current user
  http.get(`${API_BASE}/auth/me`, ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ') || !mockAuthToken) {
      return HttpResponse.json(
        createMockApiError({
          error: 'UNAUTHORIZED',
          message: 'Authentication required',
          statusCode: 401,
        }),
        { status: 401 }
      );
    }
    
    const currentUser = createMockUser({
      email: 'test@example.com',
      role: 'admin',
    });
    
    return HttpResponse.json(createMockApiResponse(currentUser));
  }),

  // Get user permissions
  http.get(`${API_BASE}/auth/permissions`, ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(
        createMockApiError({
          error: 'UNAUTHORIZED',
          message: 'Authentication required',
          statusCode: 401,
        }),
        { status: 401 }
      );
    }
    
    const permissions = [
      'users:read',
      'users:write',
      'projects:read',
      'projects:write',
      'system:admin',
    ];
    
    return HttpResponse.json(createMockApiResponse(permissions));
  }),
];

/**
 * Users handlers
 */
const usersHandlers = [
  // Get users
  http.get(`${API_BASE}/users`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '20');
    const search = url.searchParams.get('search');
    const role = url.searchParams.get('role');
    
    let filteredUsers = [...mockUsers];
    
    // Apply search filter
    if (search) {
      filteredUsers = filteredUsers.filter(user =>
        user.username.toLowerCase().includes(search.toLowerCase()) ||
        user.email.toLowerCase().includes(search.toLowerCase()) ||
        user.firstName.toLowerCase().includes(search.toLowerCase()) ||
        user.lastName.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    // Apply role filter
    if (role) {
      filteredUsers = filteredUsers.filter(user => user.role === role);
    }
    
    // Apply pagination
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
    
    return HttpResponse.json(
      createMockPaginatedResponse(paginatedUsers, {
        page,
        limit,
        total: filteredUsers.length,
      })
    );
  }),

  // Get user by ID
  http.get(`${API_BASE}/users/:id`, ({ params }) => {
    const userId = params.id as string;
    const user = mockUsers.find(u => u.id === userId);
    
    if (!user) {
      return HttpResponse.json(
        createMockApiError({
          error: 'USER_NOT_FOUND',
          message: 'User not found',
          statusCode: 404,
        }),
        { status: 404 }
      );
    }
    
    return HttpResponse.json(createMockApiResponse(user));
  }),

  // Create user
  http.post(`${API_BASE}/users`, async ({ request }) => {
    const body = await request.json() as any;
    const newUser = createMockUser(body);
    mockUsers.push(newUser);
    
    return HttpResponse.json(
      createMockApiResponse(newUser),
      { status: 201 }
    );
  }),

  // Update user
  http.patch(`${API_BASE}/users/:id`, async ({ params, request }) => {
    const userId = params.id as string;
    const body = await request.json() as any;
    const userIndex = mockUsers.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
      return HttpResponse.json(
        createMockApiError({
          error: 'USER_NOT_FOUND',
          message: 'User not found',
          statusCode: 404,
        }),
        { status: 404 }
      );
    }
    
    mockUsers[userIndex] = { ...mockUsers[userIndex], ...body };
    
    return HttpResponse.json(createMockApiResponse(mockUsers[userIndex]));
  }),

  // Delete user
  http.delete(`${API_BASE}/users/:id`, ({ params }) => {
    const userId = params.id as string;
    const userIndex = mockUsers.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
      return HttpResponse.json(
        createMockApiError({
          error: 'USER_NOT_FOUND',
          message: 'User not found',
          statusCode: 404,
        }),
        { status: 404 }
      );
    }
    
    mockUsers.splice(userIndex, 1);
    
    return HttpResponse.json(
      createMockApiResponse({ message: 'User deleted successfully' })
    );
  }),
];

/**
 * Projects handlers
 */
const projectsHandlers = [
  // Get projects
  http.get(`${API_BASE}/projects`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '20');
    const search = url.searchParams.get('search');
    const status = url.searchParams.get('status');
    const difficulty = url.searchParams.get('difficulty');
    
    let filteredProjects = [...mockProjects];
    
    // Apply filters
    if (search) {
      filteredProjects = filteredProjects.filter(project =>
        project.title.toLowerCase().includes(search.toLowerCase()) ||
        project.description.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    if (status) {
      filteredProjects = filteredProjects.filter(project => project.status === status);
    }
    
    if (difficulty) {
      filteredProjects = filteredProjects.filter(project => project.difficulty === difficulty);
    }
    
    // Apply pagination
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedProjects = filteredProjects.slice(startIndex, endIndex);
    
    return HttpResponse.json(
      createMockPaginatedResponse(paginatedProjects, {
        page,
        limit,
        total: filteredProjects.length,
      })
    );
  }),

  // Get project by ID
  http.get(`${API_BASE}/projects/:id`, ({ params }) => {
    const projectId = params.id as string;
    const project = mockProjects.find(p => p.id === projectId);
    
    if (!project) {
      return HttpResponse.json(
        createMockApiError({
          error: 'PROJECT_NOT_FOUND',
          message: 'Project not found',
          statusCode: 404,
        }),
        { status: 404 }
      );
    }
    
    return HttpResponse.json(createMockApiResponse(project));
  }),

  // Create project
  http.post(`${API_BASE}/projects`, async ({ request }) => {
    const body = await request.json() as any;
    const newProject = createMockProject({
      ...body,
      status: 'draft',
      authorId: 'current-user-id',
    });
    mockProjects.push(newProject);
    
    return HttpResponse.json(
      createMockApiResponse(newProject),
      { status: 201 }
    );
  }),

  // Update project
  http.patch(`${API_BASE}/projects/:id`, async ({ params, request }) => {
    const projectId = params.id as string;
    const body = await request.json() as any;
    const projectIndex = mockProjects.findIndex(p => p.id === projectId);
    
    if (projectIndex === -1) {
      return HttpResponse.json(
        createMockApiError({
          error: 'PROJECT_NOT_FOUND',
          message: 'Project not found',
          statusCode: 404,
        }),
        { status: 404 }
      );
    }
    
    mockProjects[projectIndex] = { ...mockProjects[projectIndex], ...body };
    
    return HttpResponse.json(createMockApiResponse(mockProjects[projectIndex]));
  }),

  // Delete project
  http.delete(`${API_BASE}/projects/:id`, ({ params }) => {
    const projectId = params.id as string;
    const projectIndex = mockProjects.findIndex(p => p.id === projectId);
    
    if (projectIndex === -1) {
      return HttpResponse.json(
        createMockApiError({
          error: 'PROJECT_NOT_FOUND',
          message: 'Project not found',
          statusCode: 404,
        }),
        { status: 404 }
      );
    }
    
    mockProjects.splice(projectIndex, 1);
    
    return HttpResponse.json(
      createMockApiResponse({ message: 'Project deleted successfully' })
    );
  }),

  // Publish project
  http.post(`${API_BASE}/projects/:id/publish`, ({ params }) => {
    const projectId = params.id as string;
    const projectIndex = mockProjects.findIndex(p => p.id === projectId);
    
    if (projectIndex === -1) {
      return HttpResponse.json(
        createMockApiError({
          error: 'PROJECT_NOT_FOUND',
          message: 'Project not found',
          statusCode: 404,
        }),
        { status: 404 }
      );
    }
    
    mockProjects[projectIndex].status = 'active';
    
    return HttpResponse.json(createMockApiResponse(mockProjects[projectIndex]));
  }),
];

/**
 * File upload handlers
 */
const fileHandlers = [
  // Upload file
  http.post(`${API_BASE}/files/upload`, async ({ request }) => {
    // Simulate file upload delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const uploadResponse = createMockFileUploadResponse();
    
    return HttpResponse.json(
      createMockApiResponse(uploadResponse),
      { status: 201 }
    );
  }),
];

/**
 * Analytics handlers
 */
const analyticsHandlers = [
  // Get analytics data
  http.get(`${API_BASE}/analytics`, ({ request }) => {
    const analyticsData = createMockAnalyticsData();
    
    return HttpResponse.json(createMockApiResponse(analyticsData));
  }),
];

/**
 * Notifications handlers
 */
const notificationsHandlers = [
  // Get notifications
  http.get(`${API_BASE}/notifications`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '20');
    const read = url.searchParams.get('read');
    
    let filteredNotifications = [...mockNotifications];
    
    if (read !== null) {
      const isRead = read === 'true';
      filteredNotifications = filteredNotifications.filter(n => n.read === isRead);
    }
    
    // Apply pagination
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedNotifications = filteredNotifications.slice(startIndex, endIndex);
    
    return HttpResponse.json(
      createMockPaginatedResponse(paginatedNotifications, {
        page,
        limit,
        total: filteredNotifications.length,
      })
    );
  }),

  // Mark notification as read
  http.patch(`${API_BASE}/notifications/:id/read`, ({ params }) => {
    const notificationId = params.id as string;
    const notificationIndex = mockNotifications.findIndex(n => n.id === notificationId);
    
    if (notificationIndex === -1) {
      return HttpResponse.json(
        createMockApiError({
          error: 'NOTIFICATION_NOT_FOUND',
          message: 'Notification not found',
          statusCode: 404,
        }),
        { status: 404 }
      );
    }
    
    mockNotifications[notificationIndex].read = true;
    mockNotifications[notificationIndex].readAt = new Date().toISOString();
    
    return HttpResponse.json(createMockApiResponse(mockNotifications[notificationIndex]));
  }),
];

// Combine all handlers
export const handlers = [
  ...authHandlers,
  ...usersHandlers,
  ...projectsHandlers,
  ...fileHandlers,
  ...analyticsHandlers,
  ...notificationsHandlers,
];

// Utility functions for tests
export const mockApi = {
  resetData: () => {
    mockUsers = createMockUsers(50);
    mockProjects = createMockProjects(30);
    mockNotifications = createMockNotifications(20);
    mockAuthToken = null;
  },
  
  setAuthToken: (token: string | null) => {
    mockAuthToken = token;
  },
  
  addUser: (user: any) => {
    mockUsers.push(user);
  },
  
  addProject: (project: any) => {
    mockProjects.push(project);
  },
  
  getUserById: (id: string) => {
    return mockUsers.find(u => u.id === id);
  },
  
  getProjectById: (id: string) => {
    return mockProjects.find(p => p.id === id);
  },
};