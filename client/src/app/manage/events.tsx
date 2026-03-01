/**
 * Events Screen
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

export default function EventsScreen() {
  const router = useRouter();
  const { t } = useLocalization();

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('dashboard.events')}
          onBack={() => router.back()}
        />
      }>
      <EmptyState
        icon="🎉"
        message="Events coming soon"
        subtitle="Stay tuned for upcoming events and activities"
      />
    </ScreenTemplate>
  );
}
