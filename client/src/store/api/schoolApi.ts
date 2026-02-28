/**
 * RTK Query API slice for School endpoints.
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithReauth } from './baseQuery';

export interface SchoolResponse {
  school_id: number;
  school_name: string;
  address: string;
  phone?: string;
  email?: string;
  director_name?: string;
  license_number?: string;
  capacity?: number;
  active_term_id?: number;
  created_date: string;
  is_deleted: number;
}

export const schoolApi = createApi({
  reducerPath: 'schoolApi',
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    /** GET /schools — list schools */
    listSchools: builder.query<SchoolResponse[], string | void>({
      query: (search) => ({
        url: '/schools',
        params: { search },
      }),
    }),
    /** GET /schools/{id} — get school by ID */
    getSchool: builder.query<SchoolResponse, number>({
      query: (id) => `/schools/${id}`,
    }),
  }),
});

export const { useListSchoolsQuery, useGetSchoolQuery } = schoolApi;
