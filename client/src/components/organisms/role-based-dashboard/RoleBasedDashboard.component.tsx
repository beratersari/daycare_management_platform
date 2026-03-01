/**
 * Organism — RoleBasedDashboard
 *
 * Renders the appropriate dashboard view based on the current user's role.
 * Acts as a router component that selects between Admin, Teacher, Parent, and Student dashboards.
 * Supports loading state with role-appropriate skeleton components.
 *
 * @example
 * ```tsx
 * <RoleBasedDashboard isLoading={isHydrating} />
 * ```
 */
import React from 'react';

import { ParentDashboard, ParentDashboardSkeleton } from '@/components/organisms/parent-dashboard';
import { TeacherDashboard, TeacherDashboardSkeleton } from '@/components/organisms/teacher-dashboard';
import { AdminDashboard, AdminDashboardSkeleton } from '@/components/organisms/admin-dashboard';
import { StudentDashboard, StudentDashboardSkeleton } from '@/components/organisms/student-dashboard';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { RoleBasedDashboardProps } from './RoleBasedDashboard.types';

export function RoleBasedDashboard({ isLoading = false }: RoleBasedDashboardProps) {
  const user = useAppSelector(selectCurrentUser);

  // Show skeleton while loading or if no user yet
  if (isLoading || !user) {
    // Show a default skeleton if we don't know the role yet
    if (!user) {
      return <AdminDashboardSkeleton />;
    }

    // Show role-appropriate skeleton
    switch (user.role) {
      case 'PARENT':
        return <ParentDashboardSkeleton />;
      case 'TEACHER':
        return <TeacherDashboardSkeleton />;
      case 'ADMIN':
      case 'DIRECTOR':
        return <AdminDashboardSkeleton />;
      default:
        return <StudentDashboardSkeleton />;
    }
  }

  switch (user.role) {
    case 'PARENT':
      return <ParentDashboard />;
    case 'TEACHER':
      return <TeacherDashboard />;
    case 'ADMIN':
    case 'DIRECTOR':
      return <AdminDashboard />;
    default:
      return <StudentDashboard />;
  }
}
