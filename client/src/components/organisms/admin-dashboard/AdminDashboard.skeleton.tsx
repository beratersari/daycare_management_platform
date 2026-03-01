/**
 * AdminDashboardSkeleton
 * Loading skeleton for the AdminDashboard component.
 */
import React from 'react';
import { View } from 'react-native';

import { Skeleton } from '@/components/atoms/skeleton';
import { styles } from './AdminDashboard.styles';

/** Skeleton dimensions */
const SECTION_LABEL_WIDTH = 120;
const BUTTON_HEIGHT = 72;
const CARD_BORDER_RADIUS = 16;
const STAT_CARD_HEIGHT = 80;

interface AdminDashboardSkeletonProps {
  /** Whether to show the management tools section. Defaults to true */
  showManagementTools?: boolean;
  /** Whether to show the quick actions section. Defaults to true */
  showQuickActions?: boolean;
  /** Whether to show the stats section. Defaults to true */
  showStats?: boolean;
}

export function AdminDashboardSkeleton({
  showManagementTools = true,
  showQuickActions = true,
  showStats = true,
}: AdminDashboardSkeletonProps) {
  return (
    <View style={styles.container}>
      {showManagementTools && (
        <View style={styles.section}>
          <Skeleton width={SECTION_LABEL_WIDTH} height={16} style={{ marginBottom: 8 }} />
          <View style={styles.buttonGrid}>
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
          </View>
        </View>
      )}

      {showQuickActions && (
        <View style={styles.section}>
          <Skeleton width={SECTION_LABEL_WIDTH} height={16} style={{ marginBottom: 8 }} />
          <View style={styles.buttonRow}>
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
          </View>
          <View style={styles.buttonRow}>
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
          </View>
        </View>
      )}

      {showStats && (
        <View style={styles.section}>
          <Skeleton width={SECTION_LABEL_WIDTH} height={16} style={{ marginBottom: 8 }} />
          <View style={styles.statsRow}>
            <Skeleton width="48%" height={STAT_CARD_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={STAT_CARD_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
          </View>
          <View style={styles.statsRow}>
            <Skeleton width="48%" height={STAT_CARD_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={STAT_CARD_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
          </View>
        </View>
      )}
    </View>
  );
}