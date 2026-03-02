/**
 * RTK Query API slice for Term endpoints.
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithReauth } from './baseQuery';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface TermResponse {
  term_id: number;
  school_id: number;
  term_name: string;
  start_date: string;
  end_date: string | null;
  activity_status: boolean;
  term_img_url: string | null;
  created_date: string;
}

export interface TermCreateRequest {
  school_id: number;
  term_name: string;
  start_date: string;
  end_date?: string | null;
  activity_status?: boolean;
  term_img_url?: string | null;
}

export interface TermUpdateRequest {
  term_name?: string;
  start_date?: string;
  end_date?: string | null;
  activity_status?: boolean;
  term_img_url?: string | null;
}

export interface TermClassResponse {
  class_id: number;
  class_name: string;
  school_id: number;
  capacity?: number | null;
  room_number?: string | null;
  schedule?: string | null;
  created_date?: string;
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

export const termApi = createApi({
  reducerPath: 'termApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Terms', 'TermClasses'],
  endpoints: (builder) => ({
    /** GET /terms — list all terms */
    listTerms: builder.query<TermResponse[], void>({
      query: () => '/terms',
      providesTags: ['Terms'],
    }),

    /** GET /terms/{term_id} — get term by ID */
    getTerm: builder.query<TermResponse, number>({
      query: (termId) => `/terms/${termId}`,
      providesTags: (result, error, termId) => [{ type: 'Terms', id: termId }],
    }),

    /** GET /terms/school/{school_id} — get terms by school */
    getTermsBySchool: builder.query<TermResponse[], number>({
      query: (schoolId) => `/terms/school/${schoolId}`,
      providesTags: ['Terms'],
    }),

    /** GET /terms/school/{school_id}/active — get active term */
    getActiveTermBySchool: builder.query<TermResponse, number>({
      query: (schoolId) => `/terms/school/${schoolId}/active`,
      providesTags: ['Terms'],
    }),

    /** GET /terms/class/{class_id}/terms — get terms by class */
    getTermsByClass: builder.query<TermResponse[], number>({
      query: (classId) => `/terms/class/${classId}/terms`,
      providesTags: ['Terms'],
    }),

    /** GET /terms/{term_id}/classes — get classes assigned to term */
    getClassesByTerm: builder.query<TermClassResponse[], number>({
      query: (termId) => `/terms/${termId}/classes`,
      providesTags: (result, error, termId) => [{ type: 'TermClasses', id: termId }],
    }),

    /** POST /terms — create a term (ADMIN/DIRECTOR only) */
    createTerm: builder.mutation<TermResponse, TermCreateRequest>({
      query: (data) => ({
        url: '/terms',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Terms'],
    }),

    /** PUT /terms/{term_id} — update a term (ADMIN/DIRECTOR only) */
    updateTerm: builder.mutation<TermResponse, { termId: number; data: TermUpdateRequest }>({
      query: ({ termId, data }) => ({
        url: `/terms/${termId}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { termId }) => [{ type: 'Terms', id: termId }, 'Terms'],
    }),

    /** DELETE /terms/{term_id} — soft delete a term (ADMIN/DIRECTOR only) */
    deleteTerm: builder.mutation<void, number>({
      query: (termId) => ({
        url: `/terms/${termId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Terms'],
    }),

    /** POST /terms/{term_id}/classes/{class_id} — assign class to term */
    assignClassToTerm: builder.mutation<void, { termId: number; classId: number }>({
      query: ({ termId, classId }) => ({
        url: `/terms/${termId}/classes/${classId}`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, { termId }) => [{ type: 'TermClasses', id: termId }, 'Terms'],
    }),

    /** DELETE /terms/{term_id}/classes/{class_id} — unassign class from term */
    unassignClassFromTerm: builder.mutation<void, { termId: number; classId: number }>({
      query: ({ termId, classId }) => ({
        url: `/terms/${termId}/classes/${classId}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { termId }) => [{ type: 'TermClasses', id: termId }, 'Terms'],
    }),
  }),
});

export const {
  useListTermsQuery,
  useGetTermQuery,
  useGetTermsBySchoolQuery,
  useGetActiveTermBySchoolQuery,
  useGetTermsByClassQuery,
  useGetClassesByTermQuery,
  useCreateTermMutation,
  useUpdateTermMutation,
  useDeleteTermMutation,
  useAssignClassToTermMutation,
  useUnassignClassFromTermMutation,
} = termApi;
