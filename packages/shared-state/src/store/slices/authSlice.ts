/**
 * Authentication slice for Redux store
 * Handles authentication state mutations via commands
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { 
  AuthState, 
  LoginCommandPayload, 
  User,
  AuthenticationError 
} from '../../types';

// Initial state
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  refreshToken: null,
  expiresAt: null,
  permissions: []
};

// Async thunks for authentication commands
export const loginCommand = createAsyncThunk<
  { user: User; token: string; refreshToken: string; expiresAt: number },
  LoginCommandPayload,
  { rejectValue: string }
>(
  'auth/login',
  async (payload, { rejectWithValue }) => {
    try {
      // This would integrate with actual API client
      // For now, simulating the API call
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new AuthenticationError('Invalid credentials');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Login failed'
      );
    }
  }
);

export const logoutCommand = createAsyncThunk<
  void,
  void,
  { rejectValue: string }
>(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Logout failed'
      );
    }
  }
);

export const refreshTokenCommand = createAsyncThunk<
  { token: string; expiresAt: number },
  string,
  { rejectValue: string }
>(
  'auth/refreshToken',
  async (refreshToken, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken })
      });

      if (!response.ok) {
        throw new AuthenticationError('Token refresh failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Token refresh failed'
      );
    }
  }
);

// Auth slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Synchronous reducers for immediate state updates
    setAuthenticated: (state, action: PayloadAction<boolean>) => {
      state.isAuthenticated = action.payload;
    },
    setUser: (state, action: PayloadAction<User | null>) => {
      state.user = action.payload;
    },
    updateUserProfile: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        Object.assign(state.user, action.payload);
      }
    },
    setPermissions: (state, action: PayloadAction<string[]>) => {
      state.permissions = action.payload;
    },
    clearAuth: (state) => {
      return initialState;
    }
  },
  extraReducers: (builder) => {
    // Login command
    builder
      .addCase(loginCommand.fulfilled, (state, action) => {
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.expiresAt = action.payload.expiresAt;
        // Extract permissions from user role
        state.permissions = extractPermissions(action.payload.user.role);
      })
      .addCase(loginCommand.rejected, (state) => {
        return initialState;
      });

    // Logout command
    builder
      .addCase(logoutCommand.fulfilled, () => {
        return initialState;
      });

    // Refresh token command
    builder
      .addCase(refreshTokenCommand.fulfilled, (state, action) => {
        state.token = action.payload.token;
        state.expiresAt = action.payload.expiresAt;
      })
      .addCase(refreshTokenCommand.rejected, () => {
        return initialState;
      });
  }
});

// Helper function to extract permissions from user role
function extractPermissions(role: User['role']): string[] {
  const rolePermissions: Record<User['role'], string[]> = {
    admin: [
      'users:read',
      'users:write',
      'users:delete',
      'projects:read',
      'projects:write',
      'projects:delete',
      'system:admin'
    ],
    company: [
      'users:read',
      'projects:read',
      'projects:write',
      'company:manage'
    ],
    learner: [
      'projects:read',
      'profile:write'
    ]
  };

  return rolePermissions[role] || [];
}

export const {
  setAuthenticated,
  setUser,
  updateUserProfile,
  setPermissions,
  clearAuth
} = authSlice.actions;

export default authSlice;