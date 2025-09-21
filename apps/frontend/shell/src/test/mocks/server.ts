/**
 * MSW Server setup for testing
 * Provides API mocking for all shell app tests
 */

import { setupServer } from 'msw/node';
import { apiHandlers } from '@skillforge-ai/testing';

// Create MSW server with shared API handlers
export const server = setupServer(...apiHandlers);