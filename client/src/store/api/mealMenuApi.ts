/**
 * RTK Query API slice for Meal Menu endpoints.
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithReauth } from './baseQuery';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface MealMenuResponse {
  menu_id: number;
  school_id: number;
  class_id: number | null;
  menu_date: string;
  breakfast: string | null;
  lunch: string | null;
  dinner: string | null;
  created_by: number | null;
  created_date: string;
  is_deleted: number;
}

export interface MealMenuCreate {
  school_id: number;
  class_id?: number | null;
  menu_date: string;
  breakfast?: string | null;
  lunch?: string | null;
  dinner?: string | null;
}

export interface MealMenuUpdate {
  class_id?: number | null;
  menu_date?: string;
  breakfast?: string | null;
  lunch?: string | null;
  dinner?: string | null;
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

export const mealMenuApi = createApi({
  reducerPath: 'mealMenuApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['MealMenu'],
  endpoints: (builder) => ({
    /** GET /meals — list all meal menus */
    listMealMenus: builder.query<MealMenuResponse[], void>({
      query: () => '/meals',
      providesTags: ['MealMenu'],
    }),

    /** GET /meals/{menu_id} — get a single meal menu */
    getMealMenu: builder.query<MealMenuResponse, number>({
      query: (menuId) => `/meals/${menuId}`,
      providesTags: (result, error, id) => [{ type: 'MealMenu', id }],
    }),

    /** GET /meals/school/{school_id} — get meal menus for a school */
    getMealMenusBySchool: builder.query<MealMenuResponse[], number>({
      query: (schoolId) => `/meals/school/${schoolId}`,
      providesTags: ['MealMenu'],
    }),

    /** GET /meals/school/{school_id}/date/{menu_date} — get meal menus for school and date */
    getMealMenusBySchoolAndDate: builder.query<MealMenuResponse[], { schoolId: number; date: string }>({
      query: ({ schoolId, date }) => `/meals/school/${schoolId}/date/${date}`,
      providesTags: ['MealMenu'],
    }),

    /** GET /meals/class/{class_id} — get meal menus for a class */
    getMealMenusByClass: builder.query<MealMenuResponse[], number>({
      query: (classId) => `/meals/class/${classId}`,
      providesTags: ['MealMenu'],
    }),

    /** GET /meals/class/{class_id}/date/{menu_date} — get meal menus for class and date */
    getMealMenusByClassAndDate: builder.query<MealMenuResponse[], { classId: number; date: string }>({
      query: ({ classId, date }) => `/meals/class/${classId}/date/${date}`,
      providesTags: ['MealMenu'],
    }),

    /** POST /meals — create a new meal menu (ADMIN, DIRECTOR, TEACHER only) */
    createMealMenu: builder.mutation<MealMenuResponse, MealMenuCreate>({
      query: (data) => ({
        url: '/meals',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['MealMenu'],
    }),

    /** PUT /meals/{menu_id} — update a meal menu (ADMIN, DIRECTOR, TEACHER only) */
    updateMealMenu: builder.mutation<MealMenuResponse, { menuId: number; data: MealMenuUpdate }>({
      query: ({ menuId, data }) => ({
        url: `/meals/${menuId}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { menuId }) => [{ type: 'MealMenu', id: menuId }, 'MealMenu'],
    }),

    /** DELETE /meals/{menu_id} — delete a meal menu (ADMIN, DIRECTOR, TEACHER only) */
    deleteMealMenu: builder.mutation<void, number>({
      query: (menuId) => ({
        url: `/meals/${menuId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['MealMenu'],
    }),
  }),
});

export const {
  useListMealMenusQuery,
  useGetMealMenuQuery,
  useGetMealMenusBySchoolQuery,
  useGetMealMenusBySchoolAndDateQuery,
  useGetMealMenusByClassQuery,
  useGetMealMenusByClassAndDateQuery,
  useCreateMealMenuMutation,
  useUpdateMealMenuMutation,
  useDeleteMealMenuMutation,
} = mealMenuApi;
