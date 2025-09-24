/**
 * TypeScript Configuration Verification Test
 */

import { describe, it, expect } from 'vitest';
import { setupTestEnvironment, cleanupTestEnvironment, createTestId } from '@skillforge-ai/testing/minimal-utils';

describe('TypeScript Configuration Verification', () => {
  it('should successfully import from testing package minimal-utils', () => {
    expect(typeof setupTestEnvironment).toBe('function');
    expect(typeof cleanupTestEnvironment).toBe('function');
    expect(typeof createTestId).toBe('function');
  });

  it('should resolve path mappings correctly', () => {
    // Test createTestId utility function
    const testId = createTestId('button', 'submit');
    expect(testId).toBe('button-submit');

    const simpleTestId = createTestId('modal');
    expect(simpleTestId).toBe('modal');
  });

  it('should handle environment setup and cleanup', () => {
    setupTestEnvironment();

    // Verify mocks are in place
    expect(window.matchMedia).toBeDefined();
    expect(global.IntersectionObserver).toBeDefined();
    expect(global.ResizeObserver).toBeDefined();

    cleanupTestEnvironment();

    // localStorage should be cleared
    expect(localStorage.length).toBe(0);
  });

  it('should support async operations', async () => {
    const result = await Promise.resolve('TypeScript config works!');
    expect(result).toBe('TypeScript config works!');
  });
});