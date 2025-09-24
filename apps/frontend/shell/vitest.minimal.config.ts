/**
 * Minimal Vitest configuration for TypeScript verification
 */

import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/minimal-setup.ts'],
    include: ['src/test/basic-config.test.ts'],
    exclude: ['node_modules', 'dist', '.nuxt'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@skillforge-ai/core': path.resolve(__dirname, '../../../packages/core/src'),
      '@skillforge-ai/ui-kit': path.resolve(__dirname, '../../../packages/ui-kit/src'),
      '@skillforge-ai/api-client': path.resolve(__dirname, '../../../packages/api-client/src'),
      '@skillforge-ai/shared': path.resolve(__dirname, '../../../packages/shared/src'),
      '@skillforge-ai/testing': path.resolve(__dirname, '../../../packages/testing/src'),
    },
  },
});