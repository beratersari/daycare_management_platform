/**
 * Organism — RoleBasedDashboard
 * Renders the appropriate dashboard view based on user role.
 */
import React from 'react';

import { ParentDashboard } from '@/components/organisms/ParentDashboard';
import { TeacherDashboard } from '@/components/organisms/TeacherDashboard';
import { AdminDashboard } from '@/components/organisms/AdminDashboard';
import { StudentDashboard } from '@/components/organisms/StudentDashboard';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import type { UserRole } from '@/store/api/authApi';

export function RoleBasedDashboard() {
  const user = useAppSelector(selectCurrentUser);

  if (!user) {
    return null;
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
      // Fallback for unknown roles - treat as student-like view
      return <StudentDashboard />;
  }
}
