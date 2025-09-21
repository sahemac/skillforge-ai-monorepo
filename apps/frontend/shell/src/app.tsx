import React from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@skillforge-ai/ui-kit';
import { createDefaultSDK } from '@skillforge-ai/api-client';
import { setupTestEnvironment } from '@skillforge-ai/testing';
import { store, persistor, queryClient } from '@skillforge-ai/shared-state';
import { eventBus } from '@skillforge-ai/shared-state';
import { authSignal, globalSignals } from '@skillforge-ai/shared-state';
import { AppRouter } from '@/presentation/router/app-router';
import { ErrorBoundary } from '@/presentation/components/error-boundary/error-boundary';
import { LoadingSpinner } from '@/presentation/components/loading/loading-spinner';
import '@skillforge-ai/ui-kit/styles';
import '@/presentation/styles/global.css';

// Initialize SDK
const sdk = createDefaultSDK({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  enableLogging: import.meta.env.DEV,
  onAuthError: () => {
    // Emit auth error event through EventBus
    eventBus.emit('auth:error', { 
      message: 'Authentication failed', 
      timestamp: Date.now() 
    });
    
    // Clear auth signal
    authSignal.value = {
      user: null,
      token: null,
      isAuthenticated: false,
      permissions: [],
    };
  },
});

// Setup test environment in development
if (import.meta.env.DEV) {
  setupTestEnvironment();
}

// Initialize signals with initial state
const initializeSignals = () => {
  // Listen to auth changes and sync with signals
  eventBus.on('auth:login', (payload) => {
    authSignal.value = {
      user: payload.user,
      token: payload.token,
      isAuthenticated: true,
      permissions: payload.permissions || [],
    };
  });

  eventBus.on('auth:logout', () => {
    authSignal.value = {
      user: null,
      token: null,
      isAuthenticated: false,
      permissions: [],
    };
  });

  // Initialize UI state
  globalSignals.ui.theme.value = 'light';
  globalSignals.ui.sidebarOpen.value = false;
  globalSignals.ui.notifications.value = [];
  globalSignals.ui.loading.value = false;
};

// Initialize signals on app start
initializeSignals();

export const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = React.useState(false);

  React.useEffect(() => {
    // Listen for theme changes
    const handleThemeChange = () => {
      setIsDarkMode(globalSignals.ui.theme.value === 'dark');
    };

    // Subscribe to theme signal changes
    globalSignals.ui.theme.subscribe(handleThemeChange);

    return () => {
      // Cleanup subscriptions
      globalSignals.ui.theme.unsubscribe(handleThemeChange);
    };
  }, []);

  return (
    <ErrorBoundary>
      <Provider store={store}>
        <PersistGate loading={<LoadingSpinner />} persistor={persistor}>
          <QueryClientProvider client={queryClient}>
            <ThemeProvider defaultDark={isDarkMode}>
              <div className="app-container">
                <AppRouter />
                {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
              </div>
            </ThemeProvider>
          </QueryClientProvider>
        </PersistGate>
      </Provider>
    </ErrorBoundary>
  );
};

export default App;