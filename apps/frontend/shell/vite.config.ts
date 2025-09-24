import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import federation from '@originjs/vite-plugin-federation';

export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production';
  const remoteBaseUrl = isProduction 
    ? 'https://skillforge-frontend-{app}-production-koi53iwqbq-ew.a.run.app'
    : 'http://localhost:{port}';

  return {
  plugins: [
    react(),
    federation({
      name: 'shell',
      remotes: {
        auth: isProduction 
          ? 'https://skillforge-frontend-auth-production-koi53iwqbq-ew.a.run.app/assets/remoteEntry.js'
          : 'http://localhost:3001/assets/remoteEntry.js',
        learner: isProduction
          ? 'https://skillforge-frontend-learner-production-koi53iwqbq-ew.a.run.app/assets/remoteEntry.js'
          : 'http://localhost:3002/assets/remoteEntry.js',
        company: isProduction
          ? 'https://skillforge-frontend-company-production-koi53iwqbq-ew.a.run.app/assets/remoteEntry.js'
          : 'http://localhost:3003/assets/remoteEntry.js',
        admin: isProduction
          ? 'https://skillforge-frontend-admin-production-koi53iwqbq-ew.a.run.app/assets/remoteEntry.js'
          : 'http://localhost:3004/assets/remoteEntry.js',
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
  };
});