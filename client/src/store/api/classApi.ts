/**
 * RTK Query API slice for Class endpoints.
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithReauth } from './baseQuery';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ClassResponse {
  class_id: number;
  school_id: number;
  class_name: string;
  capacity: number;
  age_group_min: number | null;
  age_group_max: number | null;
  room_number: string | null;
  schedule: string | null;
  created_date: string;
}

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

export const classApi = createApi({
  reducerPath: 'classApi',
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    /** GET /classes/{class_id} — fetch a single class */
    getClass: builder.query<ClassResponse, number>({
      query: (classId) => `/classes/${classId}`,
    }),

    /** GET /classes — list classes with pagination */
    listClasses: builder.query<PaginatedResponse<ClassResponse>, { page?: number; pageSize?: number; search?: string }>({
      query: ({ page = 1, pageSize = 10, search }) => ({
        url: '/classes',
        params: { page, page_size: pageSize, search },
      }),
    }),
  }),
});

export const { useGetClassQuery, useListClassesQuery } = classApi;
