import { fetchBaseQuery, type BaseQueryFn, type FetchArgs, type FetchBaseQueryError } from '@reduxjs/toolkit/query/react';
import { Mutex } from 'async-mutex';
import { RootState } from '@/store';
import { clearCredentials, setCredentials } from '@/store/authSlice';
import type { TokenResponse } from './authApi';

const mutex = new Mutex();
const baseQuery = fetchBaseQuery({
  baseUrl: 'http://localhost:8000/api/v1',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.accessToken;
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

export const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  await mutex.waitForUnlock();
  let result = await baseQuery(args, api, extraOptions);

  // Skip reauth logic for login and refresh endpoints themselves
  const url = typeof args === 'string' ? args : args.url;
  if (url.includes('/auth/login') || url.includes('/auth/refresh')) {
    return result;
  }

  if (result.error && result.error.status === 401) {
    if (!mutex.isLocked()) {
      const release = await mutex.acquire();
      try {
        const refreshToken = (api.getState() as RootState).auth.refreshToken;
        if (refreshToken) {
          const refreshResult = await baseQuery(
            {
              url: '/auth/refresh',
              method: 'POST',
              body: { refresh_token: refreshToken },
            },
            api,
            extraOptions
          );

          if (refreshResult.data) {
            api.dispatch(setCredentials({ tokens: refreshResult.data as TokenResponse }));
            result = await baseQuery(args, api, extraOptions);
          } else {
            api.dispatch(clearCredentials());
          }
        } else {
          api.dispatch(clearCredentials());
        }
      } finally {
        release();
      }
    } else {
      await mutex.waitForUnlock();
      result = await baseQuery(args, api, extraOptions);
    }
  }
  return result;
};
