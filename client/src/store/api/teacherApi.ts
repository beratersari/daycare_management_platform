/**
 * RTK Query API slice for Teacher endpoints.
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithReauth } from './baseQuery';
import type { UserResponse } from './authApi';
import type { ClassResponse } from './classApi';
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

export const teacherApi = createApi({
  reducerPath: 'teacherApi',
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    /** GET /teachers — list teachers with pagination */
    listTeachers: builder.query<PaginatedResponse<UserResponse>, { page?: number; pageSize?: number; search?: string }>({
      query: ({ page = 1, pageSize = 10, search }) => ({
        url: '/teachers',
        params: { page, page_size: pageSize, search },
      }),
    }),

    /** GET /teachers/{teacher_id}/classes — get teacher's classes */
    getTeacherClasses: builder.query<ClassResponse[], number>({
      query: (teacherId) => `/teachers/${teacherId}/classes`,
    }),

    /** GET /teachers/me/students — get students in current teacher's classes */
    getMyStudents: builder.query<StudentResponse[], void>({
      query: () => '/teachers/me/students',
    }),
  }),
});

export const { useListTeachersQuery, useGetTeacherClassesQuery, useGetMyStudentsQuery } = teacherApi;
