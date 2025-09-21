/**
 * SkillForge AI Testing Package
 * Main entry point for testing utilities, mocks, and fixtures
 */

// Test utilities
export * from './utils/test-utils';

// Fixtures and mock data
export * from './fixtures';

// API mocks
export * from './mocks/api';

// Test setup utilities
export { setupServer } from 'msw/node';
export { setupWorker } from 'msw/browser';

// Re-export testing library essentials
export {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
  getByRole,
  getByText,
  getByLabelText,
  getByTestId,
  queryByRole,
  queryByText,
  queryByLabelText,
  queryByTestId,
  findByRole,
  findByText,
  findByLabelText,
  findByTestId,
} from '@testing-library/react';

export { userEvent } from '@testing-library/user-event';

export {
  expect,
  describe,
  it,
  test,
  beforeEach,
  afterEach,
  beforeAll,
  afterAll,
  vi,
  Mock,
  MockedFunction,
  SpyInstance,
} from 'vitest';

// Test configuration utilities
export function setupTestEnvironment() {
  // Mock window.matchMedia
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
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

  // Mock scrollTo
  window.scrollTo = vi.fn();

  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  };
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
  });

  // Mock sessionStorage
  const sessionStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  };
  Object.defineProperty(window, 'sessionStorage', {
    value: sessionStorageMock,
  });

  // Mock URL.createObjectURL
  global.URL.createObjectURL = vi.fn(() => 'mocked-url');
  global.URL.revokeObjectURL = vi.fn();

  // Mock fetch
  global.fetch = vi.fn();
}

// Test cleanup utilities
export function cleanupTestEnvironment() {
  vi.clearAllMocks();
  vi.resetAllMocks();
  
  // Clear localStorage
  localStorage.clear();
  
  // Clear sessionStorage
  sessionStorage.clear();
  
  // Reset URL
  window.history.replaceState({}, '', '/');
}

// Common test assertions
export const customMatchers = {
  toBeInTheDocument: (received: any) => {
    const pass = received && document.contains(received);
    return {
      message: () => `expected element ${pass ? 'not ' : ''}to be in the document`,
      pass,
    };
  },
  
  toHaveClass: (received: any, className: string) => {
    const pass = received && received.classList && received.classList.contains(className);
    return {
      message: () => `expected element ${pass ? 'not ' : ''}to have class "${className}"`,
      pass,
    };
  },
  
  toBeVisible: (received: any) => {
    const pass = received && received.style.display !== 'none' && received.style.visibility !== 'hidden';
    return {
      message: () => `expected element ${pass ? 'not ' : ''}to be visible`,
      pass,
    };
  },
};

// Vitest configuration helper
export const vitestConfig = {
  environment: 'jsdom',
  globals: true,
  setupFiles: ['./src/test-setup.ts'],
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html'],
    exclude: [
      'node_modules/',
      'src/test-setup.ts',
      '**/*.d.ts',
      '**/*.test.{ts,tsx}',
      '**/*.spec.{ts,tsx}',
    ],
  },
  testMatch: [
    '**/__tests__/**/*.{ts,tsx}',
    '**/?(*.)+(spec|test).{ts,tsx}',
  ],
};

// Export default test setup
export default setupTestEnvironment;