/**
 * Users slice for Redux store
 * Handles user entity state mutations via commands
 */

import { createSlice, createAsyncThunk, createEntityAdapter, PayloadAction } from '@reduxjs/toolkit';
import type { 
  User, 
  CreateUserCommandPayload, 
  UpdateUserCommandPayload 
} from '../../types';

// Entity adapter for normalized user storage
const usersAdapter = createEntityAdapter<User>({
  selectId: (user) => user.id,
  sortComparer: (a, b) => a.username.localeCompare(b.username),
});

// Initial state
const initialState = usersAdapter.getInitialState({
  loading: false,
  error: null as string | null,
});

// Async thunks for user commands
export const createUserCommand = createAsyncThunk<
  User,
  CreateUserCommandPayload,
  { rejectValue: string }
>(
  'users/create',
  async (payload, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const user = await response.json();
      return user;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to create user'
      );
    }
  }
);

export const updateUserCommand = createAsyncThunk<
  User,
  UpdateUserCommandPayload,
  { rejectValue: string }
>(
  'users/update',
  async ({ id, updates }, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const user = await response.json();
      return user;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to update user'
      );
    }
  }
);

export const deleteUserCommand = createAsyncThunk<
  string,
  string,
  { rejectValue: string }
>(
  'users/delete',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      return userId;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to delete user'
      );
    }
  }
);

export const activateUserCommand = createAsyncThunk<
  User,
  string,
  { rejectValue: string }
>(
  'users/activate',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}/activate`, {
        method: 'POST'
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const user = await response.json();
      return user;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to activate user'
      );
    }
  }
);

export const deactivateUserCommand = createAsyncThunk<
  User,
  string,
  { rejectValue: string }
>(
  'users/deactivate',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}/deactivate`, {
        method: 'POST'
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const user = await response.json();
      return user;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to deactivate user'
      );
    }
  }
);

// Users slice
const usersSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    // Synchronous reducers for immediate state updates
    addUser: usersAdapter.addOne,
    addUsers: usersAdapter.addMany,
    updateUser: usersAdapter.updateOne,
    removeUser: usersAdapter.removeOne,
    clearUsers: usersAdapter.removeAll,
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    // Create user command
    builder
      .addCase(createUserCommand.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createUserCommand.fulfilled, (state, action) => {
        state.loading = false;
        usersAdapter.addOne(state, action.payload);
      })
      .addCase(createUserCommand.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to create user';
      });

    // Update user command
    builder
      .addCase(updateUserCommand.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserCommand.fulfilled, (state, action) => {
        state.loading = false;
        usersAdapter.upsertOne(state, action.payload);
      })
      .addCase(updateUserCommand.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update user';
      });

    // Delete user command
    builder
      .addCase(deleteUserCommand.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteUserCommand.fulfilled, (state, action) => {
        state.loading = false;
        usersAdapter.removeOne(state, action.payload);
      })
      .addCase(deleteUserCommand.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete user';
      });

    // Activate user command
    builder
      .addCase(activateUserCommand.fulfilled, (state, action) => {
        usersAdapter.upsertOne(state, action.payload);
      })
      .addCase(activateUserCommand.rejected, (state, action) => {
        state.error = action.payload || 'Failed to activate user';
      });

    // Deactivate user command
    builder
      .addCase(deactivateUserCommand.fulfilled, (state, action) => {
        usersAdapter.upsertOne(state, action.payload);
      })
      .addCase(deactivateUserCommand.rejected, (state, action) => {
        state.error = action.payload || 'Failed to deactivate user';
      });
  }
});

// Export selectors
export const {
  selectAll: selectAllUsers,
  selectById: selectUserById,
  selectIds: selectUserIds,
  selectEntities: selectUserEntities,
  selectTotal: selectUsersTotal
} = usersAdapter.getSelectors();

export const {
  addUser,
  addUsers,
  updateUser,
  removeUser,
  clearUsers,
  setLoading,
  setError,
  clearError
} = usersSlice.actions;

export default usersSlice;