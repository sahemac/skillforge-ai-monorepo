import React, { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '@skillforge-ai/shared-state';
import { globalSignals } from '@skillforge-ai/shared-state';
import { Navigation } from '@/presentation/components/navigation/navigation';
import { Sidebar } from '@/presentation/components/navigation/sidebar';
import { NotificationCenter } from '@/presentation/components/notifications/notification-center';
import { ErrorBoundary } from '@/presentation/components/error-boundary/error-boundary';
import { LoadingSpinner } from '@/presentation/components/loading/loading-spinner';
import { useSignal } from '@preact/signals-react';

export const AppLayout: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const sidebarOpen = useSignal(globalSignals.ui.sidebarOpen);
  const loading = useSignal(globalSignals.ui.loading);
  const notifications = useSignal(globalSignals.ui.notifications);

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 transition-colors duration-200">
      {/* Global Loading Overlay */}
      {loading.value && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-20 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-6 shadow-xl">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-sm text-neutral-600 dark:text-neutral-400">
              Loading...
            </p>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen.value}
        onClose={() => globalSignals.ui.sidebarOpen.value = false}
      />

      {/* Main Layout */}
      <div className={`flex flex-col min-h-screen transition-all duration-300 ${
        sidebarOpen.value ? 'lg:ml-64' : ''
      }`}>
        {/* Header Navigation */}
        <Navigation />

        {/* Main Content */}
        <main className="flex-1 relative">
          <div className="container mx-auto px-4 py-6 max-w-7xl">
            <ErrorBoundary>
              <Suspense fallback={
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner size="lg" />
                </div>
              }>
                <Outlet />
              </Suspense>
            </ErrorBoundary>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white dark:bg-neutral-800 border-t border-neutral-200 dark:border-neutral-700 py-6">
          <div className="container mx-auto px-4 max-w-7xl">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center space-x-4 mb-4 md:mb-0">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  © 2025 SkillForge AI. All rights reserved.
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <span className="text-xs text-neutral-500 dark:text-neutral-500">
                  Welcome back, {user?.firstName || 'User'}
                </span>
                
                {/* Version Info */}
                <div className="flex items-center space-x-2 text-xs text-neutral-400 dark:text-neutral-500">
                  <span>v1.0.0</span>
                  <span className="w-1 h-1 bg-neutral-300 rounded-full"></span>
                  <span className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                    <span>Online</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>

      {/* Notification Center */}
      <NotificationCenter 
        notifications={notifications.value}
        onDismiss={(id) => {
          globalSignals.ui.notifications.value = notifications.value.filter(n => n.id !== id);
        }}
        onClearAll={() => {
          globalSignals.ui.notifications.value = [];
        }}
      />

      {/* Sidebar Overlay for Mobile */}
      {sidebarOpen.value && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-25 lg:hidden"
          onClick={() => globalSignals.ui.sidebarOpen.value = false}
        />
      )}
    </div>
  );
};