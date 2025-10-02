import React, { Suspense, lazy } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '@skillforge-ai/shared-state';
import { AppLayout } from '@/presentation/layouts/app-layout';
import { ErrorBoundary } from '@/presentation/components/error-boundary/error-boundary';
import { LoadingSpinner } from '@/presentation/components/loading/loading-spinner';
import { Dashboard } from '@/presentation/pages/dashboard';
import { LandingPage } from '@/presentation/pages/landing-page';

// Lazy load auth module pages
const LoginPage = lazy(() => import('@/modules/auth/pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/modules/auth/pages/RegisterPage').then(m => ({ default: m.RegisterPage })));
const ForgotPasswordPage = lazy(() => import('@/modules/auth/pages/ForgotPasswordPage').then(m => ({ default: m.ForgotPasswordPage })));

// Lazy load learner module pages
const LearnerDashboard = lazy(() => import('@/modules/learner/pages/LearnerDashboard').then(m => ({ default: m.LearnerDashboard })));

// Lazy load company module pages
const CompanyDashboard = lazy(() => import('@/modules/company/pages/CompanyDashboard').then(m => ({ default: m.CompanyDashboard })));
const ProjectsList = lazy(() => import('@/modules/company/pages/ProjectsList').then(m => ({ default: m.ProjectsList })));

// TODO: Lazy load admin module when migrated
// const AdminUserList = lazy(() => import('@/modules/admin/pages/UserListPage'));

// Route Guard Component
const ProtectedRoute: React.FC<{ 
  children: React.ReactNode;
  requiredPermissions?: string[];
  fallbackPath?: string;
}> = ({ 
  children, 
  requiredPermissions = [], 
  fallbackPath = '/auth/login' 
}) => {
  const { isAuthenticated, permissions } = useSelector((state: RootState) => state.auth);
  
  // Check authentication
  if (!isAuthenticated) {
    return <Navigate to={fallbackPath} replace />;
  }
  
  // Check permissions if required
  if (requiredPermissions.length > 0) {
    const hasAllPermissions = requiredPermissions.every(permission =>
      permissions.includes(permission)
    );
    
    if (!hasAllPermissions) {
      return <Navigate to="/unauthorized" replace />;
    }
  }
  
  return <>{children}</>;
};

// Public Route Component (redirect if authenticated)
const PublicRoute: React.FC<{
  children: React.ReactNode;
  redirectPath?: string;
  allowAuthenticated?: boolean;
}> = ({ children, redirectPath = '/dashboard', allowAuthenticated = false }) => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  if (isAuthenticated && !allowAuthenticated) {
    return <Navigate to={redirectPath} replace />;
  }

  return <>{children}</>;
};

// Wrapper component with error boundary and suspense
const PageWrapper: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => (
  <ErrorBoundary>
    <Suspense fallback={<LoadingSpinner />}>
      {children}
    </Suspense>
  </ErrorBoundary>
);

// Error pages
const NotFound: React.FC = () => (
  <div className="flex flex-col items-center justify-center min-h-screen">
    <h1 className="text-4xl font-bold text-neutral-900 mb-4">404</h1>
    <p className="text-lg text-neutral-600 mb-8">Page not found</p>
    <a href="/" className="btn btn-primary">Go Home</a>
  </div>
);

const Unauthorized: React.FC = () => (
  <div className="flex flex-col items-center justify-center min-h-screen">
    <h1 className="text-4xl font-bold text-error-600 mb-4">403</h1>
    <p className="text-lg text-neutral-600 mb-8">Access denied</p>
    <a href="/" className="btn btn-primary">Go Home</a>
  </div>
);

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/auth',
    element: (
      <PublicRoute>
        <PageWrapper>
          <div />
        </PageWrapper>
      </PublicRoute>
    ),
    children: [
      {
        path: 'login',
        element: (
          <PageWrapper>
            <LoginPage />
          </PageWrapper>
        ),
      },
      {
        path: 'register',
        element: (
          <PageWrapper>
            <RegisterPage />
          </PageWrapper>
        ),
      },
      {
        path: 'forgot-password',
        element: (
          <PageWrapper>
            <ForgotPasswordPage />
          </PageWrapper>
        ),
      },
    ],
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
    ],
  },
  {
    path: '/learner',
    element: (
      <ProtectedRoute requiredPermissions={['read:content']}>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'dashboard',
        element: (
          <PageWrapper>
            <LearnerDashboard />
          </PageWrapper>
        ),
      },
    ],
  },
  {
    path: '/company',
    element: (
      <ProtectedRoute requiredPermissions={['read:company']}>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'dashboard',
        element: (
          <PageWrapper>
            <CompanyDashboard />
          </PageWrapper>
        ),
      },
      {
        path: 'projects',
        element: (
          <PageWrapper>
            <ProjectsList />
          </PageWrapper>
        ),
      },
    ],
  },
  {
    path: '/admin',
    element: (
      <ProtectedRoute requiredPermissions={['read:admin', 'write:admin']}>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'users',
        element: (
          <PageWrapper>
            <div className="p-8">
              <h1 className="text-2xl font-bold">Admin - Users</h1>
              <p className="mt-4 text-gray-600">Module admin en cours de migration...</p>
            </div>
          </PageWrapper>
        ),
      },
    ],
  },
  {
    path: '/unauthorized',
    element: <Unauthorized />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};