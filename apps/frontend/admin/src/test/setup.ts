/**
 * Test setup file for Admin app
 * Configures testing environment and mocks
 */

import { beforeAll, afterEach, afterAll, vi } from 'vitest';

// Mock redux-persist early to avoid import issues
vi.mock('redux-persist/integration/react', () => ({
  PersistGate: ({ children }: { children: any }) => children,
}));

// Mock the app file to avoid complex import issues in tests
vi.mock('../app', () => ({
  App: () => 'Mock Admin App Component',
}));

import { setupTestEnvironment, cleanupTestEnvironment } from '@skillforge-ai/testing';
import { cleanup } from '@testing-library/react';
import { server } from './mocks/server';

// Setup MSW server
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Setup test environment
beforeAll(() => {
  setupTestEnvironment();
});

// Cleanup after each test
afterEach(() => {
  cleanupTestEnvironment();
  cleanup();
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

// Mock environment variables
process.env.VITE_API_URL = 'http://localhost:8000/api';
process.env.NODE_ENV = 'test';

// Mock @preact/signals-react to avoid ESM/CommonJS conflicts
vi.mock('@preact/signals-react', () => ({
  useSignal: vi.fn((initialValue: any) => ({
    value: initialValue,
    subscribe: vi.fn(),
  })),
  useComputed: vi.fn((fn: any) => ({ value: fn() })),
  useSignalEffect: vi.fn(),
  signal: vi.fn((initialValue: any) => ({
    value: initialValue,
    subscribe: vi.fn(),
  })),
  computed: vi.fn((fn: any) => ({ value: fn() })),
  effect: vi.fn(),
  Signal: class MockSignal {
    constructor(public value: any) {}
    subscribe = vi.fn();
  },
}));

// Mock module federation remotes for tests (admin app perspective)
vi.mock('auth/App', () => ({
  default: () => 'Mock Auth App',
}));

vi.mock('learner/App', () => ({
  default: () => 'Mock Learner App',
}));

vi.mock('company/App', () => ({
  default: () => 'Mock Company App',
}));

vi.mock('shell/App', () => ({
  default: () => 'Mock Shell App',
}));