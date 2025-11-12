import React, { Suspense, lazy } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { LoadingSpinner } from '@/presentation/components/loading/loading-spinner';
import '@/presentation/styles/design-tokens.css';
import '@/presentation/styles/global.css';

// Public pages (no lazy load for better initial performance)
import { LandingPage } from '@/modules/public/pages/LandingPage';
import { MissionPage } from '@/modules/public/pages/MissionPage';
import { ContactPage } from '@/modules/public/pages/ContactPage';

// Lazy load auth pages
const LoginPage = lazy(() => import('@/modules/auth/pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/modules/auth/pages/RegisterPage').then(m => ({ default: m.RegisterPage })));

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/mission',
    element: <MissionPage />,
  },
  {
    path: '/contact',
    element: <ContactPage />,
  },
  {
    path: '/login',
    element: (
      <Suspense fallback={<LoadingSpinner />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    path: '/register',
    element: (
      <Suspense fallback={<LoadingSpinner />}>
        <RegisterPage />
      </Suspense>
    ),
  },
]);

export const App = () => {
  return <RouterProvider router={router} />;
};
