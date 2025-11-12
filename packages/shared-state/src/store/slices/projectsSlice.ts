/**
 * Projects slice for Redux store
 * Handles project entity state mutations via commands
 */

import { createSlice, createAsyncThunk, createEntityAdapter, PayloadAction } from '@reduxjs/toolkit';
import type { 
  Project, 
  CreateProjectCommandPayload, 
  UpdateProjectCommandPayload 
} from '../../types';

// Entity adapter for normalized project storage
const projectsAdapter = createEntityAdapter<Project>({
  sortComparer: (a: Project, b: Project) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
});

// Initial state
const initialState = projectsAdapter.getInitialState({
  loading: false,
  error: null as string | null,
});

// Async thunks for project commands
export const createProjectCommand = createAsyncThunk<
  Project,
  CreateProjectCommandPayload,
  { rejectValue: string }
>(
  'projects/create',
  async (payload, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const project = await response.json();
      return project;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to create project'
      );
    }
  }
);

export const updateProjectCommand = createAsyncThunk<
  Project,
  UpdateProjectCommandPayload,
  { rejectValue: string }
>(
  'projects/update',
  async ({ id, updates }, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/projects/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const project = await response.json();
      return project;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to update project'
      );
    }
  }
);

export const deleteProjectCommand = createAsyncThunk<
  string,
  string,
  { rejectValue: string }
>(
  'projects/delete',
  async (projectId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/projects/${projectId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      return projectId;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to delete project'
      );
    }
  }
);

export const publishProjectCommand = createAsyncThunk<
  Project,
  string,
  { rejectValue: string }
>(
  'projects/publish',
  async (projectId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/publish`, {
        method: 'POST'
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const project = await response.json();
      return project;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to publish project'
      );
    }
  }
);

export const archiveProjectCommand = createAsyncThunk<
  Project,
  string,
  { rejectValue: string }
>(
  'projects/archive',
  async (projectId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/archive`, {
        method: 'POST'
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const project = await response.json();
      return project;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to archive project'
      );
    }
  }
);

export const duplicateProjectCommand = createAsyncThunk<
  Project,
  { projectId: string; title?: string },
  { rejectValue: string }
>(
  'projects/duplicate',
  async ({ projectId, title }, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/duplicate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
      }

      const project = await response.json();
      return project;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to duplicate project'
      );
    }
  }
);

// Projects slice
const projectsSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {
    // Synchronous reducers for immediate state updates
    addProject: projectsAdapter.addOne,
    addProjects: projectsAdapter.addMany,
    updateProject: projectsAdapter.updateOne,
    removeProject: projectsAdapter.removeOne,
    clearProjects: projectsAdapter.removeAll,
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    // Optimistic updates for better UX
    optimisticUpdateStatus: (
      state, 
      action: PayloadAction<{ id: string; status: Project['status'] }>
    ) => {
      const { id, status } = action.payload;
      projectsAdapter.updateOne(state, {
        id,
        changes: { status, updatedAt: new Date().toISOString() }
      });
    }
  },
  extraReducers: (builder) => {
    // Create project command
    builder
      .addCase(createProjectCommand.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createProjectCommand.fulfilled, (state, action) => {
        state.loading = false;
        projectsAdapter.addOne(state, action.payload);
      })
      .addCase(createProjectCommand.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to create project';
      });

    // Update project command
    builder
      .addCase(updateProjectCommand.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProjectCommand.fulfilled, (state, action) => {
        state.loading = false;
        projectsAdapter.upsertOne(state, action.payload);
      })
      .addCase(updateProjectCommand.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update project';
      });

    // Delete project command
    builder
      .addCase(deleteProjectCommand.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteProjectCommand.fulfilled, (state, action) => {
        state.loading = false;
        projectsAdapter.removeOne(state, action.payload);
      })
      .addCase(deleteProjectCommand.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete project';
      });

    // Publish project command
    builder
      .addCase(publishProjectCommand.fulfilled, (state, action) => {
        projectsAdapter.upsertOne(state, action.payload);
      })
      .addCase(publishProjectCommand.rejected, (state, action) => {
        state.error = action.payload || 'Failed to publish project';
      });

    // Archive project command
    builder
      .addCase(archiveProjectCommand.fulfilled, (state, action) => {
        projectsAdapter.upsertOne(state, action.payload);
      })
      .addCase(archiveProjectCommand.rejected, (state, action) => {
        state.error = action.payload || 'Failed to archive project';
      });

    // Duplicate project command
    builder
      .addCase(duplicateProjectCommand.fulfilled, (state, action) => {
        projectsAdapter.addOne(state, action.payload);
      })
      .addCase(duplicateProjectCommand.rejected, (state, action) => {
        state.error = action.payload || 'Failed to duplicate project';
      });
  }
});

// Export selectors
export const {
  selectAll: selectAllProjects,
  selectById: selectProjectById,
  selectIds: selectProjectIds,
  selectEntities: selectProjectEntities,
  selectTotal: selectProjectsTotal
} = projectsAdapter.getSelectors();

export const {
  addProject,
  addProjects,
  updateProject,
  removeProject,
  clearProjects,
  setLoading,
  setError,
  clearError,
  optimisticUpdateStatus
} = projectsSlice.actions;

export default projectsSlice;