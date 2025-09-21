/**
 * Integration tests for the main App component
 * Tests the complete integration of all systems
 */

import React from 'react';
import { describe, it, expect, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders, createMockUser } from '@skillforge-ai/testing';
import { App } from '../app';

describe('App Integration', () => {
  it('should render loading state initially', () => {
    renderWithProviders(<App />);
    
    // Should show loading spinner during initial render
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('should render auth layout for unauthenticated users', async () => {
    renderWithProviders(<App />, {
      preloadedState: {
        auth: {
          user: null,
          token: null,
          isAuthenticated: false,
          permissions: [],
          loading: false,
          error: null,
        },
      },
    });

    await waitFor(() => {
      expect(screen.getByText('Welcome to SkillForge AI')).toBeInTheDocument();
      expect(screen.getByText('Get Started')).toBeInTheDocument();
    });
  });

  it('should render app layout for authenticated users', async () => {
    const mockUser = createMockUser({
      role: 'learner',
      permissions: ['read:content'],
    });

    renderWithProviders(<App />, {
      preloadedState: {
        auth: {
          user: mockUser,
          token: 'mock-token',
          isAuthenticated: true,
          permissions: ['read:content'],
          loading: false,
          error: null,
        },
      },
    });

    await waitFor(() => {
      expect(screen.getByText(`Good morning, ${mockUser.firstName}!`)).toBeInTheDocument();
      expect(screen.getByText('SkillForge AI')).toBeInTheDocument();
    });
  });

  it('should handle theme changes', async () => {
    const mockUser = createMockUser();

    renderWithProviders(<App />, {
      preloadedState: {
        auth: {
          user: mockUser,
          token: 'mock-token',
          isAuthenticated: true,
          permissions: ['read:content'],
          loading: false,
          error: null,
        },
      },
    });

    // Find theme toggle button
    const themeToggle = screen.getByLabelText('Toggle theme');
    expect(themeToggle).toBeInTheDocument();

    // Click to toggle theme
    await userEvent.click(themeToggle);

    // Should update the theme (this would require checking CSS classes or theme context)
    await waitFor(() => {
      // The actual implementation would depend on how theme is applied
      expect(document.documentElement).toHaveClass('dark');
    });
  });

  it('should handle error states gracefully', async () => {
    renderWithProviders(<App />, {
      preloadedState: {
        auth: {
          user: null,
          token: null,
          isAuthenticated: false,
          permissions: [],
          loading: false,
          error: 'Authentication failed',
        },
      },
    });

    await waitFor(() => {
      // Should still render the app, error handling should be graceful
      expect(screen.getByText('Welcome to SkillForge AI')).toBeInTheDocument();
    });
  });

  it('should integrate with Redux and React Query providers', async () => {
    const mockUser = createMockUser();

    const { store } = renderWithProviders(<App />, {
      preloadedState: {
        auth: {
          user: mockUser,
          token: 'mock-token',
          isAuthenticated: true,
          permissions: ['read:content', 'read:users'],
          loading: false,
          error: null,
        },
      },
    });

    // Check that Redux store is properly connected
    const state = store.getState();
    expect(state.auth.isAuthenticated).toBe(true);
    expect(state.auth.user).toEqual(mockUser);

    // Check that React Query is working (stats should load)
    await waitFor(() => {
      // This assumes the dashboard loads stats from React Query
      expect(screen.getByText('Total Users')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('should handle micro-frontend routing', async () => {
    const mockUser = createMockUser({
      permissions: ['read:content', 'read:company', 'read:admin'],
    });

    renderWithProviders(<App />, {
      preloadedState: {
        auth: {
          user: mockUser,
          token: 'mock-token',
          isAuthenticated: true,
          permissions: ['read:content', 'read:company', 'read:admin'],
          loading: false,
          error: null,
        },
      },
      initialEntries: ['/'],
    });

    await waitFor(() => {
      // Should show dashboard with role-based features
      expect(screen.getByText('Learning Path')).toBeInTheDocument();
      expect(screen.getByText('Company Portal')).toBeInTheDocument();
      expect(screen.getByText('Admin Panel')).toBeInTheDocument();
    });
  });

  it('should handle permission-based rendering', async () => {
    const mockUser = createMockUser({
      permissions: ['read:content'], // Only learning permissions
    });

    renderWithProviders(<App />, {
      preloadedState: {
        auth: {
          user: mockUser,
          token: 'mock-token',
          isAuthenticated: true,
          permissions: ['read:content'],
          loading: false,
          error: null,
        },
      },
    });

    await waitFor(() => {
      // Should only show learning features
      expect(screen.getByText('Learning Path')).toBeInTheDocument();
      expect(screen.queryByText('Company Portal')).not.toBeInTheDocument();
      expect(screen.queryByText('Admin Panel')).not.toBeInTheDocument();
    });
  });
});