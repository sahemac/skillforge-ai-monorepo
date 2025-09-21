/**
 * Test fixtures and mock data
 * Provides consistent test data for all components and services
 */

import { faker } from '@faker-js/faker';

// User fixtures
export function createMockUser(overrides: Partial<any> = {}) {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    username: faker.internet.userName(),
    firstName: faker.person.firstName(),
    lastName: faker.person.lastName(),
    role: faker.helpers.arrayElement(['learner', 'company', 'admin'] as const),
    isActive: faker.datatype.boolean(),
    createdAt: faker.date.past().toISOString(),
    updatedAt: faker.date.recent().toISOString(),
    profile: {
      avatar: faker.image.avatar(),
      bio: faker.lorem.paragraph(),
      skills: faker.helpers.arrayElements(['JavaScript', 'React', 'TypeScript', 'Node.js', 'Python'], { min: 1, max: 5 }),
      preferences: {
        theme: faker.helpers.arrayElement(['light', 'dark']),
        language: faker.helpers.arrayElement(['en', 'fr', 'es']),
        notifications: faker.datatype.boolean(),
      },
    },
    ...overrides,
  };
}

export function createMockLearner(overrides: Partial<any> = {}) {
  return createMockUser({
    role: 'learner',
    ...overrides,
  });
}

export function createMockCompany(overrides: Partial<any> = {}) {
  return createMockUser({
    role: 'company',
    profile: {
      avatar: faker.image.avatar(),
      bio: faker.company.catchPhrase(),
      skills: faker.helpers.arrayElements(['Project Management', 'Leadership', 'Strategy', 'Marketing'], { min: 2, max: 4 }),
      preferences: {
        theme: 'light',
        language: 'en',
        notifications: true,
      },
    },
    ...overrides,
  });
}

export function createMockAdmin(overrides: Partial<any> = {}) {
  return createMockUser({
    role: 'admin',
    isActive: true,
    ...overrides,
  });
}

// Project fixtures
export function createMockProject(overrides: Partial<any> = {}) {
  return {
    id: faker.string.uuid(),
    title: faker.lorem.words(3),
    description: faker.lorem.paragraphs(2),
    status: faker.helpers.arrayElement(['draft', 'active', 'completed', 'archived'] as const),
    difficulty: faker.helpers.arrayElement(['beginner', 'intermediate', 'advanced'] as const),
    estimatedDuration: faker.number.int({ min: 1, max: 40 }),
    skills: faker.helpers.arrayElements(['JavaScript', 'React', 'TypeScript', 'Node.js', 'Python', 'Docker'], { min: 1, max: 4 }),
    requirements: faker.helpers.arrayElements([
      'Basic programming knowledge',
      'Understanding of web development',
      'Familiarity with version control',
      'Knowledge of databases',
    ], { min: 0, max: 3 }),
    deliverables: faker.helpers.arrayElements([
      'Completed application',
      'Documentation',
      'Test suite',
      'Deployment guide',
    ], { min: 1, max: 4 }),
    resources: Array.from({ length: faker.number.int({ min: 1, max: 5 }) }, () => ({
      title: faker.lorem.words(2),
      url: faker.internet.url(),
      type: faker.helpers.arrayElement(['video', 'article', 'documentation', 'tutorial', 'other'] as const),
    })),
    authorId: faker.string.uuid(),
    author: createMockUser(),
    createdAt: faker.date.past().toISOString(),
    updatedAt: faker.date.recent().toISOString(),
    metadata: {
      tags: faker.helpers.arrayElements(['web', 'mobile', 'backend', 'frontend', 'fullstack'], { min: 1, max: 3 }),
      views: faker.number.int({ min: 0, max: 10000 }),
      enrollments: faker.number.int({ min: 0, max: 500 }),
    },
    ...overrides,
  };
}

export function createMockActiveProject(overrides: Partial<any> = {}) {
  return createMockProject({
    status: 'active',
    ...overrides,
  });
}

export function createMockDraftProject(overrides: Partial<any> = {}) {
  return createMockProject({
    status: 'draft',
    ...overrides,
  });
}

// Authentication fixtures
export function createMockAuthResponse(overrides: Partial<any> = {}) {
  const expiresIn = 3600; // 1 hour
  const expiresAt = Date.now() + (expiresIn * 1000);
  
  return {
    accessToken: faker.string.alphanumeric(32),
    refreshToken: faker.string.alphanumeric(32),
    expiresIn,
    expiresAt,
    tokenType: 'Bearer',
    user: createMockUser(),
    ...overrides,
  };
}

export function createMockLoginRequest(overrides: Partial<any> = {}) {
  return {
    email: faker.internet.email(),
    password: faker.internet.password(),
    rememberMe: faker.datatype.boolean(),
    ...overrides,
  };
}

// API response fixtures
export function createMockApiResponse<T>(data: T, overrides: Partial<any> = {}) {
  return {
    data,
    message: 'Success',
    timestamp: new Date().toISOString(),
    ...overrides,
  };
}

export function createMockPaginatedResponse<T>(
  items: T[],
  overrides: Partial<any> = {}
) {
  const page = overrides.page || 1;
  const limit = overrides.limit || 20;
  const total = overrides.total || items.length;
  const totalPages = Math.ceil(total / limit);
  
  return {
    data: items,
    pagination: {
      page,
      limit,
      total,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1,
    },
    message: 'Success',
    timestamp: new Date().toISOString(),
    ...overrides,
  };
}

export function createMockApiError(overrides: Partial<any> = {}) {
  return {
    error: 'API_ERROR',
    message: faker.lorem.sentence(),
    statusCode: faker.helpers.arrayElement([400, 401, 403, 404, 422, 500]),
    details: {},
    timestamp: new Date().toISOString(),
    ...overrides,
  };
}

// Notification fixtures
export function createMockNotification(overrides: Partial<any> = {}) {
  return {
    id: faker.string.uuid(),
    type: faker.helpers.arrayElement(['info', 'success', 'warning', 'error'] as const),
    title: faker.lorem.words(3),
    message: faker.lorem.sentence(),
    read: faker.datatype.boolean(),
    userId: faker.string.uuid(),
    metadata: {
      actionUrl: faker.internet.url(),
      category: faker.helpers.arrayElement(['system', 'project', 'user', 'admin']),
    },
    createdAt: faker.date.recent().toISOString(),
    readAt: faker.datatype.boolean() ? faker.date.recent().toISOString() : undefined,
    ...overrides,
  };
}

// Analytics fixtures
export function createMockAnalyticsData(overrides: Partial<any> = {}) {
  const startDate = faker.date.past();
  const endDate = faker.date.recent();
  const granularity = faker.helpers.arrayElement(['hour', 'day', 'week', 'month'] as const);
  
  // Generate time series data
  const dataPoints = Array.from({ length: 30 }, (_, index) => ({
    timestamp: new Date(startDate.getTime() + (index * 24 * 60 * 60 * 1000)).toISOString(),
    value: faker.number.int({ min: 0, max: 1000 }),
  }));
  
  return {
    period: {
      start: startDate.toISOString(),
      end: endDate.toISOString(),
      granularity,
    },
    metrics: {
      users: dataPoints,
      projects: dataPoints.map(point => ({
        ...point,
        value: faker.number.int({ min: 0, max: 100 }),
      })),
    },
    summary: {
      users: {
        total: faker.number.int({ min: 1000, max: 10000 }),
        average: faker.number.int({ min: 10, max: 100 }),
        change: faker.number.int({ min: -100, max: 100 }),
        changePercent: faker.number.float({ min: -50, max: 50, fractionDigits: 2 }),
      },
    },
    ...overrides,
  };
}

// Form fixtures
export function createMockFormData(overrides: Partial<any> = {}) {
  return {
    name: faker.person.fullName(),
    email: faker.internet.email(),
    message: faker.lorem.paragraph(),
    category: faker.helpers.arrayElement(['support', 'feedback', 'bug', 'feature']),
    priority: faker.helpers.arrayElement(['low', 'medium', 'high', 'urgent']),
    ...overrides,
  };
}

// File upload fixtures
export function createMockFile(overrides: Partial<any> = {}) {
  const name = faker.system.fileName();
  const size = faker.number.int({ min: 1024, max: 1024 * 1024 * 10 }); // 1KB to 10MB
  
  const file = new File(['mock file content'], name, {
    type: faker.helpers.arrayElement([
      'image/jpeg',
      'image/png',
      'application/pdf',
      'text/plain',
      'application/json',
    ]),
  });
  
  Object.defineProperty(file, 'size', {
    value: size,
    writable: false,
  });
  
  return file;
}

export function createMockFileUploadResponse(overrides: Partial<any> = {}) {
  return {
    id: faker.string.uuid(),
    filename: faker.system.fileName(),
    originalName: faker.system.fileName(),
    mimeType: faker.helpers.arrayElement([
      'image/jpeg',
      'image/png',
      'application/pdf',
      'text/plain',
    ]),
    size: faker.number.int({ min: 1024, max: 1024 * 1024 * 10 }),
    url: faker.internet.url(),
    uploadedAt: faker.date.recent().toISOString(),
    ...overrides,
  };
}

// Utility functions for creating collections
export function createMockUsers(count: number, overrides: Partial<any> = {}) {
  return Array.from({ length: count }, () => createMockUser(overrides));
}

export function createMockProjects(count: number, overrides: Partial<any> = {}) {
  return Array.from({ length: count }, () => createMockProject(overrides));
}

export function createMockNotifications(count: number, overrides: Partial<any> = {}) {
  return Array.from({ length: count }, () => createMockNotification(overrides));
}

// Seed function for consistent test data
export function seedFaker(seed?: number) {
  if (seed !== undefined) {
    faker.seed(seed);
  }
}

// Reset faker for clean tests
export function resetFaker() {
  faker.seed();
}