/**
 * Redux store with redux-persist for auth state persistence.
 * RTK Query cache is intentionally NOT persisted (always fresh from server).
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { combineReducers, configureStore } from '@reduxjs/toolkit';
import {
  FLUSH,
  PAUSE,
  PERSIST,
  persistReducer,
  persistStore,
  PURGE,
  REGISTER,
  REHYDRATE,
} from 'redux-persist';

import { authApi } from '@/store/api/authApi';
import { studentApi } from '@/store/api/studentApi';
import { classApi } from '@/store/api/classApi';
import { teacherApi } from '@/store/api/teacherApi';
import { parentApi } from '@/store/api/parentApi';
import { mealMenuApi } from '@/store/api/mealMenuApi';
import { schoolApi } from '@/store/api/schoolApi';
import authReducer, { clearCredentials } from '@/store/authSlice';

// Only persist the auth slice (tokens + user), not RTK Query cache
const authPersistConfig = {
  key: 'auth',
  storage: AsyncStorage,
  whitelist: ['accessToken', 'refreshToken', 'tokenExpiresAt', 'user'],
};

const rootReducer = combineReducers({
  auth: persistReducer(authPersistConfig, authReducer),
  [authApi.reducerPath]: authApi.reducer,
  [studentApi.reducerPath]: studentApi.reducer,
  [classApi.reducerPath]: classApi.reducer,
  [teacherApi.reducerPath]: teacherApi.reducer,
  [parentApi.reducerPath]: parentApi.reducer,
  [mealMenuApi.reducerPath]: mealMenuApi.reducer,
  [schoolApi.reducerPath]: schoolApi.reducer,
});

// Root reducer with reset capability for logout
const appReducer = (state: any, action: any) => {
  // Reset all state (including RTK Query cache) on logout
  if (action.type === clearCredentials.type) {
    // Keep the RTK Query middleware state structure but reset data
    const newState = rootReducer(undefined, action);
    // Ensure we don't get stuck in a hydrating state after logout
    return {
      ...newState,
      auth: {
        ...newState.auth,
        isHydrating: false,
      },
    };
  }
  return rootReducer(state, action);
};

export const store = configureStore({
  reducer: appReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // redux-persist dispatches non-serializable actions — suppress warnings
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }).concat(
      authApi.middleware,
      studentApi.middleware,
      classApi.middleware,
      teacherApi.middleware,
      parentApi.middleware,
      mealMenuApi.middleware,
      schoolApi.middleware,
    ),
});

export const persistor = persistStore(store);

// Inferred types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
