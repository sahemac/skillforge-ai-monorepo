/**
 * MSW Server setup for testing
 * Provides API mocking for all shell app tests
 */

import { setupServer } from 'msw/node';
import { handlers } from '@skillforge-ai/testing';

// Setup MSW server with API handlers
export const server = setupServer(...handlers);