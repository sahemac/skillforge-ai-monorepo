/**
 * Redux Toolkit store configuration for command handling (write operations)
 * Implements CQRS pattern with Redux for state mutations
 */

import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import authSlice from './slices/authSlice';
import usersSlice from './slices/usersSlice';
import projectsSlice from './slices/projectsSlice';
import type { RootState } from '../types';

// Persist configuration
const persistConfig = {
  key: 'skillforge-ai',
  storage,
  whitelist: ['auth'], // Only persist auth state
  version: 1,
};

// Root reducer
const rootReducer = combineReducers({
  auth: authSlice.reducer,
  users: usersSlice.reducer,
  projects: projectsSlice.reducer,
});

// Persisted reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Store configuration
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export const persistor = persistStore(store);

// Types
export type AppDispatch = typeof store.dispatch;
export type AppRootState = ReturnType<typeof store.getState>;

// Re-export for convenience
export { authSlice, usersSlice, projectsSlice };
export type { RootState };