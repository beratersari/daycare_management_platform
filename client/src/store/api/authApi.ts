/**
 * RTK Query API slice for authentication endpoints.
 * Mirrors the backend /api/v1/auth/* routes.
 */
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { RootState } from '@/store';

// ---------------------------------------------------------------------------
// Types (mirror backend schemas/auth.py)
// ---------------------------------------------------------------------------

export type UserRole = 'ADMIN' | 'DIRECTOR' | 'TEACHER' | 'PARENT';

export interface UserResponse {
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  school_id: number | null;
  phone: string | null;
  address: string | null;
  created_date: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface UserRegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  school_id?: number | null;
  phone?: string | null;
  address?: string | null;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8000/api/v1',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  endpoints: (builder) => ({
    /** POST /auth/register — create new user account */
    register: builder.mutation<UserResponse, UserRegisterRequest>({
      query: (data) => ({
        url: '/auth/register',
        method: 'POST',
        body: data,
      }),
    }),

    /** POST /auth/login — returns access + refresh tokens */
    login: builder.mutation<TokenResponse, UserLoginRequest>({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),

    /** POST /auth/refresh — exchange refresh token for new pair */
    refreshToken: builder.mutation<TokenResponse, RefreshTokenRequest>({
      query: (body) => ({
        url: '/auth/refresh',
        method: 'POST',
        body,
      }),
    }),

    /** POST /auth/logout — revoke all tokens for current user */
    logout: builder.mutation<void, void>({
      query: () => ({
        url: '/auth/logout',
        method: 'POST',
      }),
    }),

    /** GET /auth/me — fetch current user profile */
    getMe: builder.query<UserResponse, void>({
      query: () => '/auth/me',
    }),
  }),
});

export const {
  useRegisterMutation,
  useLoginMutation,
  useRefreshTokenMutation,
  useLogoutMutation,
  useGetMeQuery,
} = authApi;
