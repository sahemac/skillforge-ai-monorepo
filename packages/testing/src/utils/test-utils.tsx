/**
 * Test utilities for SkillForge AI components and state management
 * Provides custom render functions and testing helpers
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { StateProvider } from '@skillforge-ai/shared-state';
import { ThemeProvider } from '@skillforge-ai/ui-kit';
import { EventBus } from '@skillforge-ai/shared-state';

// Test store configuration
function createTestStore(initialState = {}) {
  return configureStore({
    reducer: {
      // Add your reducers here based on the actual store structure
      auth: (state = { isAuthenticated: false, user: null }, action) => state,
      users: (state = { entities: {}, loading: false, error: null }, action) => state,
      projects: (state = { entities: {}, loading: false, error: null }, action) => state,
    },
    preloadedState: initialState,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: false,
      }),
  });
}

// Test query client configuration
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

// Custom render options
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialState?: any;
  store?: ReturnType<typeof createTestStore>;
  queryClient?: QueryClient;
  route?: string;
  withRouter?: boolean;
  withTheme?: boolean;
  withStateProvider?: boolean;
}

// All providers wrapper
function AllProviders({
  children,
  store,
  queryClient,
  route = '/',
  withRouter = true,
  withTheme = true,
  withStateProvider = true,
}: {
  children: React.ReactNode;
  store: ReturnType<typeof createTestStore>;
  queryClient: QueryClient;
  route?: string;
  withRouter?: boolean;
  withTheme?: boolean;
  withStateProvider?: boolean;
}) {
  // Set initial route
  if (withRouter && route !== '/') {
    window.history.pushState({}, 'Test page', route);
  }

  let content = children;

  // Wrap with Redux Provider
  content = <Provider store={store}>{content}</Provider>;

  // Wrap with React Query Provider
  content = <QueryClientProvider client={queryClient}>{content}</QueryClientProvider>;

  // Wrap with State Provider (includes Redux and React Query)
  if (withStateProvider) {
    content = <StateProvider showDevtools={false}>{content}</StateProvider>;
  }

  // Wrap with Theme Provider
  if (withTheme) {
    content = <ThemeProvider>{content}</ThemeProvider>;
  }

  // Wrap with Router
  if (withRouter) {
    content = <BrowserRouter>{content}</BrowserRouter>;
  }

  return <>{content}</>;
}

/**
 * Custom render function with all providers
 */
export function renderWithProviders(
  ui: ReactElement,
  {
    initialState = {},
    store = createTestStore(initialState),
    queryClient = createTestQueryClient(),
    route = '/',
    withRouter = true,
    withTheme = true,
    withStateProvider = true,
    ...renderOptions
  }: CustomRenderOptions = {}
): RenderResult & {
  store: ReturnType<typeof createTestStore>;
  queryClient: QueryClient;
} {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <AllProviders
        store={store}
        queryClient={queryClient}
        route={route}
        withRouter={withRouter}
        withTheme={withTheme}
        withStateProvider={withStateProvider}
      >
        {children}
      </AllProviders>
    );
  }

  const result = render(ui, { wrapper: Wrapper, ...renderOptions });

  return {
    ...result,
    store,
    queryClient,
  };
}

/**
 * Render function for components that only need theme provider
 */
export function renderWithTheme(
  ui: ReactElement,
  options: RenderOptions = {}
): RenderResult {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <ThemeProvider>{children}</ThemeProvider>;
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

/**
 * Render function for Redux-only components
 */
export function renderWithRedux(
  ui: ReactElement,
  {
    initialState = {},
    store = createTestStore(initialState),
    ...renderOptions
  }: {
    initialState?: any;
    store?: ReturnType<typeof createTestStore>;
  } & RenderOptions = {}
): RenderResult & { store: ReturnType<typeof createTestStore> } {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <Provider store={store}>{children}</Provider>;
  }

  const result = render(ui, { wrapper: Wrapper, ...renderOptions });

  return { ...result, store };
}

/**
 * Render function for React Query-only components
 */
export function renderWithQuery(
  ui: ReactElement,
  {
    queryClient = createTestQueryClient(),
    ...renderOptions
  }: {
    queryClient?: QueryClient;
  } & RenderOptions = {}
): RenderResult & { queryClient: QueryClient } {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  const result = render(ui, { wrapper: Wrapper, ...renderOptions });

  return { ...result, queryClient };
}

/**
 * Wait for loading states to complete
 */
export async function waitForLoadingToFinish() {
  const { findByTestId } = renderWithProviders(<div />);
  
  // Wait for any loading spinners to disappear
  await new Promise(resolve => setTimeout(resolve, 100));
}

/**
 * Mock IntersectionObserver for components that use it
 */
export function mockIntersectionObserver() {
  const mockIntersectionObserver = vi.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  });
  
  Object.defineProperty(window, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: mockIntersectionObserver,
  });
  
  Object.defineProperty(global, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: mockIntersectionObserver,
  });
}

/**
 * Mock ResizeObserver for components that use it
 */
export function mockResizeObserver() {
  const mockResizeObserver = vi.fn();
  mockResizeObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  });
  
  Object.defineProperty(window, 'ResizeObserver', {
    writable: true,
    configurable: true,
    value: mockResizeObserver,
  });
}

/**
 * Mock matchMedia for responsive components
 */
export function mockMatchMedia(matches = false) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

/**
 * Create a mock user event with common interactions
 */
export function createMockUserEvent() {
  return {
    click: vi.fn(),
    type: vi.fn(),
    clear: vi.fn(),
    tab: vi.fn(),
    hover: vi.fn(),
    unhover: vi.fn(),
    keyboard: vi.fn(),
  };
}

/**
 * Helper to trigger window resize events
 */
export function triggerResize(width = 1024, height = 768) {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
  
  window.dispatchEvent(new Event('resize'));
}

/**
 * Helper to clean up after tests
 */
export function cleanup() {
  // Clear EventBus
  EventBus.off();
  EventBus.clearHistory();
  
  // Clear localStorage
  localStorage.clear();
  
  // Clear sessionStorage
  sessionStorage.clear();
  
  // Reset window location
  window.history.replaceState({}, '', '/');
}

/**
 * Helper to create test IDs consistently
 */
export function createTestId(component: string, element?: string): string {
  return element ? `${component}-${element}` : component;
}

/**
 * Helper to wait for specific conditions
 */
export async function waitFor(
  condition: () => boolean | Promise<boolean>,
  timeout = 5000,
  interval = 100
): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const result = await condition();
    if (result) return;
    
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  throw new Error(`Condition not met within ${timeout}ms`);
}

/**
 * Helper to simulate async operations
 */
export function createAsyncHelper<T>(
  data: T,
  delay = 100,
  shouldReject = false
): Promise<T> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (shouldReject) {
        reject(new Error('Async operation failed'));
      } else {
        resolve(data);
      }
    }, delay);
  });
}

// Re-export testing library utilities
export * from '@testing-library/react';
export * from '@testing-library/jest-dom';
export { userEvent } from '@testing-library/user-event';
export { vi, expect, describe, it, test, beforeEach, afterEach, beforeAll, afterAll } from 'vitest';