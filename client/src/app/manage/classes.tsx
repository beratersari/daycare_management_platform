/**
 * Classes Management Screen
 *
 * Page (Atomic Design):
 * - Uses ScreenTemplate for consistent layout
 * - Uses PageHeader for navigation
 * - Uses InfoCard molecules for class cards
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
import { useListClassesQuery } from '@/store/api/classApi';

export default function ClassesManagementScreen() {
  const router = useRouter();
  const { t } = useLocalization();
  const { data: classesData, isLoading } = useListClassesQuery({ pageSize: 100 });
  const classes = classesData?.data || [];

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('dashboard.manageClasses')}
          onBack={() => router.back()}
        />
      }>
      {isLoading ? (
        <LoadingState cardCount={3} />
      ) : classes.length > 0 ? (
        classes.map((cls) => (
          <InfoCard
            key={cls.class_id}
            title={cls.class_name}
            subtitle={`${t('class.room')}: ${cls.room_number || 'N/A'}`}
          />
        ))
      ) : (
        <EmptyState
          icon="🏫"
          message="No classes found"
          subtitle="Classes will appear here once created"
        />
      )}
    </ScreenTemplate>
  );
}
