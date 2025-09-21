/**
 * Combined state provider for CQRS implementation
 * Sets up both Redux store and TanStack Query client
 */

import React from 'react';
import { Provider as ReduxProvider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { QueryClientProvider, ReactQueryDevtools } from '@tanstack/react-query';
import { store, persistor } from '../store';
import { queryClient } from '../queries';

interface StateProviderProps {
  children: React.ReactNode;
  showDevtools?: boolean;
}

/**
 * Main state provider that combines Redux and TanStack Query
 * Provides both command (write) and query (read) capabilities
 */
export function StateProvider({ children, showDevtools = process.env.NODE_ENV === 'development' }: StateProviderProps) {
  return (
    <ReduxProvider store={store}>
      <PersistGate 
        loading={<StateLoadingFallback />} 
        persistor={persistor}
      >
        <QueryClientProvider client={queryClient}>
          {children}
          {showDevtools && <ReactQueryDevtools initialIsOpen={false} />}
        </QueryClientProvider>
      </PersistGate>
    </ReduxProvider>
  );
}

/**
 * Loading fallback while persisted state is being rehydrated
 */
function StateLoadingFallback() {
  return (
    <div 
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <div style={{ 
          width: '32px', 
          height: '32px', 
          border: '3px solid #f3f3f3',
          borderTop: '3px solid #3498db',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 16px'
        }} />
        <p style={{ margin: 0, color: '#666' }}>Loading SkillForge AI...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
}

export default StateProvider;