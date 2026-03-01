/**
 * Parents Management Screen
 *
 * Page (Atomic Design):
 * - Uses ScreenTemplate for consistent layout
 * - Uses PageHeader for navigation
 * - Uses InfoCard molecules for parent cards
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
import { useListParentsQuery } from '@/store/api/parentApi';

export default function ParentsManagementScreen() {
  const router = useRouter();
  const { t } = useLocalization();
  const { data: parentsData, isLoading } = useListParentsQuery({ pageSize: 100 });

  const parents = parentsData?.data || [];

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('dashboard.manageParents')}
          onBack={() => router.back()}
        />
      }>
      {isLoading ? (
        <LoadingState cardCount={4} />
      ) : parents.length > 0 ? (
        parents.map((parent) => (
          <InfoCard
            key={parent.user_id}
            title={`${parent.first_name} ${parent.last_name}`}
            subtitle={parent.email}
          />
        ))
      ) : (
        <EmptyState
          icon="👨‍👩‍👧"
          message="No parents found"
          subtitle="Parents will appear here once registered"
        />
      )}
    </ScreenTemplate>
  );
}
