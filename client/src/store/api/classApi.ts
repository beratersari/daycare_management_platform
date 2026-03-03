/**
 * RTK Query API slice for Class endpoints.
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithReauth } from './baseQuery';
import type { StudentResponse } from './studentApi';
import type { UserResponse } from './authApi';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ClassResponse {
  class_id: number;
  school_id: number;
  class_name: string;
  capacity: number;
  created_date: string;
  students: StudentResponse[];
  teachers: UserResponse[];
}

export interface ClassCreateRequest {
  class_name: string;
  school_id: number;
  capacity: number;
}

export interface ClassUpdateRequest {
  class_name?: string;
  school_id?: number;
  capacity?: number;
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

export interface ClassEventResponse {
  event_id: number;
  class_id: number;
  class_name: string;
  title: string;
  description: string | null;
  photo_url: string | null;
  event_date: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface ClassEventCreateRequest {
  title: string;
  description?: string;
  photo_url?: string;
  event_date: string;
}

export interface ClassEventUpdateRequest {
  title?: string;
  description?: string;
  photo_url?: string;
  event_date?: string;
}

// Assignment Types
export interface StudentAssignmentRequest {
  student_id: number;
  term_id?: number;
}

export interface StudentAssignmentResponse {
  student_id: number;
  class_id: number;
  term_id: number | null;
  student_name: string | null;
  class_name: string | null;
  term_name: string | null;
}

export interface TeacherAssignmentRequest {
  teacher_id: number;
  term_id?: number;
}

export interface TeacherAssignmentResponse {
  teacher_id: number;
  class_id: number;
  term_id: number | null;
  teacher_name: string | null;
  class_name: string | null;
  term_name: string | null;
}

export interface ClassAssignmentsResponse {
  class_id: number;
  class_name: string;
  term_id: number | null;
  term_name: string | null;
  students: StudentAssignmentResponse[];
  teachers: TeacherAssignmentResponse[];
  capacity: number | null;
  current_student_count: number;
  available_spots: number | null;
}

export interface BulkStudentAssignmentRequest {
  student_ids: number[];
  term_id?: number;
}

export interface BulkTeacherAssignmentRequest {
  teacher_ids: number[];
  term_id?: number;
}

export interface BulkAssignmentResponse {
  class_id: number;
  term_id: number | null;
  assigned: number[];
  already_assigned: number[];
  failed: { id: number; reason: string }[];
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

export const classApi = createApi({
  reducerPath: 'classApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Classes'],
  endpoints: (builder) => ({
    /** GET /classes/{class_id} — fetch a single class */
    getClass: builder.query<ClassResponse, number>({
      query: (classId) => `/classes/${classId}`,
      providesTags: ['Classes'],
    }),

    /** GET /classes — list classes with pagination */
    listClasses: builder.query<PaginatedResponse<ClassResponse>, { page?: number; pageSize?: number; search?: string }>({
      query: ({ page = 1, pageSize = 10, search }) => ({
        url: '/classes',
        params: { page, page_size: pageSize, search },
      }),
      providesTags: ['Classes'],
    }),

    /** POST /classes — create a class */
    createClass: builder.mutation<ClassResponse, ClassCreateRequest>({
      query: (data) => ({
        url: '/classes',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Classes'],
    }),

    /** PUT /classes/{class_id} — update a class */
    updateClass: builder.mutation<ClassResponse, { classId: number; data: ClassUpdateRequest }>({
      query: ({ classId, data }) => ({
        url: `/classes/${classId}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Classes'],
    }),

    /** DELETE /classes/{class_id} — delete a class */
    deleteClass: builder.mutation<void, number>({
      query: (classId) => ({
        url: `/classes/${classId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Classes'],
    }),

    /** GET /classes/my-events — get events for current user */
    getMyEvents: builder.query<ClassEventResponse[], void>({
      query: () => '/classes/my-events',
    }),

    /** GET /classes/{class_id}/events — get events for a specific class */
    getClassEvents: builder.query<ClassEventResponse[], number>({
      query: (classId) => `/classes/${classId}/events`,
    }),

    /** POST /classes/{class_id}/events — create an event for a class */
    createClassEvent: builder.mutation<ClassEventResponse, { classId: number; data: ClassEventCreateRequest }>({
      query: ({ classId, data }) => ({
        url: `/classes/${classId}/events`,
        method: 'POST',
        body: data,
      }),
    }),

    /** PUT /classes/{class_id}/events/{event_id} — update an event */
    updateClassEvent: builder.mutation<ClassEventResponse, { classId: number; eventId: number; data: ClassEventUpdateRequest }>({
      query: ({ classId, eventId, data }) => ({
        url: `/classes/${classId}/events/${eventId}`,
        method: 'PUT',
        body: data,
      }),
    }),

    /** DELETE /classes/{class_id}/events/{event_id} — delete an event */
    deleteClassEvent: builder.mutation<void, { classId: number; eventId: number }>({
      query: ({ classId, eventId }) => ({
        url: `/classes/${classId}/events/${eventId}`,
        method: 'DELETE',
      }),
    }),

    // --- Assignment Endpoints ---

    /** GET /classes/{class_id}/assignments — get all assignments for a class */
    getClassAssignments: builder.query<ClassAssignmentsResponse, { classId: number; termId?: number }>({
      query: ({ classId, termId }) => ({
        url: `/classes/${classId}/assignments`,
        params: termId ? { term_id: termId } : undefined,
      }),
      providesTags: ['Classes'],
    }),

    /** POST /classes/{class_id}/students — assign a student to a class */
    assignStudentToClass: builder.mutation<StudentAssignmentResponse, { classId: number; data: StudentAssignmentRequest }>({
      query: ({ classId, data }) => ({
        url: `/classes/${classId}/students`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Classes'],
    }),

    /** POST /classes/{class_id}/students/bulk — bulk assign students to a class */
    bulkAssignStudentsToClass: builder.mutation<BulkAssignmentResponse, { classId: number; data: BulkStudentAssignmentRequest }>({
      query: ({ classId, data }) => ({
        url: `/classes/${classId}/students/bulk`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Classes'],
    }),

    /** DELETE /classes/{class_id}/students/{student_id} — unassign a student from a class */
    unassignStudentFromClass: builder.mutation<void, { classId: number; studentId: number; termId?: number }>({
      query: ({ classId, studentId, termId }) => ({
        url: `/classes/${classId}/students/${studentId}`,
        method: 'DELETE',
        params: termId ? { term_id: termId } : undefined,
      }),
      invalidatesTags: ['Classes'],
    }),

    /** POST /classes/{class_id}/teachers — assign a teacher to a class */
    assignTeacherToClass: builder.mutation<TeacherAssignmentResponse, { classId: number; data: TeacherAssignmentRequest }>({
      query: ({ classId, data }) => ({
        url: `/classes/${classId}/teachers`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Classes'],
    }),

    /** POST /classes/{class_id}/teachers/bulk — bulk assign teachers to a class */
    bulkAssignTeachersToClass: builder.mutation<BulkAssignmentResponse, { classId: number; data: BulkTeacherAssignmentRequest }>({
      query: ({ classId, data }) => ({
        url: `/classes/${classId}/teachers/bulk`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Classes'],
    }),

    /** DELETE /classes/{class_id}/teachers/{teacher_id} — unassign a teacher from a class */
    unassignTeacherFromClass: builder.mutation<void, { classId: number; teacherId: number; termId?: number }>({
      query: ({ classId, teacherId, termId }) => ({
        url: `/classes/${classId}/teachers/${teacherId}`,
        method: 'DELETE',
        params: termId ? { term_id: termId } : undefined,
      }),
      invalidatesTags: ['Classes'],
    }),
  }),
});

export const { 
  useGetClassQuery, 
  useListClassesQuery,
  useCreateClassMutation,
  useUpdateClassMutation,
  useDeleteClassMutation,
  useGetMyEventsQuery,
  useGetClassEventsQuery,
  useCreateClassEventMutation,
  useUpdateClassEventMutation,
  useDeleteClassEventMutation,
  // Assignment hooks
  useGetClassAssignmentsQuery,
  useAssignStudentToClassMutation,
  useBulkAssignStudentsToClassMutation,
  useUnassignStudentFromClassMutation,
  useAssignTeacherToClassMutation,
  useBulkAssignTeachersToClassMutation,
  useUnassignTeacherFromClassMutation,
} = classApi;
