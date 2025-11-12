import React, { Suspense, lazy } from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider, Link } from 'react-router-dom';
import { store, persistor, queryClient } from '@skillforge-ai/shared-state';
import { ErrorBoundary } from '@/presentation/components/error-boundary/error-boundary';
import { LoadingSpinner } from '@/presentation/components/loading/loading-spinner';
import '@/presentation/styles/global.css';

// Lazy load auth pages
const LoginPage = lazy(() => import('@/modules/auth/pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/modules/auth/pages/RegisterPage').then(m => ({ default: m.RegisterPage })));

// Lazy load learner module
const LearnerDashboard = lazy(() => import('@/modules/learner/pages/LearnerDashboard').then(m => ({ default: m.LearnerDashboard })));

// Lazy load company module
const CompanyDashboard = lazy(() => import('@/modules/company/pages/CompanyDashboard').then(m => ({ default: m.CompanyDashboard })));
const ProjectsList = lazy(() => import('@/modules/company/pages/ProjectsList').then(m => ({ default: m.ProjectsList })));

// Lazy load admin module
const AdminDashboard = lazy(() => import('@/modules/admin/pages/AdminDashboard').then(m => ({ default: m.AdminDashboard })));

// Simple landing sans aucun lazy loading
const SimpleLanding = () => (
  <div style={{
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontFamily: 'Inter, system-ui, sans-serif',
    textAlign: 'center',
    padding: '20px'
  }}>
    <div>
      <h1 style={{ fontSize: '3rem', marginBottom: '2rem' }}>SkillForge AI</h1>
      <p style={{ fontSize: '1.25rem', marginBottom: '2rem', opacity: 0.9 }}>
        Application monolithique - Architecture migrée avec succès
      </p>
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
        <Link
          to="/auth/login"
          style={{
            background: 'white',
            color: '#667eea',
            padding: '1rem 2rem',
            borderRadius: '8px',
            textDecoration: 'none',
            fontWeight: 'bold'
          }}
        >
          Se Connecter
        </Link>
        <Link
          to="/auth/register"
          style={{
            background: 'rgba(255,255,255,0.2)',
            color: 'white',
            padding: '1rem 2rem',
            borderRadius: '8px',
            textDecoration: 'none',
            fontWeight: 'bold',
            border: '2px solid white'
          }}
        >
          S'inscrire
        </Link>
      </div>
    </div>
  </div>
);

const router = createBrowserRouter([
  {
    path: '/',
    element: <SimpleLanding />
  },
  {
    path: '/auth/login',
    element: (
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <LoginPage />
        </Suspense>
      </ErrorBoundary>
    )
  },
  {
    path: '/auth/register',
    element: (
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <RegisterPage />
        </Suspense>
      </ErrorBoundary>
    )
  },
  {
    path: '/learner/dashboard',
    element: (
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <LearnerDashboard />
        </Suspense>
      </ErrorBoundary>
    )
  },
  {
    path: '/company/dashboard',
    element: (
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <CompanyDashboard />
        </Suspense>
      </ErrorBoundary>
    )
  },
  {
    path: '/company/projects',
    element: (
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <ProjectsList />
        </Suspense>
      </ErrorBoundary>
    )
  },
  {
    path: '/admin/users',
    element: (
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <AdminDashboard />
        </Suspense>
      </ErrorBoundary>
    )
  },
  {
    path: '*',
    element: <SimpleLanding />
  }
]);

export const App: React.FC = () => {
  return (
    <Provider store={store}>
      <PersistGate loading={<LoadingSpinner />} persistor={persistor}>
        <QueryClientProvider client={queryClient}>
          <div className="app-container">
            <RouterProvider router={router} />
          </div>
        </QueryClientProvider>
      </PersistGate>
    </Provider>
  );
};

export default App;
