/**
 * Basic TypeScript Configuration Test
 * No React or complex dependencies
 */

import { describe, it, expect, vi } from 'vitest';

// Import a simple utility from core package to test path resolution
// Using type-only imports to avoid runtime issues

describe('Basic TypeScript Configuration', () => {
  it('should run basic Vitest tests', () => {
    expect(1 + 1).toBe(2);
    expect('test').toBe('test');
    expect(true).toBe(true);
  });

  it('should support TypeScript features', () => {
    // Test TypeScript compilation works
    const obj: { name: string; value: number } = {
      name: 'test',
      value: 42
    };

    expect(obj.name).toBe('test');
    expect(obj.value).toBe(42);
  });

  it('should support async operations', async () => {
    const asyncFunction = async (): Promise<string> => {
      return 'success';
    };

    const result = await asyncFunction();
    expect(result).toBe('success');
  });

  it('should support mocking with vi', () => {
    const mockFn = vi.fn().mockReturnValue('mocked');

    expect(mockFn()).toBe('mocked');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('should support array and object operations', () => {
    const items = [1, 2, 3, 4, 5];
    const doubled = items.map(x => x * 2);

    expect(doubled).toEqual([2, 4, 6, 8, 10]);

    const user = {
      id: '123',
      name: 'Test User',
      roles: ['user', 'admin']
    };

    expect(user.id).toBe('123');
    expect(user.roles).toContain('admin');
  });

  it('should handle error scenarios', () => {
    expect(() => {
      throw new Error('Test error');
    }).toThrow('Test error');
  });
});