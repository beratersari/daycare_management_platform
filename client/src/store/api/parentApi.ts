/**
 * RTK Query API slice for Parent endpoints.
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithReauth } from './baseQuery';
import type { UserResponse } from './authApi';
import type { StudentResponse } from './studentApi';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PaginatedResponse<T> {
  data: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

export const parentApi = createApi({
  reducerPath: 'parentApi',
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    /** GET /parents — list parents with pagination */
    listParents: builder.query<PaginatedResponse<UserResponse>, { page?: number; pageSize?: number; search?: string }>({
      query: ({ page = 1, pageSize = 10, search }) => ({
        url: '/parents',
        params: { page, page_size: pageSize, search },
      }),
    }),

    /** GET /parents/me/children — get children for current parent user */
    getMyChildren: builder.query<StudentResponse[], void>({
      query: () => '/parents/me/children',
    }),
  }),
});

export const { useListParentsQuery, useGetMyChildrenQuery } = parentApi;
