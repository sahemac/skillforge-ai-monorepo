/**
 * Vitest configuration for Shell app
 */

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: [
      'node_modules',
      'dist',
      '.nuxt',
      // TEMPORARY: Excluding app.test.tsx due to vitest worker crash after test completion
      // TODO: Investigate and fix the root cause of worker exit
      'src/test/app.test.tsx',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.{ts,js}',
        'dist/',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
    server: {
      deps: {
        inline: [
          '@skillforge-ai/shared-state',
          '@skillforge-ai/testing',
          '@skillforge-ai/core',
          '@skillforge-ai/ui-kit',
          '@skillforge-ai/api-client',
          '@skillforge-ai/shared',
        ],
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/domain': path.resolve(__dirname, './src/domain'),
      '@/application': path.resolve(__dirname, './src/application'),
      '@/infrastructure': path.resolve(__dirname, './src/infrastructure'),
      '@/presentation': path.resolve(__dirname, './src/presentation'),
      '@skillforge-ai/core': path.resolve(__dirname, '../../../packages/core/src'),
      '@skillforge-ai/ui-kit': path.resolve(__dirname, '../../../packages/ui-kit/src'),
      '@skillforge-ai/api-client': path.resolve(__dirname, '../../../packages/api-client/src'),
      '@skillforge-ai/shared': path.resolve(__dirname, '../../../packages/shared/src'),
      '@skillforge-ai/shared-state': path.resolve(__dirname, '../../../packages/shared-state/src'),
      '@skillforge-ai/testing': path.resolve(__dirname, '../../../packages/testing/src'),
    },
  },
});