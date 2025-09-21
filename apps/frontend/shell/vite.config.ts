import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'shell',
      remotes: {
        auth: 'http://localhost:3001/assets/remoteEntry.js',
        learner: 'http://localhost:3002/assets/remoteEntry.js',
        company: 'http://localhost:3003/assets/remoteEntry.js',
        admin: 'http://localhost:3004/assets/remoteEntry.js',
      },
      shared: {
        react: {
          singleton: true,
          requiredVersion: '^19.1.1',
        },
        'react-dom': {
          singleton: true,
          requiredVersion: '^19.1.1',
        },
        'react-router-dom': {
          singleton: true,
          requiredVersion: '^6.20.1',
        },
        '@skillforge-ai/core': {
          singleton: true,
        },
        '@skillforge-ai/ui-kit': {
          singleton: true,
        },
        '@skillforge-ai/api-client': {
          singleton: true,
        },
        '@skillforge-ai/shared': {
          singleton: true,
        },
      },
    }),
  ],
  build: {
    target: 'esnext',
    minify: false,
    cssCodeSplit: false,
  },
  server: {
    port: 3000,
    cors: true,
    origin: 'http://localhost:3000',
  },
  preview: {
    port: 3000,
    cors: true,
  },
  resolve: {
    alias: {
      '@': '/src',
      '@/domain': '/src/domain',
      '@/application': '/src/application',
      '@/infrastructure': '/src/infrastructure',
      '@/presentation': '/src/presentation',
    },
  },
  define: {
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development'),
  },
});