import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js',
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          // Automatic code splitting by module
          // Vite will create chunks for each lazy-loaded module automatically
        },
      },
    },
  },
  server: {
    port: 3000,
    strictPort: true, // CRITIQUE: Fail si port occupé au lieu de chercher un autre port
    cors: true,
    origin: 'http://localhost:3000',
    host: '0.0.0.0', // Expose sur toutes les interfaces (nécessaire pour Docker/Cloud Run)
  },
  preview: {
    port: 3000,
    cors: true,
  },
  resolve: {
    alias: {
      '@': '/src',
      '@/modules': '/src/modules',
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