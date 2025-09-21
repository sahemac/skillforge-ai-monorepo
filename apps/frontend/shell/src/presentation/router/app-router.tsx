import React, { Suspense, lazy } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '@skillforge-ai/shared-state';
import { authSignal } from '@skillforge-ai/shared-state';
import { AppLayout } from '@/presentation/layouts/app-layout';
import { AuthLayout } from '@/presentation/layouts/auth-layout';
import { ErrorBoundary } from '@/presentation/components/error-boundary/error-boundary';
import { LoadingSpinner } from '@/presentation/components/loading/loading-spinner';
import { Dashboard } from '@/presentation/pages/dashboard';

// Lazy load micro-frontends
const AuthApp = lazy(() => import('auth/App'));
const LearnerApp = lazy(() => import('learner/App'));
const CompanyApp = lazy(() => import('company/App'));
const AdminApp = lazy(() => import('admin/App'));

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
}> = ({ children, redirectPath = '/' }) => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  
  if (isAuthenticated) {
    return <Navigate to={redirectPath} replace />;
  }
  
  return <>{children}</>;
};

// Wrapper components for micro-frontends
const MicroFrontendWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
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
    path: '/auth/*',
    element: (
      <PublicRoute>
        <AuthLayout>
          <MicroFrontendWrapper>
            <AuthApp />
          </MicroFrontendWrapper>
        </AuthLayout>
      </PublicRoute>
    ),
  },
  {
    path: '/',
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
      {
        path: 'learning/*',
        element: (
          <ProtectedRoute requiredPermissions={['read:content']}>
            <MicroFrontendWrapper>
              <LearnerApp />
            </MicroFrontendWrapper>
          </ProtectedRoute>
        ),
      },
      {
        path: 'company/*',
        element: (
          <ProtectedRoute requiredPermissions={['read:company']}>
            <MicroFrontendWrapper>
              <CompanyApp />
            </MicroFrontendWrapper>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/*',
        element: (
          <ProtectedRoute requiredPermissions={['read:admin', 'write:admin']}>
            <MicroFrontendWrapper>
              <AdminApp />
            </MicroFrontendWrapper>
          </ProtectedRoute>
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