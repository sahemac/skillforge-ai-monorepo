import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'shell',
      remotes: {
        auth: 'https://skillforge-auth-koi53iwqbq-ew.a.run.app/assets/remoteEntry.js',
        learner: 'https://skillforge-learner-koi53iwqbq-ew.a.run.app/assets/remoteEntry.js',
        company: 'https://skillforge-company-koi53iwqbq-ew.a.run.app/assets/remoteEntry.js',
        admin: 'https://skillforge-admin-koi53iwqbq-ew.a.run.app/assets/remoteEntry.js',
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
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
});