/**
 * Minimal testing utilities without complex dependencies
 * For verifying TypeScript configuration
 */

// Test environment setup without complex dependencies
export function setupTestEnvironment() {
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
}

// Test cleanup utilities
export function cleanupTestEnvironment() {
  // Clear localStorage
  localStorage.clear();

  // Clear sessionStorage
  sessionStorage.clear();

  // Reset URL
  window.history.replaceState({}, '', '/');
}

// Helper to create test IDs consistently
export function createTestId(component: string, element?: string): string {
  return element ? `${component}-${element}` : component;
}

// Re-export testing library essentials for basic usage
export {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
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
} from 'vitest';