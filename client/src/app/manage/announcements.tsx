/**
 * Announcements Screen
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

export default function AnnouncementsScreen() {
  const router = useRouter();
  const { t } = useLocalization();

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('dashboard.announcements')}
          onBack={() => router.back()}
        />
      }>
      <EmptyState
        icon="📢"
        message="Announcements coming soon"
        subtitle="Important updates will be posted here"
      />
    </ScreenTemplate>
  );
}
