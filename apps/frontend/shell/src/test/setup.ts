/**
 * Test setup file for Shell app
 * Configures testing environment and mocks
 */

import { beforeAll, afterEach, afterAll } from 'vitest';
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