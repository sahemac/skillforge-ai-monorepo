/**
 * MSW Server setup for testing
 * Provides API mocking for all learner app tests
 */

import { vi } from 'vitest';

// Mock MSW server for test environment
export const server = {
  listen: vi.fn(),
  close: vi.fn(),
  resetHandlers: vi.fn(),
  use: vi.fn(),
};