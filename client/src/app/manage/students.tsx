/**
 * Students Management Screen
 *
 * Page (Atomic Design):
 * - Uses ScreenTemplate for consistent layout
 * - Uses PageHeader for navigation
 * - Uses InfoCard molecules for student cards
 * - Uses LoadingState and EmptyState for UX consistency
 */
import { useRouter } from 'expo-router';
import React from 'react';

import { AppText } from '@/components/atoms/app-text';
import { PageHeader } from '@/components/molecules/page-header';
import { InfoCard } from '@/components/molecules/info-card';
import { LoadingState } from '@/components/molecules/loading-state';
import { EmptyState } from '@/components/molecules/empty-state';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useListStudentsQuery } from '@/store/api/studentApi';

export default function StudentsManagementScreen() {
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const { data: studentsData, isLoading } = useListStudentsQuery({ pageSize: 100 });

  const students = studentsData?.data || [];

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('dashboard.manageStudents')}
          onBack={() => router.back()}
        />
      }>
      {isLoading ? (
        <LoadingState cardCount={4} />
      ) : students.length > 0 ? (
        students.map((student) => (
          <InfoCard
            key={student.student_id}
            title={`${student.first_name} ${student.last_name}`}
            subtitle={student.date_of_birth ? `${t('student.dateOfBirth')}: ${student.date_of_birth}` : undefined}
            onPress={() => router.push(`/student/${student.student_id}`)}
          />
        ))
      ) : (
        <EmptyState
          icon="👶"
          message="No students found"
          subtitle="Students will appear here once added"
        />
      )}
    </ScreenTemplate>
  );
}
