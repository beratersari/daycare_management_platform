/**
 * Teachers Management Screen
 *
 * Page (Atomic Design):
 * - Uses ScreenTemplate for consistent layout
 * - Uses PageHeader for navigation
 * - Uses InfoCard molecules for teacher cards
 * - Uses LoadingState and EmptyState for UX consistency
 */
import { useRouter } from 'expo-router';
import React from 'react';

import { PageHeader } from '@/components/molecules/page-header';
import { InfoCard } from '@/components/molecules/info-card';
import { LoadingState } from '@/components/molecules/loading-state';
import { EmptyState } from '@/components/molecules/empty-state';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useLocalization } from '@/hooks/use-localization';
import { useListTeachersQuery } from '@/store/api/teacherApi';

export default function TeachersManagementScreen() {
  const router = useRouter();
  const { t } = useLocalization();
  const { data: teachersData, isLoading } = useListTeachersQuery({ pageSize: 100 });

  const teachers = teachersData?.data || [];

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('dashboard.manageTeachers')}
          onBack={() => router.back()}
        />
      }>
      {isLoading ? (
        <LoadingState cardCount={4} />
      ) : teachers.length > 0 ? (
        teachers.map((teacher) => (
          <InfoCard
            key={teacher.user_id}
            title={`${teacher.first_name} ${teacher.last_name}`}
            subtitle={teacher.email}
          />
        ))
      ) : (
        <EmptyState
          icon="👩‍🏫"
          message="No teachers found"
          subtitle="Teachers will appear here once added"
        />
      )}
    </ScreenTemplate>
  );
}
