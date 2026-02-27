/**
 * Redux slice for local authentication state.
 * Stores tokens and the current user profile in persisted Redux state.
 */
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { TokenResponse, UserResponse } from '@/store/api/authApi';

export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  /** Unix timestamp (ms) when the access token expires */
  tokenExpiresAt: number | null;
  user: UserResponse | null;
  /** true while the app is rehydrating persisted state on startup */
  isHydrating: boolean;
}

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  tokenExpiresAt: null,
  user: null,
  isHydrating: true,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /** Called after a successful login or token refresh */
    setCredentials(
      state,
      action: PayloadAction<{ tokens: TokenResponse; user?: UserResponse }>,
    ) {
      const { tokens, user } = action.payload;
      state.accessToken = tokens.access_token;
      state.refreshToken = tokens.refresh_token;
      state.tokenExpiresAt = Date.now() + tokens.expires_in * 1000;
      if (user) {
        state.user = user;
      }
    },

    /** Called after fetching /auth/me */
    setUser(state, action: PayloadAction<UserResponse>) {
      state.user = action.payload;
    },

    /** Clear all auth state (logout) */
    clearCredentials(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.tokenExpiresAt = null;
      state.user = null;
    },

    /** Mark rehydration as complete */
    setHydrated(state) {
      state.isHydrating = false;
    },
  },
});

export const { setCredentials, setUser, clearCredentials, setHydrated } =
  authSlice.actions;

export default authSlice.reducer;

// ---------------------------------------------------------------------------
// Selectors
// ---------------------------------------------------------------------------

import { RootState } from '@/store';

export const selectIsAuthenticated = (state: RootState) =>
  state.auth.accessToken !== null;

export const selectCurrentUser = (state: RootState) => state.auth.user;

export const selectAccessToken = (state: RootState) => state.auth.accessToken;

export const selectRefreshToken = (state: RootState) =>
  state.auth.refreshToken;

export const selectIsHydrating = (state: RootState) => state.auth.isHydrating;
