/**
 * RTK Query API slice for Student endpoints.
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithReauth } from './baseQuery';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AllergyResponse {
  allergy_id: number;
  student_id: number;
  allergy_name: string;
  severity: string | null;
  notes: string | null;
  created_date: string;
}

export interface HWInfoResponse {
  hw_id: number;
  student_id: number;
  height: number;
  weight: number;
  measurement_date: string;
  created_date: string;
}

export interface StudentResponse {
  student_id: number;
  school_id: number;
  first_name: string;
  last_name: string;
  class_ids: number[];
  student_photo: string | null;
  date_of_birth: string | null;
  created_date: string;
  parents: number[];
  student_allergies: AllergyResponse[];
  student_hw_info: HWInfoResponse[];
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

export const studentApi = createApi({
  reducerPath: 'studentApi',
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    /** GET /students/{student_id} — fetch a single student */
    getStudent: builder.query<StudentResponse, number>({
      query: (studentId) => `/students/${studentId}`,
    }),

    /** GET /students — list students with pagination */
    listStudents: builder.query<PaginatedResponse<StudentResponse>, { page?: number; pageSize?: number; search?: string }>({
      query: ({ page = 1, pageSize = 10, search }) => ({
        url: '/students',
        params: { page, page_size: pageSize, search },
      }),
    }),
  }),
});

export const { useGetStudentQuery, useListStudentsQuery } = studentApi;
