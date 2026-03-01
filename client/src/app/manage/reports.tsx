/**
 * Reports Screen
 *
 * Page (Atomic Design):
 * - Uses ScreenTemplate for consistent layout
 * - Uses PageHeader for navigation
 * - Uses EmptyState for placeholder content
 */
import { useRouter } from 'expo-router';
import React from 'react';

import { PageHeader } from '@/components/molecules/page-header';
import { EmptyState } from '@/components/molecules/empty-state';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useLocalization } from '@/hooks/use-localization';

export default function ReportsScreen() {
  const router = useRouter();
  const { t } = useLocalization();

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('dashboard.reports')}
          onBack={() => router.back()}
        />
      }>
      <EmptyState
        icon="📊"
        message="Reports coming soon"
        subtitle="Detailed reports and analytics will be available here"
      />
    </ScreenTemplate>
  );
}
