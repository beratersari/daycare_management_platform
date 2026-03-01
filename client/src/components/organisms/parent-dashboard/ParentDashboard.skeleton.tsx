/**
 * ParentDashboardSkeleton
 * Loading skeleton for the ParentDashboard component.
 */
import React from 'react';
import { View } from 'react-native';

import { Skeleton } from '@/components/atoms/skeleton';
import { styles } from './ParentDashboard.styles';

/** Skeleton dimensions */
const SECTION_LABEL_WIDTH = 120;
const BUTTON_HEIGHT = 72;
const CARD_BORDER_RADIUS = 16;
const CHILD_CARD_HEIGHT = 120;
const QUICK_ACTIONS_HEIGHT = 150;

interface ParentDashboardSkeletonProps {
  /** Whether to show the quick actions section. Defaults to true */
  showQuickActions?: boolean;
  /** Number of child cards to show. Defaults to 2 */
  childCount?: number;
}

export function ParentDashboardSkeleton({
  showQuickActions = true,
  childCount = 2,
}: ParentDashboardSkeletonProps) {
  return (
    <View style={styles.container}>
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

      <Skeleton width={SECTION_LABEL_WIDTH * 1.5} height={16} style={{ marginBottom: 8 }} />

      {Array.from({ length: childCount }).map((_, index) => (
        <Skeleton
          key={`child-${index}`}
          width="100%"
          height={CHILD_CARD_HEIGHT}
          borderRadius={CARD_BORDER_RADIUS}
          style={{ marginBottom: 12 }}
        />
      ))}
    </View>
  );
}