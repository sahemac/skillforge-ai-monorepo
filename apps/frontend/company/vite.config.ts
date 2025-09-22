import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'company',
      filename: 'remoteEntry.js',
      exposes: {
        './App': './src/app.tsx',
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
    minify: 'terser',
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
        },
      },
    },
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
  server: {
    port: 3003,
    cors: true,
    origin: 'http://localhost:3003',
  },
  preview: {
    port: 3003,
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
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
});