/**
 * Simple test to verify TypeScript and Vitest configuration
 */

import { describe, it, expect } from 'vitest';
import { setupTestEnvironment, cleanupTestEnvironment } from '@skillforge-ai/testing';

describe('Configuration Test', () => {
  it('should import from testing package successfully', () => {
    expect(typeof setupTestEnvironment).toBe('function');
    expect(typeof cleanupTestEnvironment).toBe('function');
  });

  it('should run basic tests', () => {
    expect(1 + 1).toBe(2);
    expect('hello').toBe('hello');
  });

  it('should handle async operations', async () => {
    const result = await Promise.resolve('success');
    expect(result).toBe('success');
  });
});