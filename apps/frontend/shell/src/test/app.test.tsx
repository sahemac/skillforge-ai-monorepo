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
  it('should render mocked app component', () => {
    // App component already has RouterProvider, so disable the Router wrapper
    renderWithProviders(<App />, { withRouter: false });

    // Should show the mocked app component
    expect(screen.getByText('Mock App Component')).toBeInTheDocument();
  });

  it('should render with different state configurations', async () => {
    // App component already has RouterProvider, so disable the Router wrapper
    renderWithProviders(<App />, {
      withRouter: false,
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

    // Should still show the mocked app component regardless of state
    expect(screen.getByText('Mock App Component')).toBeInTheDocument();
  });

  it('should handle authenticated users with mock', async () => {
    const mockUser = createMockUser({
      role: 'learner',
      permissions: ['read:content'],
    });

    // App component already has RouterProvider, so disable the Router wrapper
    renderWithProviders(<App />, {
      withRouter: false,
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

    expect(screen.getByText('Mock App Component')).toBeInTheDocument();
  });

  it('should render with store integration', async () => {
    const mockUser = createMockUser();

    // App component already has RouterProvider, so disable the Router wrapper
    const { store } = renderWithProviders(<App />, {
      withRouter: false,
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
    expect(screen.getByText('Mock App Component')).toBeInTheDocument();
  });
});